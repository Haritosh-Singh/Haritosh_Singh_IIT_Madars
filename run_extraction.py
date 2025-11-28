import os
import json
from extractor import extract_data
from schemas import ExtractBillDataData

# Set the URL provided by the user
url = "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_1.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A21%3A03Z&se=2026-11-25T14%3A21%3A00Z&sr=b&sp=r&sig=2szJobwLVzcVSmg5IPWjRT9k7pHq2Tvifd6seRa2xRI%3D"

def main():
    try:
        print(f"Extracting data from: {url}")
        result = extract_data(url)
        
        # Convert Pydantic model to dict and then to JSON
        # Assuming result is an instance of ExtractBillDataData which is a Pydantic model
        if hasattr(result, 'model_dump'):
            data_dict = result.model_dump()
        elif hasattr(result, 'dict'):
            data_dict = result.dict()
        else:
            data_dict = result # Fallback if it's already a dict or something else

        # Wrap in the requested structure
        final_output = {
            "is_success": True,
            "data": data_dict
        }

        print(json.dumps(final_output, indent=4))
        
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    main()
