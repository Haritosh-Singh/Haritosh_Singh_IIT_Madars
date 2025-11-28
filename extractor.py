import os
import google.generativeai as genai
import requests
from pdf2image import convert_from_bytes
from io import BytesIO
import json
from schemas import ExtractBillDataData, PageLineItems, BillItem, TokenUsage
import typing

# Configure Gemini inside the function to ensure env vars are loaded

def download_file(url: str) -> typing.Tuple[bytes, str]:
    response = requests.get(url)
    response.raise_for_status()
    content_type = response.headers.get('Content-Type', '')
    return response.content, content_type

def process_document(file_content: bytes, mime_type: str) -> list:
    """
    Returns a list of image parts (PIL Images or bytes) for Gemini.
    """
    if 'pdf' in mime_type.lower():
        # Convert PDF to images
        images = convert_from_bytes(file_content)
        return images
    elif 'image' in mime_type.lower():
        # Return as is (Gemini can handle image bytes directly if wrapped correctly, 
        # but usually it's better to pass PIL images or use the file API. 
        # For simplicity with google-generativeai, we can pass the bytes with mime_type)
        return [{"mime_type": mime_type, "data": file_content}]
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")

def extract_data(url: str) -> ExtractBillDataData:
    if "GEMINI_API_KEY" in os.environ:
        genai.configure(api_key=os.environ["GEMINI_API_KEY"])
        
    content, mime_type = download_file(url)
    
    parts = []
    if 'pdf' in mime_type.lower():
        images = convert_from_bytes(content)
        for img in images:
            parts.append(img)
    else:
        parts.append({"mime_type": mime_type, "data": content})

    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = """
    You are an expert invoice extractor. 
    Extract all line items from the provided bill/invoice images.
    
    For each page, provide a list of items.
    Extract:
    - Item name
    - Rate
    - Quantity
    - Final amount per item (after discounts)
    
    Also calculate:
    - total_item_count (how many items across all pages)
    
    Return the data in the following strict JSON format:
    {
        "pagewise_line_items": [
            {
                "page_no": "1",
                "page_type": "Bill Detail", 
                "bill_items": [
                    {
                        "item_name": "string",
                        "item_amount": float,
                        "item_rate": float,
                        "item_quantity": float
                    }
                ]
            }
        ],
        "total_item_count": int
    }
    
    Ensure the total_item_count matches the actual number of items extracted.
    Do not include any markdown formatting (like ```json). Just return the raw JSON string.
    """
    
    response = model.generate_content([prompt, *parts])
    
    # Parse response
    try:
        text = response.text
        # Clean up if model returns markdown
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        data = json.loads(text)
        
        # Calculate token usage (approximate or from response if available)
        # usage_metadata is available in response.usage_metadata
        usage = response.usage_metadata
        token_usage = TokenUsage(
            total_tokens=usage.total_token_count,
            input_tokens=usage.prompt_token_count,
            output_tokens=usage.candidates_token_count
        )
        
        # Validate and convert to Pydantic model
        # We might need to adjust if the model output isn't perfect, but let's try direct mapping first
        result = ExtractBillDataData(
            pagewise_line_items=data['pagewise_line_items'],
            total_item_count=data['total_item_count'],
            token_usage=token_usage
        )
        return result
        
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response: {response.text}")
        raise e
