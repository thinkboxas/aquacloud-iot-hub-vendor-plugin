import logging
import os
from typing import Any

from asyncua import Server, ua, Node
from asyncua.ua import String, Int16, NodeId
from asyncua.server.users import UserRole, User

from aquacloud_common.models.sensor.base_sensor import BaseSensorModel
from aquacloud_common.models.sensor.environment.co2_sensor import CO2SensorModel
from aquacloud_common.models.sensor.environment.ftu_sensor import FTUSensorModel
from aquacloud_common.models.sensor.environment.light_sensor import LightSensorModel
from aquacloud_common.models.sensor.environment.ntu_sensor import NTUSensorModel
from aquacloud_common.models.sensor.environment.oxygen_concentration_sensor import OxygenConcentrationSensorModel
from aquacloud_common.models.sensor.environment.oxygen_saturation_sensor import OxygenSaturationSensorModel
from aquacloud_common.models.sensor.environment.ph_sensor import PHSensorModel
from aquacloud_common.models.sensor.environment.salinity_sensor import SalinitySensorModel
from aquacloud_common.models.sensor.environment.sea_current_sensor import SeaCurrentSensorModel
from aquacloud_common.models.sensor.environment.temperature_sensor import TemperatureSensorModel
from aquacloud_common.models.sensor.feeding.calculated_accumulated_feeding_sensor import \
    CalculatedAccumulatedFeedingSensorModel
from aquacloud_common.models.sensor.feeding.feed_silo_sensor import FeedSiloSensorModel
from aquacloud_common.models.sensor.feeding.feeding_intensity_sensor import FeedingIntensitySensorModel
from core.opcua.nodes.base_sensor_node import BaseSensorNode
from core.opcua.nodes.calculated_accumulated_deeding_sensor_node import CalculatedAccumulatedFeedingSensorNode
from core.opcua.nodes.co2_sensor_node import CO2SensorNode
from core.opcua.nodes.feed_silo_sensor_node import FeedSiloSensorNode
from core.opcua.nodes.feeding_intensity_sensor_node import FeedingIntensitySensorNode
from core.opcua.nodes.ftu_sensor_node import FTUSensorNode
from core.opcua.nodes.light_sensor_node import LightSensorNode
from core.opcua.nodes.ntu_sensor_node import NTUSensorNode
from core.opcua.nodes.oxygen_concentration_sensor_node import OxygenConcentrationSensorNode
from core.opcua.nodes.oxygen_saturation_sensor_node import OxygenSaturationSensorNode
from core.opcua.nodes.ph_sensor_node import PHSensorNode
from core.opcua.nodes.salinity_sensor_node import SalinitySensorNode
from core.opcua.nodes.sea_current_sensor_node import SeaCurrentSensorNode
from core.opcua.nodes.temperature_sensor_node import TemperatureSensorNode

USERNAME = os.getenv("OPC_UA_USERNAME", "")
PASSWORD = os.getenv("OPC_UA_PASSWORD", "")

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class UserManager:
    def get_user(self, iserver, username=None, password=None, certificate=None):
        if username == USERNAME and password == PASSWORD:
            return User(role=UserRole.Admin)
        return None


class OPCUAServer:
    def __init__(
            self,
            endpoint: str,
            name: str,
            uri: str,
            xml_file_path: str
    ):
        self._server: Server = Server(user_manager=UserManager())
        self._xml_file_path: str = xml_file_path
        self._uri: str = uri
        self._ns: int = 2
        self._server.set_endpoint(endpoint)
        self._server.set_server_name(name)
        self._server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt
        ])
        self._server.set_security_IDs(["Username"])

        self._objects_node: Node = self._server.get_objects_node()

    async def init(self) -> bool:
        await self._server.init()
        self._ns = await self._server.register_namespace(self._uri)
        return await self._import_nodeset_from_xml_file(self._xml_file_path)

    async def _import_nodeset_from_xml_file(self, xml_file_path: str) -> bool:
        try:
            await self._server.import_xml(path=xml_file_path)
            return True
        except Exception as e:
            _logger.warning(e)
        return False

    async def __aenter__(self):
        status = await self.init()
        if status is True:
            if status is True:
                await self._server.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        await self._server.stop()

    def get_node(self, identifier: str) -> Node | None:
        node_id = ua.NodeId(String(identifier), Int16(self._ns))
        try:
            return self._server.get_node(node_id)
        except Exception as e:
            _logger.warning("Node not found", e)
            return None

    async def get_node_by_node_id(self, node_id: NodeId) -> Node | None:
        try:
            return self._server.get_node(node_id)
        except Exception as e:
            _logger.warning("Node not found", e)
            return None

    def get_namespace(self):
        return self._ns

    def get_objects_node(self):
        return self._objects_node

    @staticmethod
    async def create_sensors(sensors_node: Node, sensors: list[BaseSensorModel], ns: int, identifier: str):
        for sensor in sensors:
            class_name = sensor.__class__
            sensor_node = BaseSensorNode(sensor, ns, sensors_node, identifier)
            if class_name == CalculatedAccumulatedFeedingSensorModel:
                s = CalculatedAccumulatedFeedingSensorModel.model_validate(sensor.model_dump())
                sensor_node = CalculatedAccumulatedFeedingSensorNode(s, ns, sensors_node, identifier)
            elif class_name == FeedingIntensitySensorModel:
                s = FeedingIntensitySensorModel.model_validate(sensor.model_dump())
                sensor_node = FeedingIntensitySensorNode(s, ns, sensors_node, identifier)
            elif class_name == FeedSiloSensorModel:
                s = FeedSiloSensorModel.model_validate(sensor.model_dump())
                sensor_node = FeedSiloSensorNode(s, ns, sensors_node, identifier)
            elif class_name == OxygenSaturationSensorModel:
                s = OxygenSaturationSensorModel.model_validate(sensor.model_dump())
                sensor_node = OxygenSaturationSensorNode(s, ns, sensors_node, identifier)
            elif class_name == OxygenConcentrationSensorModel:
                s = OxygenConcentrationSensorModel.model_validate(sensor.model_dump())
                sensor_node = OxygenConcentrationSensorNode(s, ns, sensors_node, identifier)
            elif class_name == TemperatureSensorModel:
                s = TemperatureSensorModel.model_validate(sensor.model_dump())
                sensor_node = TemperatureSensorNode(s, ns, sensors_node, identifier)
            elif class_name == SalinitySensorModel:
                s = SalinitySensorModel.model_validate(sensor.model_dump())
                sensor_node = SalinitySensorNode(s, ns, sensors_node, identifier)
            elif class_name == SeaCurrentSensorModel:
                s = SeaCurrentSensorModel.model_validate(sensor.model_dump())
                sensor_node = SeaCurrentSensorNode(s, ns, sensors_node, identifier)
            elif class_name == NTUSensorModel:
                s = NTUSensorModel.model_validate(sensor.model_dump())
                sensor_node = NTUSensorNode(s, ns, sensors_node, identifier)
            elif class_name == FTUSensorModel:
                s = FTUSensorModel.model_validate(sensor.model_dump())
                sensor_node = FTUSensorNode(s, ns, sensors_node, identifier)
            elif class_name == PHSensorModel:
                s = PHSensorModel.model_validate(sensor.model_dump())
                sensor_node = PHSensorNode(s, ns, sensors_node, identifier)
            elif class_name == CO2SensorModel:
                s = CO2SensorModel.model_validate(sensor.model_dump())
                sensor_node = CO2SensorNode(s, ns, sensors_node, identifier)
            elif class_name == LightSensorModel:
                s = LightSensorModel.model_validate(sensor.model_dump())
                sensor_node = LightSensorNode(s, ns, sensors_node, identifier)

            await sensor_node.init()
