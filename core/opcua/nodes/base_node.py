import abc
import logging

from asyncua import Node, ua, Server
from asyncua.common.manage_nodes import create_object
from asyncua.ua import Int16, String

from aquacloud_common.models.common.aqua_base_model import AquaBaseModel
from utilities.config_parser import get_type_definition_identifier_from_model

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class Base(metaclass=abc.ABCMeta):
    def __init__(
            self,
            model: AquaBaseModel,
            ns: int,
            parent_node: Node, browser_name: str,
            path: str = ""
    ):
        self.model: AquaBaseModel = model
        self.ns: int = ns
        self.parent_node = parent_node
        self._browser_name = browser_name
        self.node: Node | None = None

        obj_type = self.__class__.__name__

        if "Sensor" in self.__class__.__name__:
            obj_type = "Sensor"

        self.identifier = obj_type + "|" + model.name

        if path != "":
            self.identifier = path + "|" + obj_type + "|" + model.name

    @abc.abstractmethod
    async def update_object_properties_node(self):
        pass

    async def _init_node(self) -> Node | None:
        node_id = ua.NodeId(String(self.identifier), Int16(self.ns))
        type_definition_identifier = get_type_definition_identifier_from_model(self.model)
        type_definition = ua.NodeId(String(type_definition_identifier), Int16(self.ns))
        try:
            return await create_object(self.parent_node, node_id, self._browser_name, type_definition)
        except Exception as e:
            _logger.warning("Cannot create node", e)
            return None

    @abc.abstractmethod
    async def init(self):
        self.node = await self._init_node()
        if self.node is not None:
            # update node property value
            await self.update_object_properties_node()



