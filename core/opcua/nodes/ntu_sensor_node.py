from asyncua import Node

from aquacloud_common.models.sensor.environment.ntu_sensor import NTUSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class NTUSensorNode(BaseSensorNode):
    def __init__(self, model: NTUSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        ntu = await self.node.get_child(str(self.ns) + ":" + "NTU")
        if ntu is not None:
            await AnalogItemNode(ntu, self.model.ntu).update_properties_node()
