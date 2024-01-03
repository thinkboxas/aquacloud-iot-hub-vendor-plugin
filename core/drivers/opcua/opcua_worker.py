import asyncio
import logging
import time
from datetime import datetime
from typing import Any

from asyncua import Client, ua, Node
from asyncua.common.subscription import Subscription, DataChangeNotif
from asyncua.ua import String, Int16, Int32

from core.drivers.opcua.server_model import ServerModel
from core.opcua.opcua_server import OPCUAServer
from models.mapping_model import MappingModel
from models.sensor_model import OpcSensorModel, NodeModel

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

RECONNECT_TIME_OUT = 5
DISCOVERY_INTERVAL = 60 * 60


class OpcuaWorker:
    def __init__(
            self,
            server: ServerModel,
            sensors: list[OpcSensorModel],
            mapping: dict[str, list[MappingModel]],
            opc_server: OPCUAServer
    ):
        self._server: ServerModel = server
        self._opc_server = opc_server
        self._unit_id: str = server.unit_id
        self._sensors: list[OpcSensorModel] = sensors
        self._mapping = mapping
        self._client: Client = None
        self._subscription_nodes: list[Node] = []
        self._subscriber: Subscription = None

    async def subscribe(self):
        for sensor in self._sensors:
            try:
                for key in sensor.mapping:
                    node_model: NodeModel = sensor.mapping[key]
                    node_id = ua.NodeId(Int32(node_model.i), Int16(node_model.ns))
                    node = self._client.get_node(node_id)
                    if node is not None:
                        self._subscription_nodes.append(node)
                await self._subscriber.subscribe_data_change(self._subscription_nodes)
            except Exception as e:
                _logger.warning(e)

    async def run(self):
        while True:
            try:
                self._client = Client(self._server.endpoint)
                self._client.set_user(self._server.username)
                self._client.set_password(self._server.password)
                async with self._client:
                    self._subscriber = await self._client.create_subscription(500, self)
                    try:
                        await self.subscribe()
                    except Exception as e:
                        _logger.warning(e)
                    while True:
                        await asyncio.sleep(5)
            except Exception as e:
                _logger.warning(e)
            await asyncio.sleep(DISCOVERY_INTERVAL)

    async def _handle_data_change(self, node: Node, value: Any):
        ns = node.nodeid.NamespaceIndex
        i = node.nodeid.Identifier
        key = self._unit_id + ":" + str(ns) + "_" + str(i)
        for mapping_key in self._mapping:
            if key in mapping_key:
                mapping = self._mapping[mapping_key]
                for m in mapping:
                    measurement_path = m.measurement
                    if m.measurement == "Depth":
                        measurement_path = "Position.Depth"
                    identifier = "Unit|" + m.unit_id + \
                                 "|Sensor|" + m.sensor + \
                                 "." + measurement_path

                    measurement_node = self._opc_server.get_node(identifier)
                    if measurement_node is not None:
                        await measurement_node.set_value(ua.Float(value))

                        timestamp = time.time()
                        timestamp = datetime.fromtimestamp(timestamp)
                        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                        parent_node = await measurement_node.get_parent()
                        local_timestamp_node = await parent_node.get_child(str(ns) + ":" + "LocalTimestamp")
                        if local_timestamp_node is not None:
                            await local_timestamp_node.set_value(ua.String(timestamp))

                break

    def datachange_notification(self, node: Node, val: Any, data: DataChangeNotif):
        asyncio.get_event_loop().create_task(self._handle_data_change(node, val))
