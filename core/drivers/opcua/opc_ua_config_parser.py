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
from core.drivers.opcua.server_model import ServerModel
from models.mapping_model import MappingModel
from models.sensor_model import OpcSensorModel

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class OpcuaConfigurationParser:
    def __init__(self, config_file: str):
        self._config_file = config_file
        self._sensors: list[OpcSensorModel] = []
        self._server: list[ServerModel] = []
        self._standard_sensors: list[BaseSensorModel] = []
        self._units: list[UnitModel] = []

    def parse_config_file(self):
        try:
            with open(self._config_file) as json_file:
                config = json.load(json_file)
                sensors = config["sensors"]
                for s in sensors:
                    sensor = OpcSensorModel.model_validate(s)
                    self._sensors.append(sensor)
                    standard_sensor = self._create_standard_sensor(sensor)
                    self._standard_sensors.append(standard_sensor)

                for unit in config["units"]:
                    server = ServerModel.model_validate(unit["server"])
                    server.unit_id = unit["unit_id"]
                    self._server.append(server)

                    unit = UnitModel(
                        id=unit["unit_id"],
                        name=unit["unit_id"]
                    )

                    unit.sensors = self._standard_sensors
                    self._units.append(unit)

                return

        except Exception as e:
            _logger.warning("Configuration file not found on disk!", e)

    def get_standard_sensors(self) -> list[BaseSensorModel]:
        return self._standard_sensors

    def get_units(self) -> list[UnitModel]:
        return self._units

    def get_servers(self) -> list[ServerModel]:
        return self._server

    def get_unit_sensors(self) -> list[OpcSensorModel]:
        return self._sensors

    def create_mapping(self) -> dict[str, list[MappingModel]]:
        mapping: dict[str, list[MappingModel]] = {}
        for unit in self._units:
            for sensor in self._sensors:
                sensor_name = sensor.sensor_name
                for key in sensor.mapping:
                    mapping_key = unit.id + ":" + str(sensor.mapping[key].ns) + "_" \
                                  + str(sensor.mapping[key].i) + ":" + sensor_name
                    mapping_model = MappingModel(
                        unit_id=unit.id,
                        sensor=sensor_name,
                        measurement=key
                    )

                    if mapping_key not in mapping:
                        mapping[mapping_key] = []

                    mapping[mapping_key].append(mapping_model)

                # make default timestamp mapping
                mapping_key = sensor.unit_id + ":" + "local_timestamp" + ":" + sensor_name
                mapping[mapping_key] = [
                    MappingModel(
                        unit_id=sensor.unit_id,
                        sensor=sensor_name,
                        measurement="LocalTimestamp"
                    )
                ]

        return mapping

    @staticmethod
    def _create_standard_sensor(sensor: OpcSensorModel) -> BaseSensorModel:
        model: BaseSensorModel = BaseSensorModel()
        namespace_uri = "http://www.opcfoundation.org/UA/units/un/cefact"

        if sensor.sensor_type == EnvironmentSensorType.OXYGEN_SATURATION:
            model = OxygenSaturationSensorModel()
            model.oxygen_saturation.engineering_units.namespace_uri = namespace_uri
            model.oxygen_saturation.engineering_units.display_name = "%"
            model.oxygen_saturation.engineering_units.description = "Percentage"
        elif sensor.sensor_type == EnvironmentSensorType.OXYGEN_CONCENTRATION:
            model = OxygenConcentrationSensorModel()
            model.oxygen_concentration.engineering_units.namespace_uri = namespace_uri
            model.oxygen_concentration.engineering_units.display_name = "mg/l"
            model.oxygen_concentration.engineering_units.description = "Milligram per liter"
            model.salinity.engineering_units.namespace_uri = namespace_uri
            model.salinity.engineering_units.display_name = "ppt"
            model.salinity.engineering_units.description = "Parts per thousand"
        elif sensor.sensor_type == EnvironmentSensorType.TEMPERATURE:
            model = TemperatureSensorModel()
            model.temperature.engineering_units.namespace_uri = namespace_uri
            model.temperature.engineering_units.display_name = "C°"
            model.temperature.engineering_units.description = "Celsius"
        elif sensor.sensor_type == EnvironmentSensorType.SALINITY:
            model = SalinitySensorModel()
            model.salinity.engineering_units.namespace_uri = namespace_uri
            model.salinity.engineering_units.display_name = "ppt"
            model.salinity.engineering_units.description = "Parts per thousand"
        elif sensor.sensor_type == EnvironmentSensorType.SEA_CURRENT:
            model = SeaCurrentSensorModel()
            model.direction.engineering_units.namespace_uri = namespace_uri
            model.direction.engineering_units.display_name = "Absolute North"
            model.direction.engineering_units.description = "Absolute direction in degrees"

            model.speed.engineering_units.namespace_uri = namespace_uri
            model.speed.engineering_units.display_name = "cm/s"
            model.speed.engineering_units.description = "Centimeter per second"
        elif sensor.sensor_type == EnvironmentSensorType.NTU:
            model = NTUSensorModel()
            model.ntu.engineering_units.namespace_uri = namespace_uri
            model.ntu.engineering_units.display_name = "NTU"
            model.ntu.engineering_units.description = "Nephelometric Turbidity Units"
        elif sensor.sensor_type == EnvironmentSensorType.FTU:
            model = FTUSensorModel()
            model.ftu.engineering_units.namespace_uri = namespace_uri
            model.ftu.engineering_units.display_name = "FTU"
            model.ftu.engineering_units.description = "Formazin Turbidity Units"
        elif sensor.sensor_type == EnvironmentSensorType.PH:
            model = PHSensorModel()
            model.ph.engineering_units.namespace_uri = namespace_uri
            model.ph.engineering_units.display_name = "pH"
            model.ph.engineering_units.description = "pH"
        elif sensor.sensor_type == EnvironmentSensorType.LIGHT:
            model = LightSensorModel()
            model.lux.engineering_units.namespace_uri = namespace_uri
            model.lux.engineering_units.display_name = "lux"
            model.lux.engineering_units.description = "Lumen per square meter"

        model.name = sensor.sensor_name

        return model
