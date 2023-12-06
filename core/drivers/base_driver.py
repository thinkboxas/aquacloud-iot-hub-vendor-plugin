import abc

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

    @abc.abstractmethod
    def on_data_change(self, tag: str, value: float, timestamp: str):
        pass

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

