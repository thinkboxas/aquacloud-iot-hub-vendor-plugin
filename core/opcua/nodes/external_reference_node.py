from asyncua import Node

from aquacloud_common.models.common.external_reference import ExternalReferenceModel
from core.opcua.nodes.base_node import Base


class ExternalReference(Base):
    def __init__(self, model: ExternalReferenceModel, ns: int, parent_node: Node, path: str):
        b_name = model.type + "(" + model.reference + ")"
        super().__init__(model, ns, parent_node, b_name, path)
        self.model = model
        self.identifier = path + "|ExternalReference|" + self.model.type + "|" + self.model.reference

    async def update_object_properties_node(self):
        properties = await self.node.get_properties()
        for p in properties:
            if p.nodeid.Identifier == (self.identifier + ".Type"):
                await p.set_value(self.model.type)
            elif p.nodeid.Identifier == (self.identifier + ".Reference"):
                await p.set_value(self.model.reference)

    async def init(self):
        await super().init()