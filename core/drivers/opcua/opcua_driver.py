import asyncio
import logging
import os

from core.constants import CONFIG_PATH
from core.drivers.base_driver import BaseDriver
from core.drivers.opcua.opc_ua_config_parser import OpcuaConfigurationParser
from core.drivers.opcua.opcua_worker import OpcuaWorker
from core.drivers.opcua.server_model import ServerModel
from core.opcua.opcua_server import OPCUAServer
from models.sensor_model import OpcSensorModel


_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class OpcuaDriver(BaseDriver):
    def __init__(self, server: OPCUAServer):
        super().__init__(server)
        self._servers: list[ServerModel] = []
        self._unit_sensors: list[OpcSensorModel] = []

    def parse_config(self):
        config_path_file = os.path.join(CONFIG_PATH, "opcua_config.json")
        config_parser = OpcuaConfigurationParser(config_path_file)
        config_parser.parse_config_file()
        self.units = config_parser.get_units()
        self.sensors = config_parser.get_standard_sensors()
        self.mapping = config_parser.create_mapping()
        self._servers = config_parser.get_servers()
        self._unit_sensors = config_parser.get_unit_sensors()

    async def start(self):
        self.is_starting = True
        self.parse_config()
        await self.create_unit_nodes()
        # await self.create_sensors()

        for server in self._servers:
            try:
                worker = OpcuaWorker(server, self._unit_sensors, self.mapping, self.server)
                asyncio.get_event_loop().create_task(worker.run())
            except Exception as e:
                _logger.warning(e)

    def stop(self):
        self.is_starting = False

    async def subscribe(self):
        pass