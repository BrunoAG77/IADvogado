from pydantic import BaseModel
from typing import Optional

class ProcessRequest(BaseModel):
    process_number: Optional[str] = None
    user_id: Optional[str] = None

class SimplifyResponse(BaseModel):
    what_happened: str
    what_it_means: str
    what_to_do_now: str
    disclaimer: str