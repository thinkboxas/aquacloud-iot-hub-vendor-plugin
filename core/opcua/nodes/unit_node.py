from asyncua import Node

from aquacloud_common.models.organization.unit import UnitModel
from core.opcua.nodes.base_node import Base
from core.opcua.nodes.sensor_base_node import SensorBaseNode
from utilities.opcua import update_external_references_node, update_position_node


class Unit(Base):
    def __init__(self, model: UnitModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, model.name, path)
        self.model = model

    async def update_object_properties_node(self):
        properties = await self.node.get_properties()
        name_node = properties[0]
        await name_node.set_value(self.model.name)

    async def _create_sensors(self):
        sensors_node = await self.node.get_child(str(self.ns) + ":Sensors")
        for sensor in self.model.sensors:
            sensor_node = SensorBaseNode(sensor, self.ns, sensors_node, self.identifier)
            await sensor_node.init()

    async def init(self):
        await super().init()

        # Update ExternalReferences
        external_references_node = await self.node.get_child(str(self.ns) + ":ExternalReferences")
        if external_references_node is not None:
            await update_external_references_node(
                self.ns,
                external_references_node,
                self.model.external_references,
                self.identifier
            )

        # Update Position
        position_node = await self.node.get_child(str(self.ns) + ":Position")
        if position_node is not None:
            await update_position_node(self.ns, position_node, self.model.position)

        # create sensor nodes
        await self._create_sensors()

