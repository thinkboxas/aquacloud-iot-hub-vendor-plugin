import logging
from typing import Any

from asyncua import Server, ua, Node
from asyncua.ua import String, Int16


_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


class OPCUAServer:
    def __init__(
            self,
            endpoint: str,
            name: str,
            uri: str,
            xml_file_path: str
    ):
        self._server: Server = Server()
        self._xml_file_path: str = xml_file_path
        self._uri: str = uri
        self._ns: int = 2
        self._server.set_endpoint(endpoint)
        self._server.set_server_name(name)
        self._server.set_security_policy([
            ua.SecurityPolicyType.NoSecurity,
            ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
            ua.SecurityPolicyType.Basic256Sha256_Sign])

        self._objects_node: Node = self._server.get_objects_node()

    async def init(self) -> bool:
        await self._server.init()
        self._ns = await self._server.register_namespace(self._uri)
        return await self._import_nodeset_from_xml_file(self._xml_file_path)

    async def _import_nodeset_from_xml_file(self, xml_file_path: str) -> bool:
        try:
            await self._server.import_xml(path=xml_file_path)
            return True
        except Exception as e:
            _logger.warning(e)
        return False

    async def __aenter__(self):
        status = await self.init()
        if status is True:
            if status is True:
                await self._server.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        await self._server.stop()

    def get_node(self, identifier: str) -> Node | None:
        node_id = ua.NodeId(String(identifier), Int16(self._ns))
        try:
            return self._server.get_node(node_id)
        except Exception as e:
            _logger.warning("Node not found", e)
            return None

    def get_namespace(self):
        return self._ns

    def get_objects_node(self):
        return self._objects_node



