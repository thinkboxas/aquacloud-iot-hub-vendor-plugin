from asyncua import Node

from aquacloud_common.models.sensor.base_sensor import BaseSensorModel
from core.opcua.nodes.base_node import Base
from utilities.opcua import update_external_references_node, update_position_node


class SensorBaseNode(Base):
    def __init__(self, model: BaseSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, model.name, path)
        self.model = model

    async def init(self):
        await super().init()

        # # Update ExternalReferences
        # external_references_node = await self.node.get_child(str(self.ns) + ":ExternalReferences")
        # if external_references_node is not None:
        #     await update_external_references_node(
        #         self.ns,
        #         external_references_node,
        #         self.model.external_references,
        #         self.identifier
        #     )
        #
        # # Update Position
        # position_node = await self.node.get_child(str(self.ns) + ":Position")
        # if position_node is not None:
        #     await update_position_node(self.ns, position_node, self.model.position)

    async def update_object_properties_node(self):
        pass
