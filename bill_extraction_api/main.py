from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .models import BillExtractionResponse
from .extractor import process_document
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Bill Extraction API", description="API to extract line items from bills using Vision LLM")

class ExtractRequest(BaseModel):
    document: str

@app.post("/extract-bill-data", response_model=BillExtractionResponse)
async def extract_bill_data(request: ExtractRequest):
    """
    Extracts bill line items from a document URL.
    """
    if not request.document:
        raise HTTPException(status_code=400, detail="Document URL is required")

    result = process_document(request.document)
    
    if not result.is_success:
        # We return 200 even on failure as per the Postman collection example for 500 error, 
        # but the schema implies we might want to return 500 status code for internal errors.
        # However, the example shows a 500 status code in the response meta, but the body has is_success: false.
        # Let's stick to returning the object. If it's a server error, we might want to set status_code.
        # The Postman example "500 Internal Server Error" has status 500.
        # So let's return 500 if it failed due to exception.
        # But wait, the prompt says "If Status code 200 and following valid schema, then true".
        # So if is_success is false, we probably should return a non-200 code or just return the object with false.
        # Let's return the object. If message indicates error, we can set status code if needed, 
        # but FastAPI response_model will handle the body.
        # To match Postman exactly, let's just return the result. 
        # If we want to force a 500 status code, we can do that.
        pass

    return result

@app.get("/")
def read_root():
    return {"message": "Bill Extraction API is running. Use POST /extract-bill-data to extract data."}
