from asyncua import Node

from aquacloud_common.models.sensor.environment.ftu_sensor import FTUSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class FTUSensorNode(BaseSensorNode):
    def __init__(self, model: FTUSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        ftu = await self.node.get_child(str(self.ns) + ":" + "FTU")
        if ftu is not None:
            await AnalogItemNode(ftu, self.model.ftu).update_properties_node()