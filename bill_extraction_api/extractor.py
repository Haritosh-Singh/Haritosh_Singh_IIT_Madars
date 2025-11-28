import os
import tempfile
import requests
import google.generativeai as genai
from pdf2image import convert_from_path
from dotenv import load_dotenv
from .models import BillExtractionResponse, BillData, PageLineItems, BillItem, TokenUsage
import json
import typing

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def download_file(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()
    
    # Determine file extension or default to .pdf
    # This is a simplification; in production, we'd check Content-Type
    filename = url.split("?")[0].split("/")[-1]
    if not filename:
        filename = "document.pdf"
        
    # Create a temp file
    fd, path = tempfile.mkstemp(suffix=f"_{filename}")
    with os.fdopen(fd, 'wb') as tmp:
        tmp.write(response.content)
    return path

def extract_data_from_image(image_path: str, page_num: int) -> dict:
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    You are an expert data extraction agent. Extract the following information from the bill/invoice image:
    1. Page Type: "Bill Detail", "Final Bill", or "Pharmacy".
    2. Line Items: For each item, extract:
        - Item Name (exactly as mentioned)
        - Item Amount (net amount post discounts)
        - Item Rate (rate per unit)
        - Item Quantity
    
    Return the output in valid JSON format matching this structure:
    {
        "page_no": "string",
        "page_type": "string",
        "bill_items": [
            {
                "item_name": "string",
                "item_amount": float,
                "item_rate": float,
                "item_quantity": float
            }
        ]
    }
    If a value is missing, use 0 for numbers and "" for strings.
    Do not include markdown formatting like ```json ... ```. Just return the raw JSON string.
    """
    
    # Upload the file to Gemini
    myfile = genai.upload_file(image_path)
    
    result = model.generate_content([prompt, myfile])
    
    # Clean up the response text
    response_text = result.text.strip()
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]
        
    try:
        data = json.loads(response_text)
        data["page_no"] = str(page_num)
        
        # Extract token usage if available (Gemini Python SDK might not expose it easily in all versions, 
        # but we can try to get it from result.usage_metadata)
        usage = result.usage_metadata
        token_usage = {
            "total_tokens": usage.total_token_count,
            "input_tokens": usage.prompt_token_count,
            "output_tokens": usage.candidates_token_count
        }
        return data, token_usage
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for page {page_num}: {response_text}")
        return None, None

def process_document(url: str) -> BillExtractionResponse:
    try:
        file_path = download_file(url)
    except Exception as e:
        return BillExtractionResponse(is_success=False, message=f"Failed to download document: {str(e)}")

    try:
        # Check if it's a PDF or Image
        if file_path.lower().endswith('.pdf'):
            images = convert_from_path(file_path)
        else:
            # Assume it's an image
            # We need to handle image files differently if we want to use convert_from_path logic, 
            # but for now let's assume we just treat it as a single page image
            # Ideally we should convert it to a format Gemini accepts or just pass the path
            # Since convert_from_path returns PIL images, we might want to save them to temp files for upload_file
            # Or use PIL image directly if Gemini supports it (it does)
            import PIL.Image
            images = [PIL.Image.open(file_path)]

        all_page_items = []
        total_tokens = 0
        input_tokens = 0
        output_tokens = 0
        
        temp_image_paths = []

        for i, image in enumerate(images):
            # Save image to temp file for upload
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            
            fd, img_path = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            image.save(img_path, "JPEG")
            temp_image_paths.append(img_path)
            
            page_data, usage = extract_data_from_image(img_path, i + 1)
            
            if page_data:
                # Validate and convert to Pydantic models
                items = []
                for item in page_data.get("bill_items", []):
                    items.append(BillItem(
                        item_name=item.get("item_name", ""),
                        item_amount=float(item.get("item_amount", 0)),
                        item_rate=float(item.get("item_rate", 0)),
                        item_quantity=float(item.get("item_quantity", 0))
                    ))
                
                all_page_items.append(PageLineItems(
                    page_no=str(page_data.get("page_no", str(i+1))),
                    page_type=page_data.get("page_type", "Bill Detail"),
                    bill_items=items
                ))
                
                if usage:
                    total_tokens += usage.get("total_tokens", 0)
                    input_tokens += usage.get("input_tokens", 0)
                    output_tokens += usage.get("output_tokens", 0)

        # Cleanup temp files
        os.remove(file_path)
        for p in temp_image_paths:
            os.remove(p)

        # Calculate total item count
        total_item_count = sum(len(p.bill_items) for p in all_page_items)

        return BillExtractionResponse(
            is_success=True,
            token_usage=TokenUsage(
                total_tokens=total_tokens,
                input_tokens=input_tokens,
                output_tokens=output_tokens
            ),
            data=BillData(
                pagewise_line_items=all_page_items,
                total_item_count=total_item_count
            )
        )

    except Exception as e:
        return BillExtractionResponse(is_success=False, message=f"Processing failed: {str(e)}")
