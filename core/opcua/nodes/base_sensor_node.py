from asyncua import Node, ua

from aquacloud_common.models.sensor.base_sensor import BaseSensorModel
from core.opcua.nodes.base_node import Base
from core.opcua.nodes.feed_type_node import FeedTypeNode
from utilities.opcua import update_external_references_node, update_position_node


FEEDING_SENSOR_MODEL = [
    "FeedingIntensitySensorModel",
    "CalculatedAccumulatedFeedingSensorModel",
    "FeedSiloSensorModel"
]


class BaseSensorNode(Base):
    def __init__(self, model: BaseSensorModel, ns: int, parent_node: Node, path: str = ""):
        super().__init__(model, ns, parent_node, model.name, path)
        self.model = model

    async def update_object_properties_node(self):
        properties = await self.node.get_properties()
        for p in properties:
            if p.nodeid.Identifier == (self.identifier + ".SerialNumber"):
                await p.set_value(ua.String(self.model.serial_number))
            elif p.nodeid.Identifier == (self.identifier + ".Manufacturer"):
                await p.set_value(ua.LocalizedText(self.model.manufacturer))
            elif p.nodeid.Identifier == (self.identifier + ".Model"):
                await p.set_value(ua.LocalizedText(self.model.model))
            elif p.nodeid.Identifier == (self.identifier + ".ProductCode"):
                await p.set_value(ua.String(self.model.product_code))

    async def update_analog_item_variables_node(self):
        pass

    async def init(self):
        await super().init()

        # update properties node:
        await self.update_object_properties_node()
        #
        # update analog item variables node:
        await self.update_analog_item_variables_node()

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

        # update FeedType if the sensor is feeding sensor:
        if self.model.name in FEEDING_SENSOR_MODEL:
            try:
                feed_type_node = await self.node.get_child(str(self.ns) + ":" + "FeedType")
                if feed_type_node is not None:
                    feed_type_node = FeedTypeNode(feed_type_node, self.model.feed_type)
                    await feed_type_node.update_variables_node()
            except Exception as e:
                print(e)

