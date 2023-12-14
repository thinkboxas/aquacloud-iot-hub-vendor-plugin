import json
import logging

from aquacloud_common.core.core_type import EnvironmentSensorType
from aquacloud_common.models.organization.unit import UnitModel
from aquacloud_common.models.sensor.base_sensor import BaseSensorModel
from aquacloud_common.models.sensor.environment.ftu_sensor import FTUSensorModel
from aquacloud_common.models.sensor.environment.light_sensor import LightSensorModel
from aquacloud_common.models.sensor.environment.ntu_sensor import NTUSensorModel
from aquacloud_common.models.sensor.environment.oxygen_concentration_sensor import OxygenConcentrationSensorModel
from aquacloud_common.models.sensor.environment.oxygen_saturation_sensor import OxygenSaturationSensorModel
from aquacloud_common.models.sensor.environment.ph_sensor import PHSensorModel
from aquacloud_common.models.sensor.environment.salinity_sensor import SalinitySensorModel
from aquacloud_common.models.sensor.environment.sea_current_sensor import SeaCurrentSensorModel
from aquacloud_common.models.sensor.environment.temperature_sensor import TemperatureSensorModel
from models.mapping_model import MappingModel
from models.sensor_model import SensorModel


_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class EnvironmentConfigurationParser:
    def __init__(self, config_file: str):
        self._config_file = config_file
        self._sensors: list[SensorModel] = []
        self._standard_sensors: list[BaseSensorModel] = []

    def parse_config_file(self):
        try:
            with open(self._config_file) as json_file:
                config = json.load(json_file)
                self._sensors = [SensorModel.model_validate(sensor) for sensor in config["sensors"]]
        except Exception as e:
            _logger.warning("Configuration file not found on disk!", e)

    def create_units(self) -> list[UnitModel]:
        units: dict[str, UnitModel] = {}
        for sensor in self._sensors:
            standard_sensor = self._create_standard_sensor(sensor)

            if sensor.type == "site":
                self._standard_sensors.append(standard_sensor)
            else:
                unit_id = sensor.unit_id
                if sensor.unit_id not in units:
                    unit = UnitModel(
                        id=unit_id,
                        name=unit_id
                    )
                    units[unit_id] = unit
                units[unit_id].sensors.append(standard_sensor)

        return [units[key] for key in units]

    def get_standard_sensors(self) -> list[BaseSensorModel]:
        return self._standard_sensors

    @staticmethod
    def _create_standard_sensor(sensor: SensorModel) -> BaseSensorModel:
        model: BaseSensorModel = BaseSensorModel()

        depth = "dynamic_depth"
        if sensor.depth is not None:
            model.position.depth = sensor.depth
            depth = str(int(sensor.depth)) + "m"

        namespace_uri = "http://www.opcfoundation.org/UA/units/un/cefact"
        if sensor.sensor_type == EnvironmentSensorType.OXYGEN_SATURATION:
            model = OxygenSaturationSensorModel()
            model.name = "OxygenSaturation_" + depth
            model.oxygen_saturation.engineering_units.namespace_uri = namespace_uri
            model.oxygen_saturation.engineering_units.display_name = "%"
            model.oxygen_saturation.engineering_units.description = "Percentage"
        elif sensor.sensor_type == EnvironmentSensorType.OXYGEN_CONCENTRATION:
            model = OxygenConcentrationSensorModel()
            model.name = "OxygenConcentration_" + depth
            model.oxygen_concentration.engineering_units.namespace_uri = namespace_uri
            model.oxygen_concentration.engineering_units.display_name = "mg/l"
            model.oxygen_concentration.engineering_units.description = "Milligram per liter"
            model.salinity.engineering_units.namespace_uri = namespace_uri
            model.salinity.engineering_units.display_name = "ppt"
            model.salinity.engineering_units.description = "Parts per thousand"
        elif sensor.sensor_type == EnvironmentSensorType.TEMPERATURE:
            model = TemperatureSensorModel()
            model.name = "Temperature_" + depth
            model.temperature.engineering_units.namespace_uri = namespace_uri
            model.temperature.engineering_units.display_name = "C°"
            model.temperature.engineering_units.description = "Celsius"
        elif sensor.sensor_type == EnvironmentSensorType.SALINITY:
            model = SalinitySensorModel()
            model.name = "Salinity_" + depth
            model.salinity.engineering_units.namespace_uri = namespace_uri
            model.salinity.engineering_units.display_name = "ppt"
            model.salinity.engineering_units.description = "Parts per thousand"
        elif sensor.sensor_type == EnvironmentSensorType.SEA_CURRENT:
            model = SeaCurrentSensorModel()
            model.name = "SeaCurrent_" + depth
            model.direction.engineering_units.namespace_uri = namespace_uri
            model.direction.engineering_units.display_name = "Absolute North"
            model.direction.engineering_units.description = "Absolute direction in degrees"

            model.speed.engineering_units.namespace_uri = namespace_uri
            model.speed.engineering_units.display_name = "cm/s"
            model.speed.engineering_units.description = "Centimeter per second"
        elif sensor.sensor_type == EnvironmentSensorType.NTU:
            model = NTUSensorModel()
            model.name = "NTU_" + depth
            model.ntu.engineering_units.namespace_uri = namespace_uri
            model.ntu.engineering_units.display_name = "NTU"
            model.ntu.engineering_units.description = "Nephelometric Turbidity Units"
        elif sensor.sensor_type == EnvironmentSensorType.FTU:
            model = FTUSensorModel()
            model.name = "FTU_" + depth
            model.ftu.engineering_units.namespace_uri = namespace_uri
            model.ftu.engineering_units.display_name = "FTU"
            model.ftu.engineering_units.description = "Formazin Turbidity Units"
        elif sensor.sensor_type == EnvironmentSensorType.PH:
            model = PHSensorModel()
            model.name = "PH_" + depth
            model.ph.engineering_units.namespace_uri = namespace_uri
            model.ph.engineering_units.display_name = "pH"
            model.ph.engineering_units.description = "pH"
        elif sensor.sensor_type == EnvironmentSensorType.LIGHT:
            model = LightSensorModel()
            model.name = "Light_" + depth
            model.lux.engineering_units.namespace_uri = namespace_uri
            model.lux.engineering_units.display_name = "lux"
            model.lux.engineering_units.description = "Lumen per square meter"

        return model

    @staticmethod
    def get_sensor_name(sensor: SensorModel):
        depth = "dynamic_depth"
        if sensor.depth is not None:
            depth = str(int(sensor.depth)) + "m"
        if sensor.sensor_type == EnvironmentSensorType.OXYGEN_SATURATION:
            return "OxygenSaturation_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.OXYGEN_CONCENTRATION:
            return "OxygenConcentration_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.TEMPERATURE:
            return "Temperature_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.SALINITY:
            return "Salinity_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.SEA_CURRENT:
            return "SeaCurrent_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.NTU:
            return "NTU_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.FTU:
            return "FTU_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.PH:
            return "PH_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.LIGHT:
            return "Light_" + depth

    def create_mapping(self) -> dict[str, list[MappingModel]]:
        mapping: dict[str, list[MappingModel]] = {}
        for sensor in self._sensors:
            sensor_name = self.get_sensor_name(sensor)
            for key in sensor.mapping:

                if sensor.type == "site":
                    mapping_key = "site:" + sensor.mapping[key] + ":" + sensor_name
                else:
                    mapping_key = sensor.unit_id + ":" + sensor.mapping[key] + ":" + sensor_name

                mapping_model = MappingModel(
                    unit_id=sensor.unit_id,
                    sensor=sensor_name,
                    measurement=key
                )

                if mapping_key not in mapping:
                    mapping[mapping_key] = []

                mapping[mapping_key].append(mapping_model)

            # make default timestamp mapping
            if sensor.type == "site":
                mapping_key = "site:" + "local_timestamp" + ":" + sensor_name
            else:
                mapping_key = sensor.unit_id + ":" + "local_timestamp" + ":" + sensor_name
            mapping[mapping_key] = [
                MappingModel(
                    unit_id=sensor.unit_id,
                    sensor=sensor_name,
                    measurement="LocalTimestamp"
                )
            ]

        return mapping




