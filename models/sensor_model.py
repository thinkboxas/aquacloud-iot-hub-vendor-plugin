from typing import Optional

from pydantic import BaseModel


class SensorModel(BaseModel):
    sensor_name: Optional[str] = ""
    type: str
    unit_id: str
    sensor_type: str
    depth: Optional[float] = None
    mapping: dict[str, str]


class NodeModel(BaseModel):
    ns: int
    i: int


class OpcSensorModel(SensorModel):
    mapping: dict[str, NodeModel]
    type: Optional[str] = "unit"
    unit_id: Optional[str] = ""
