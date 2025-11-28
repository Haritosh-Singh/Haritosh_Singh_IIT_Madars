from pydantic import BaseModel
from typing import List, Optional

class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: float
    item_quantity: float

class PageLineItems(BaseModel):
    page_no: str
    page_type: str = "Bill Detail"
    bill_items: List[BillItem]

class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int

class ExtractBillDataData(BaseModel):
    pagewise_line_items: List[PageLineItems]
    total_item_count: int
    token_usage: TokenUsage

class ExtractBillDataResponse(BaseModel):
    is_success: bool
    data: Optional[ExtractBillDataData] = None
    error: Optional[str] = None

class ExtractRequest(BaseModel):
    document: str
