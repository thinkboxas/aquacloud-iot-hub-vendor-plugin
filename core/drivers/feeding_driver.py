import os
import time

from core.constants import CONFIG_PATH
from core.drivers.base_driver import BaseDriver
from core.drivers.feeding_config_parser import FeedingConfigurationParser


POLL_TIME_INTERVAL = int(os.getenv("TIME_INTERVAL", 10))


class FeedingDriver(BaseDriver):
    def parse_config(self):
        config_path_file = os.path.join(CONFIG_PATH, "config.json")
        config_parser = FeedingConfigurationParser(config_path_file)
        config_parser.parse_config_file()
        self.units = config_parser.create_units()
        self.mapping = config_parser.create_mapping()

    def _poll_data(self):
        pass

    def subscribe(self):
        while self.is_starting is True:
            self._poll_data()
            time.sleep(POLL_TIME_INTERVAL)

    async def start(self):
        self.is_starting = True
        self.parse_config()
        await self.create_unit_nodes()

    def stop(self):
        self.is_starting = False
