import asyncio
import os
import random
import threading
import time
from datetime import datetime

from aquacloud_common.models.organization.unit import UnitModel
from aquacloud_common.models.sensor.base_sensor import BaseSensorModel
from aquacloud_common.models.sensor.environment.ftu_sensor import FTUSensorModel
from aquacloud_common.models.sensor.environment.light_sensor import LightSensorModel
from aquacloud_common.models.sensor.environment.ntu_sensor import NTUSensorModel
from aquacloud_common.models.sensor.environment.oxygen_concentration_sensor import OxygenConcentrationSensorModel
from aquacloud_common.models.sensor.environment.oxygen_saturation_sensor import OxygenSaturationSensorModel
from aquacloud_common.models.sensor.environment.ph_sensor import PHSensorModel
from aquacloud_common.models.sensor.environment.salinity_sensor import SalinitySensorModel
from aquacloud_common.models.sensor.environment.sea_current_sensor import SeaCurrentSensorModel
from aquacloud_common.models.sensor.environment.temperature_sensor import TemperatureSensorModel
from core.constants import CONFIG_PATH
from core.drivers.base_driver import BaseDriver
from core.drivers.environment_config_parser import EnvironmentConfigurationParser

POLL_TIME_INTERVAL = int(os.getenv("TIME_INTERVAL", 3))


class EnvironmentDriver(BaseDriver):
    def parse_config(self):
        config_path_file = os.path.join(CONFIG_PATH, "env_config.json")
        config_parser = EnvironmentConfigurationParser(config_path_file)
        config_parser.parse_config_file()
        self.units = config_parser.create_units()
        self.mapping = config_parser.create_mapping()
        self.sensors = config_parser.get_standard_sensors()

    async def _notify_data_change(self, sensor: BaseSensorModel, timestamp: str, unit_id: str = ""):
        prefix_tag = "site" + ":" + "site_001"
        if unit_id != "":
            prefix_tag = unit_id + ":" + "site_001_" + unit_id

        if sensor.__class__ == OxygenSaturationSensorModel:
            oxygen_saturation = random.uniform(0, 100)
            tag = prefix_tag + "_oxygen_saturation" + ":" + sensor.name
            await self.on_data_change(tag, oxygen_saturation, timestamp)
        elif sensor.__class__ == OxygenConcentrationSensorModel:
            oxygen_concentration = random.uniform(0, 100)
            tag = prefix_tag + "_oxygen_concentration" + ":" + sensor.name
            await self.on_data_change(tag, oxygen_concentration, timestamp)

            salinity = random.uniform(0, 100)
            tag = prefix_tag + "_salinity" + ":" + sensor.name
            await self.on_data_change(tag, salinity, timestamp)
        elif sensor.__class__ == TemperatureSensorModel:
            temperature = random.uniform(0, 100)
            tag = prefix_tag + "_temperature" + ":" + sensor.name
            await self.on_data_change(tag, temperature, timestamp)
        elif sensor.__class__ == SalinitySensorModel:
            salinity = random.uniform(0, 100)
            tag = prefix_tag + "_salinity" + ":" + sensor.name
            await self.on_data_change(tag, salinity, timestamp)
        elif sensor.__class__ == SeaCurrentSensorModel:
            direction = random.uniform(0, 100)
            tag = prefix_tag + "_direction" + ":" + sensor.name
            await self.on_data_change(tag, direction, timestamp)

            speed = random.uniform(0, 100)
            tag = prefix_tag + "_speed" + ":" + sensor.name
            await self.on_data_change(tag, speed, timestamp)
        elif sensor.__class__ == NTUSensorModel:
            ntu = random.uniform(0, 100)
            tag = prefix_tag + "_ntu" + ":" + sensor.name
            await self.on_data_change(tag, ntu, timestamp)
        elif sensor.__class__ == FTUSensorModel:
            ftu = random.uniform(0, 100)
            tag = prefix_tag + "_ftu" + ":" + sensor.name
            await self.on_data_change(tag, ftu, timestamp)
        elif sensor.__class__ == PHSensorModel:
            ph = random.uniform(0, 100)
            tag = prefix_tag + "_ph" + ":" + sensor.name
            await self.on_data_change(tag, ph, timestamp)
        elif sensor.__class__ == LightSensorModel:
            lux = random.uniform(0, 100)
            tag = prefix_tag + "_lux" + ":" + sensor.name
            await self.on_data_change(tag, lux, timestamp)

        if unit_id == "":
            timestamp_tag = "site:" + "local_timestamp" + ":" + sensor.name
        else:
            timestamp_tag = unit_id + ":" + "local_timestamp" + ":" + sensor.name
        await self.on_data_change(timestamp_tag, timestamp, timestamp)

    async def _simulate_site_env_sensor_data(self, timestamp: str):
        for sensor in self.sensors:
            await self._notify_data_change(sensor, timestamp)

    async def _simulate_unit_env_sensor_data(self, unit: UnitModel, timestamp: str):
        for sensor in unit.sensors:
            await self._notify_data_change(sensor, timestamp, unit.id)

    async def _simulate_sensor_depth_data(self, timestamp: str):
        for key in self.mapping:
            mapping = self.mapping[key]
            for m in mapping:
                if m.measurement == "Depth":
                    depth = random.uniform(0, 100)
                    if m.unit_id != "":
                        tag = m.unit_id + ":depth" + ":" + m.sensor
                    else:
                        tag = "site:depth" + ":" + m.sensor
                    await self.on_data_change(tag, depth, timestamp)

    async def _poll_data(self):
        timestamp = time.time()
        timestamp = datetime.fromtimestamp(timestamp)
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        await self._simulate_site_env_sensor_data(timestamp)
        await self._simulate_sensor_depth_data(timestamp)
        for unit in self.units:
            await self._simulate_unit_env_sensor_data(unit, timestamp)

    async def subscribe(self):
        while self.is_starting is True:
            await self._poll_data()
            time.sleep(POLL_TIME_INTERVAL)

    async def start(self):
        self.is_starting = True
        self.parse_config()
        await self.create_unit_nodes()
        await self.create_sensors()

        worker_thread = threading.Thread(target=asyncio.run, args=(self.subscribe(),))
        worker_thread.start()

        # asyncio.get_event_loop().create_task(self.subscribe())

    def stop(self):
        self.is_starting = False
