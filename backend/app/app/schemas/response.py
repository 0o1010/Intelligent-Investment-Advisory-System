from typing import Optional, Any

from pydantic import BaseModel


class Response(BaseModel):
    code: Optional[int] = None
    data: Optional[Any] = None
    message: Optional[str] = None
    total: Optional[int] = None
