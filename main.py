from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from schemas import ExtractRequest, ExtractBillDataResponse
from extractor import extract_data
import os

app = FastAPI()

@app.post("/extract-bill-data", response_model=ExtractBillDataResponse)
async def extract_bill_data(request: ExtractRequest):
    try:
        if not os.getenv("GEMINI_API_KEY"):
             return ExtractBillDataResponse(
                is_success=False,
                error="GEMINI_API_KEY not found in environment variables."
            )

        data = extract_data(request.document)
        return ExtractBillDataResponse(
            is_success=True,
            data=data
        )
    except Exception as e:
        return ExtractBillDataResponse(
            is_success=False,
            error=str(e)
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
