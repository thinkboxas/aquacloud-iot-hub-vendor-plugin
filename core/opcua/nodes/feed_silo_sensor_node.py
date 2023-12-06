from asyncua import Node

from aquacloud_common.models.sensor.feeding.feed_silo_sensor import FeedSiloSensorModel
from core.opcua.nodes.analog_item_node import AnalogItemNode
from core.opcua.nodes.base_sensor_node import BaseSensorNode


class FeedSiloSensorNode(BaseSensorNode):
    def __init__(self, model: FeedSiloSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, path)
        self.model = model

    async def update_analog_item_variables_node(self):
        feed = await self.node.get_child(str(self.ns) + ":" + "Feed")
        silo_capacity = await self.node.get_child(str(self.ns) + ":" + "SiloCapacity")
        fill_percentage = await self.node.get_child(str(self.ns) + ":" + "FillPercentage")

        if feed is not None:
            await AnalogItemNode(feed, self.model.feed).update_properties_node()

        if silo_capacity is not None:
            await AnalogItemNode(feed, self.model.silo_capacity).update_properties_node()

        if fill_percentage is not None:
            await AnalogItemNode(feed, self.model.fill_percentage).update_properties_node()
