import abc

from asyncua import ua

from aquacloud_common.models.organization.unit import UnitModel
from core.opcua.nodes.unit_node import Unit
from core.opcua.opcua_server import OPCUAServer
from models.mapping_model import MappingModel


class BaseDriver(metaclass=abc.ABCMeta):
    def __init__(self, server: OPCUAServer):
        self.units: list[UnitModel] = []
        self.mapping: dict[str, list[MappingModel]] = {}
        self.is_starting: bool = False
        self.server: OPCUAServer = server

    async def create_unit_nodes(self):
        for unit_model in self.units:
            unit = Unit(unit_model, self.server.get_namespace(), self.server.get_objects_node())
            await unit.init()

    async def on_data_change(self, tag: str, value: float, timestamp: str):
        sensors: list[MappingModel] = self.mapping[tag]
        for sensor_mapping in sensors:
            identifier = "Unit|" + sensor_mapping.unit_id + \
                         "|Sensor|" + sensor_mapping.sensor + \
                         "." + sensor_mapping.measurement

            measurement_node = self.server.get_node(identifier)
            if measurement_node is not None:
                await measurement_node.set_value(ua.Float(value))

                sensor_node = await measurement_node.get_parent()
                local_time_stamp = await sensor_node.get_child(
                    str(self.server.get_namespace()) + ":" + "LocalTimestamp")
                if local_time_stamp is not None:
                    await local_time_stamp.set_value(ua.String(timestamp))

    @abc.abstractmethod
    def parse_config(self):
        pass

    @abc.abstractmethod
    async def start(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @abc.abstractmethod
    def subscribe(self):
        pass
