# api/schemas.py
from typing import Optional
from pydantic import BaseModel

class DocumentChunk(BaseModel):
    id: Optional[str] = None
    document_id: Optional[str] = None
    page_content: str
    metadata: dict = {}