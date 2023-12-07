from typing import Optional

from pydantic import BaseModel


class MappingModel(BaseModel):
    unit_id: str
    sensor: str
    measurement: str
    depth: Optional[str] = ""
