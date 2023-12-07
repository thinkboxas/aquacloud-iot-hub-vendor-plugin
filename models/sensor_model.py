from typing import Optional

from pydantic import BaseModel


class SensorModel(BaseModel):
    type: str
    unit_id: str
    sensor_type: str
    depth: Optional[float] = None
    mapping: dict[str, str]
