from pydantic import BaseModel


class SensorModel(BaseModel):
    unit_id: str
    sensor_type: str
    mapping: dict[str, str]
