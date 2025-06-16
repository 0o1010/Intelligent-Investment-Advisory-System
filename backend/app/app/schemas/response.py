# -*- coding: utf-8 -*-
# @Time    : 2023/4/11 16:09
# @Author  : 陈旭燃
# @File    : response.py
# @Description :
from typing import Optional, Any

from pydantic import BaseModel


class Response(BaseModel):
    code: Optional[int] = None
    data: Optional[Any] = None
    message: Optional[str] = None
    total: Optional[int] = None
