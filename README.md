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

**Flow**

 Basically, the template creates the standard opcua server automatically include AquaStandard ObjectType node such as Global, Country, etc...
 We need to define AquaStandard Sensors with unit container if sensor in Unit in (driver) config file (feeding_config.json, opcua_config.json, etc..).
 Configuration parser will read config from config file and tell opcua server create AquaStandard Sensors.

For example: 
 
 **opcua_config.json (OpuUa driver):**

 "sensors": [

      {
        "sensor_type": "TemperatureSensorType",
        "sensor_name": "TemperatureSensor_2",
        "mapping": {
          "Temperature": {"ns": 4,"i": 5}
        }
      },
      {
        "sensor_type": "TemperatureSensorType",
        "sensor_name": "TemperatureSensor_1",
        "mapping": {
          "Temperature": {"ns": 4,"i": 6}
        }

 ]
 
 sensor_type: Opcua module will create 2 instances of "TemperatureSensorType" that defined in Standard 
 sensor_name: Opcua Sensor node name
 mapping: mapping between AquaStandard Sensors and Real Sensor. driver will get data from real sensor and use mapping and put to Opc Ua Standard Sensor node

 You can create config file that adapt with your driver, no need same format in example and have individual ConfigParser to handle this config.

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

**1. Feeding Driver example**

 class FeedingDriver(BaseDriver):

     def parse_config(self):
         config_path_file = os.path.join(CONFIG_PATH, "feeding_config.json")
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
 
             timestamp_tag = unit.id + ":" + "local_timestamp" + ":" + sensor.name
             await self.on_data_change(timestamp_tag, timestamp, timestamp)
 
     async def _poll_data(self):
         for unit in self.units:
             await self._simulate_unit_feeding_sensor_data(unit)
 
     async def subscribe(self):
         while self.is_starting is True:
             await self._poll_data()
             time.sleep(POLL_TIME_INTERVAL)
 
     async def start(self):
         self.is_starting = True
         self.parse_config()
         await self.create_unit_nodes()
 
         worker_thread = threading.Thread(target=asyncio.run, args=(self.subscribe(),))
         worker_thread.start()
 
         # asyncio.get_event_loop().create_task(self.subscribe())
 
     def stop(self):
         self.is_starting = False

 **config/feeding_config.json**
 
{
  
  "sensors": [

    {
      "type": "unit",
      "unit_id": "unit_001",
      "sensor_type": "FeedingIntensitySensorType",
      "mapping": {
        "FeedingIntensity": "unit_001_intensity"
      }
    },
    {
      "type": "unit",
      "unit_id": "unit_001",
      "sensor_type": "CalculatedAccumulatedFeedingSensorType",
      "mapping": {
        "FedAmount": "unit_001_accumulated_feed_today"
      }
    }
 }

**2. Environment driver example**

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

**config/env_config.json**

{
  
"sensors": [

    {
      "type": "site",
      "unit_id": "",
      "sensor_type": "OxygenSaturationSensorType",
      "mapping": {
        "OxygenSaturation": "site_001_oxygen_saturation",
        "Depth": "depth"
      }
    },
    {
      "type": "site",
      "unit_id": "",
      "depth": 5,
      "sensor_type": "OxygenSaturationSensorType",
      "mapping": {
        "OxygenSaturation": "site_001_oxygen_saturation"
      }
    }
  ]

}

**Contributing**

https://github.com/thinkboxas/aquacloud-iot-hub-vendor-plugin
