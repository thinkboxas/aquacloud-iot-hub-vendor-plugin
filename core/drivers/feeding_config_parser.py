import json
import os

from aquacloud_common.core.core_type import FeedingSensorType
from aquacloud_common.models.organization.unit import UnitModel
from aquacloud_common.models.sensor.base_sensor import BaseSensorModel
from aquacloud_common.models.sensor.feeding.calculated_accumulated_feeding_sensor import \
    CalculatedAccumulatedFeedingSensorModel
from aquacloud_common.models.sensor.feeding.feed_silo_sensor import FeedSiloSensorModel
from aquacloud_common.models.sensor.feeding.feeding_intensity_sensor import FeedingIntensitySensorModel
from models.mapping_model import MappingModel
from models.sensor_model import SensorModel


class FeedingConfigurationParser:
    def __init__(self, config_file: str):
        self._config_file = config_file
        self._sensors: list[SensorModel] = []

    def parse_config_file(self):
        try:
            with open(self._config_file) as json_file:
                config = json.load(json_file)
                self._sensors = [SensorModel.model_validate(sensor) for sensor in config["sensors"]]
        except Exception as e:
            print("Configuration file not found on disk!", e)

    def create_units(self) -> list[UnitModel]:
        units: dict[str, UnitModel] = {}
        for sensor in self._sensors:
            unit_id = sensor.unit_id
            if sensor.unit_id not in units:
                unit = UnitModel(
                    id=unit_id,
                    name=unit_id
                )
                units[unit_id] = unit
            standard_sensor = self._create_standard_sensor(sensor)
            standard_sensor.name = standard_sensor.__class__.__name__.replace("Model", "")
            units[unit_id].sensors.append(standard_sensor)

        return [units[key] for key in units]

    @staticmethod
    def _create_standard_sensor(sensor: SensorModel) -> BaseSensorModel:
        if sensor.sensor_type == FeedingSensorType.FEEDING_INTENSITY:
            return FeedingIntensitySensorModel()
        elif sensor.sensor_type == FeedingSensorType.FEED_SILO:
            return FeedSiloSensorModel()
        else:
            return CalculatedAccumulatedFeedingSensorModel()

    def create_mapping(self) -> dict[str, list[MappingModel]]:
        mapping: dict[str, list[MappingModel]] = {}
        for sensor in self._sensors:
            sensor_name = sensor.sensor_type.replace("Type", "")
            for key in sensor.mapping:
                mapping_key = sensor.unit_id + ":" + sensor_name + ":" + sensor.mapping[key]
                mapping_model = MappingModel(
                    unit_id=sensor.unit_id,
                    sensor=sensor_name,
                    measurement=key
                )

                if mapping_key not in mapping:
                    mapping[mapping_key] = []

                mapping[mapping_key].append(mapping_model)

        return mapping




