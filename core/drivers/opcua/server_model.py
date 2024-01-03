from typing import Optional

from pydantic import BaseModel


class ServerModel(BaseModel):
    unit_id: Optional[str] = ""
    endpoint: str
    username: str
    password: str