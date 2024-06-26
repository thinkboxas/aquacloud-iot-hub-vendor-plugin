import asyncio
import logging
import os

from core.drivers.environment_driver import EnvironmentDriver
from core.drivers.feeding_driver import FeedingDriver
from core.drivers.opcua.opcua_driver import OpcuaDriver
from core.opcua.opcua_server import OPCUAServer

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

ENDPOINT = os.getenv("ENDPOINT", "opc.tcp://127.0.0.1:4841")


async def start_opcua_server():
    xml_file_path = os.path.join("config", "AquaCloudStandardNodeSet.xml")
    async with OPCUAServer(
            ENDPOINT,
            "AquaCloud Vendor Plugin",
            "http://aquacloud.iothub.thinkbox.no",
            xml_file_path
    ) as opcua_server:
        # driver = FeedingDriver(opcua_server)
        # driver = EnvironmentDriver(opcua_server)
        driver = OpcuaDriver(opcua_server)
        await driver.start()
        await asyncio.sleep(10)
        while True:
            await asyncio.sleep(1)


if __name__ == '__main__':
    asyncio.run(start_opcua_server())