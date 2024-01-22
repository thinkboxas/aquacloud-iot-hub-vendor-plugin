The Vendor Plugin helps vendors integrate existing sensor systems with AquaCloud standard

**AquaCloud Vendor Plugin V1.0.3** 

Define plugin template, input/output modules that contributor can be used to implement vendor plugin to get data from
sensors then convert to AquaCloud standard semantic model.

Version V1.0.3 support OpcUa driver, Feeding sensor driver, and Environment sensor driver

Plays nicely with your linters/IDE/brain.
Support of python >= 3.11
Vendor Plugin is packaged as Docker Image

**Modules**

+ OpcUa server that implemented semantic model as standard
+ Configuration parser: define mapping validation, vendor sensors structure
+ Drivers: sensor driver that implemented protocol to connect and get data from sensor

**Usage**
Pull Docker image and run

**A Simple Example**

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

**Contributing**

https://github.com/thinkboxas/aquacloud-iot-hub-vendor-plugin