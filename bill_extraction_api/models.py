from pydantic import BaseModel
from typing import List, Optional, Literal

class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int

class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: float
    item_quantity: float

class PageLineItems(BaseModel):
    page_no: str
    page_type: Literal["Bill Detail", "Final Bill", "Pharmacy"]
    bill_items: List[BillItem]

class BillData(BaseModel):
    pagewise_line_items: List[PageLineItems]
    total_item_count: int

class BillExtractionResponse(BaseModel):
    is_success: bool
    token_usage: Optional[TokenUsage] = None
    data: Optional[BillData] = None
    message: Optional[str] = None
