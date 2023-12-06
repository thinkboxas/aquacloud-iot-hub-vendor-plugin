import os
import random
import time
from datetime import datetime

from aquacloud_common.models.organization.unit import UnitModel
from aquacloud_common.models.sensor.feeding.calculated_accumulated_feeding_sensor import \
    CalculatedAccumulatedFeedingSensorModel
from aquacloud_common.models.sensor.feeding.feed_silo_sensor import FeedSiloSensorModel
from aquacloud_common.models.sensor.feeding.feeding_intensity_sensor import FeedingIntensitySensorModel
from core.constants import CONFIG_PATH
from core.drivers.base_driver import BaseDriver
from core.drivers.feeding_config_parser import FeedingConfigurationParser


POLL_TIME_INTERVAL = int(os.getenv("TIME_INTERVAL", 600))


class FeedingDriver(BaseDriver):
    def parse_config(self):
        config_path_file = os.path.join(CONFIG_PATH, "config.json")
        config_parser = FeedingConfigurationParser(config_path_file)
        config_parser.parse_config_file()
        self.units = config_parser.create_units()
        self.mapping = config_parser.create_mapping()

    async def _simulate_unit_feeding_sensor_data(self, unit: UnitModel):
        timestamp = time.time()
        timestamp = datetime.fromtimestamp(timestamp)
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        for sensor in unit.sensors:
            if sensor.__class__ == CalculatedAccumulatedFeedingSensorModel:
                accumulated_feed_today = random.uniform(0, 100)
                tag = unit.id + ":" + unit.id + "_accumulated_feed_today" + ":" + sensor.name
                await self.on_data_change(tag, accumulated_feed_today, timestamp)
            elif sensor.__class__ == FeedingIntensitySensorModel:
                intensity = random.uniform(0, 100)
                tag = unit.id + ":" + unit.id + "_intensity" + ":" + sensor.name
                await self.on_data_change(tag, intensity, timestamp)
            elif sensor.__class__ == FeedSiloSensorModel:
                feed = random.uniform(0, 100)
                silo_capacity = random.uniform(0, 100)
                fill_percentage = random.uniform(0, 100)
                tag = unit.id + ":" + unit.id + "_accumulated_feed" + ":" + sensor.name
                await self.on_data_change(tag, feed, timestamp)
                tag = unit.id + ":" + unit.id + "_silo_capacity" + ":" + sensor.name
                await self.on_data_change(tag, silo_capacity, timestamp)
                tag = unit.id + ":" + unit.id + "_fill_percentage" + ":" + sensor.name
                await self.on_data_change(tag, fill_percentage, timestamp)

    async def _poll_data(self):
        for unit in self.units:
            await self._simulate_unit_feeding_sensor_data(unit)

    async def subscribe(self):
        await self._poll_data()
        # while self.is_starting is True:
        #     await self._poll_data()
        #     time.sleep(POLL_TIME_INTERVAL)

    async def start(self):
        self.is_starting = True
        self.parse_config()
        await self.create_unit_nodes()
        await self.subscribe()

    def stop(self):
        self.is_starting = False
