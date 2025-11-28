import requests
import json
import time

def test_api():
    url = "http://localhost:8000/extract-bill-data"
    # Use one of the sample URLs from the Postman collection or training data
    # This URL is from the Postman collection sample
    payload = {
        "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
    }
    
    print("Sending request to API...")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            data = response.json()
            if data.get("is_success"):
                print("SUCCESS: API returned success.")
            else:
                print("FAILURE: API returned is_success=False.")
        else:
            print("FAILURE: API returned non-200 status code.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Wait a bit for server to start
    time.sleep(2)
    test_api()
