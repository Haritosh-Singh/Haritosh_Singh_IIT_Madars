# Bill Extraction API

A robust FastAPI application designed to extract structured line-item data from bill and invoice images (or PDFs) using Google's Gemini 2.0 Flash Vision model.

## 🚀 Features

- **Multi-Format Support**: Accepts image URLs (PNG, JPEG, etc.) and PDF documents.
- **AI-Powered Extraction**: Utilizes Google's Gemini 2.0 Flash model for high-accuracy text and data extraction.
- **Structured Output**: Returns clean, structured JSON data including:
  - Item Name
  - Rate
  - Quantity
  - Final Amount
  - Page-wise breakdown
  - Total item count
- **Token Usage Tracking**: Provides details on input and output token usage for cost monitoring.
- **FastAPI Powered**: Built on FastAPI for high performance and easy documentation (Swagger UI).

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+**
- **Poppler Utils** (Required for PDF processing)
  - *Ubuntu/Debian*: `sudo apt-get install poppler-utils`
  - *MacOS*: `brew install poppler`
  - *Windows*: Download and add to PATH.

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

1.  **Get a Google Gemini API Key:**
    - Visit [Google AI Studio](https://aistudio.google.com/) to generate an API key.

2.  **Set up Environment Variables:**
    - Create a `.env` file in the root directory.
    - Add your API key:
      ```env
      GEMINI_API_KEY=your_actual_api_key_here
      ```

## 🏃‍♂️ Usage

### Running the Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn main:app --reload
```

The server will start at `http://0.0.0.0:8000`.

### API Documentation

Once the server is running, you can access the interactive API documentation at:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Extracting Data

**Endpoint:** `POST /extract-bill-data`

**Request Body:**

```json
{
  "document": "https://example.com/path/to/invoice.png"
}
```

**Example Response:**

```json
{
  "is_success": true,
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail",
        "bill_items": [
          {
            "item_name": "Product A",
            "item_amount": 100.0,
            "item_rate": 50.0,
            "item_quantity": 2.0
          }
        ]
      }
    ],
    "total_item_count": 1,
    "token_usage": {
      "total_tokens": 150,
      "input_tokens": 100,
      "output_tokens": 50
    }
  }
}
```

## 📂 Project Structure

```
.
├── main.py                 # FastAPI application entry point
├── extractor.py            # Core logic for Gemini interaction and PDF processing
├── schemas.py              # Pydantic models for request/response validation
├── requirements.txt        # Python dependencies
├── Procfile                # Deployment configuration (e.g., for Render/Heroku)
├── .env                    # Environment variables (not committed)
└── bill_extraction_api/    # (Optional) Package structure
```

## 🧪 Testing

You can test the extraction logic independently using the provided script:

```bash
python run_extraction.py
```
*Note: You may need to update the `url` variable in `run_extraction.py` to test different documents.*
