import abc
from typing import Any

from asyncua import ua, Node

from aquacloud_common.models.organization.unit import UnitModel
from aquacloud_common.models.sensor.base_sensor import BaseSensorModel
from core.opcua.nodes.unit_node import Unit
from core.opcua.opcua_server import OPCUAServer
from models.mapping_model import MappingModel


class BaseDriver(metaclass=abc.ABCMeta):
    def __init__(self, server: OPCUAServer):
        self.units: list[UnitModel] = []
        self.sensors: list[BaseSensorModel] = []
        self.mapping: dict[str, list[MappingModel]] = {}
        self.is_starting: bool = False
        self.server: OPCUAServer = server

    async def create_unit_nodes(self):
        for unit_model in self.units:
            unit = Unit(unit_model, self.server.get_namespace(), self.server.get_objects_node())
            await unit.init()

    async def create_sensors(self):
        # create sensor nodes
        objects_node = self.server.get_objects_node()
        await OPCUAServer.create_sensors(objects_node, self.sensors, self.server.get_namespace(), "")

    async def on_data_change(self, tag: str, value: Any, timestamp: str):
        sensors: list[MappingModel] = self.mapping[tag]
        for sensor_mapping in sensors:
            measurement_path = sensor_mapping.measurement
            if sensor_mapping.measurement == "Depth":
                measurement_path = "Position.Depth"
            if sensor_mapping.unit_id != "":
                identifier = "Unit|" + sensor_mapping.unit_id + \
                             "|Sensor|" + sensor_mapping.sensor + \
                             "." + measurement_path
            else:
                identifier = "Sensor|" + sensor_mapping.sensor + \
                             "." + measurement_path

            measurement_node = self.server.get_node(identifier)
            if measurement_node is not None:
                if sensor_mapping.measurement == "LocalTimestamp":
                    await measurement_node.set_value(ua.String(value))
                else:
                    await measurement_node.set_value(ua.Float(value))

                # if sensor_mapping.measurement != "Depth":
                #     sensor_node = await measurement_node.get_parent()
                #     local_time_stamp = await sensor_node.get_child(
                #         str(self.server.get_namespace()) + ":" + "LocalTimestamp")
                #     if local_time_stamp is not None:
                #         await local_time_stamp.set_value(ua.String(timestamp))

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
