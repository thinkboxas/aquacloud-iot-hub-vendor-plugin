from asyncua import Node

from aquacloud_common.models.organization.unit import UnitModel
from aquacloud_common.models.sensor.feeding.calculated_accumulated_feeding_sensor import \
    CalculatedAccumulatedFeedingSensorModel
from aquacloud_common.models.sensor.feeding.feed_silo_sensor import FeedSiloSensorModel
from aquacloud_common.models.sensor.feeding.feeding_intensity_sensor import FeedingIntensitySensorModel
from core.opcua.nodes.base_node import Base
from core.opcua.nodes.base_sensor_node import BaseSensorNode
from core.opcua.nodes.calculated_accumulated_deeding_sensor_node import CalculatedAccumulatedFeedingSensorNode
from core.opcua.nodes.feed_silo_sensor_node import FeedSiloSensorNode
from core.opcua.nodes.feeding_intensity_sensor_node import FeedingIntensitySensorNode
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
            class_name = sensor.__class__
            sensor_node = BaseSensorNode(sensor, self.ns, sensors_node, self.identifier)
            if class_name == CalculatedAccumulatedFeedingSensorModel:
                s = CalculatedAccumulatedFeedingSensorModel.model_validate(sensor.model_dump())
                sensor_node = CalculatedAccumulatedFeedingSensorNode(s, self.ns, sensors_node, self.identifier)
            elif class_name == FeedingIntensitySensorModel:
                s = FeedingIntensitySensorModel.model_validate(sensor.model_dump())
                sensor_node = FeedingIntensitySensorNode(s, self.ns, sensors_node, self.identifier)
            elif class_name == FeedSiloSensorModel:
                s = FeedSiloSensorModel.model_validate(sensor.model_dump())
                sensor_node = FeedSiloSensorNode(s, self.ns, sensors_node, self.identifier)

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

