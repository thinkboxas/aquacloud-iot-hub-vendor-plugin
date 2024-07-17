The Vendor Plugin helps vendors integrate existing sensor systems with AquaCloud Standard

**AquaCloud Vendor Plugin V1.0.3** 

Define plugin template, input/output modules that contributor can be used to implement vendor plugin to get data from
sensors then convert to AquaCloud Standard semantic model.

Version V1.0.3 support OpcUa driver, Feeding sensor driver, and Environment sensor driver

Plays nicely with your linters/IDE/brain.
Support of python >= 3.11
Vendor Plugin is packaged as Docker Image

**Modules**

+ OpcUa server that implemented semantic model as Standard
+ Configuration parser: define mapping validation, vendor sensors structure
+ Drivers: sensor driver that implemented protocol to connect and get data from sensor

**Flow**

 Basically, the template creates the opcua server automatically. This includes AquaCloud Standard ObjectType node such as Global, Country, etc...
 We need to define AquaCloud Standard Sensors with unit container if sensor in Unit in (driver) config file (feeding_config.json, opcua_config.json, etc..).
 Configuration parser will read config from config file and tell opcua server creates AquaCloud Standard Sensors.

 For example opcua_config.json (OpuUa driver):

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
 
 sensor_type: Opcua module will create 2 instances of "TemperatureSensorType" that was defined in Standard 
 
 sensor_name: Opcua Sensor node name
 
 mapping: mapping between AquaCloud Standard Sensors and Real Sensor. driver will get data from real sensor and use mapping and put to OpcUa Standard Sensor node

 You can create configuration file that adapts your driver, no need sames format on example and have individual ConfigParser to handle this config.

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

 **core/drivers/feeding_config_parser**

 class FeedingConfigurationParser:

    def __init__(self, config_file: str):
        self._config_file = config_file
        self._sensors: list[SensorModel] = []

    def parse_config_file(self):
        try:
            with open(self._config_file) as json_file:
                config = json.load(json_file)
                self._sensors = [SensorModel.model_validate(sensor) for sensor in config["sensors"]]
        except Exception as e:
            _logger.warning("Configuration file not found on disk!", e)

    def create_units(self) -> list[UnitModel]:
        units: dict[str, UnitModel] = {}
        for sensor in self._sensors:
            unit_id = sensor.unit_id
            if sensor.unit_id not in units:
                unit = UnitModel(
                    id=unit_id,
                    name=unit_id
                )
                units[unit_id] = unit
            standard_sensor = self._create_standard_sensor(sensor)
            standard_sensor.name = standard_sensor.__class__.__name__.replace("Model", "")
            units[unit_id].sensors.append(standard_sensor)

        return [units[key] for key in units]

    @staticmethod
    def _create_standard_sensor(sensor: SensorModel) -> BaseSensorModel:
        namespace_uri = "http://www.opcfoundation.org/UA/units/un/cefact"
        if sensor.sensor_type == FeedingSensorType.FEEDING_INTENSITY:
            model = FeedingIntensitySensorModel()
            model.feeding_intensity.engineering_units.namespace_uri = namespace_uri
            model.feeding_intensity.engineering_units.display_name = "g/s"
            model.feeding_intensity.engineering_units.description = "Gram per second"
        elif sensor.sensor_type == FeedingSensorType.FEED_SILO:
            model = FeedSiloSensorModel()
            model.feed.engineering_units.namespace_uri = namespace_uri
            model.feed.engineering_units.display_name = "kg"
            model.feed.engineering_units.description = "Kilogram"
            model.silo_capacity.engineering_units.namespace_uri = namespace_uri
            model.silo_capacity.engineering_units.display_name = "kg"
            model.silo_capacity.engineering_units.description = "Kilogram"
            model.fill_percentage.engineering_units.namespace_uri = namespace_uri
            model.fill_percentage.engineering_units.display_name = "%"
            model.fill_percentage.engineering_units.description = "Percentage"
        else:
            model = CalculatedAccumulatedFeedingSensorModel()
            model.fed_amount.engineering_units.namespace_uri = namespace_uri
            model.fed_amount.engineering_units.display_name = ""
            model.fed_amount.engineering_units.description = ""

        model.feed_type.pellet_size.engineering_units.namespace_uri = namespace_uri
        model.feed_type.pellet_size.engineering_units.display_name = "mm"
        model.feed_type.pellet_size.engineering_units.description = "Millimeter"
        model.feed_type.mass_per_pellet.engineering_units.namespace_uri = namespace_uri
        model.feed_type.mass_per_pellet.engineering_units.display_name = "g"
        model.feed_type.mass_per_pellet.engineering_units.description = "Gram"

        return model

    def create_mapping(self) -> dict[str, list[MappingModel]]:
        mapping: dict[str, list[MappingModel]] = {}
        for sensor in self._sensors:
            sensor_name = sensor.sensor_type.replace("Type", "")
            for key in sensor.mapping:
                mapping_key = sensor.unit_id + ":" + sensor.mapping[key] + ":" + sensor_name
                mapping_model = MappingModel(
                    unit_id=sensor.unit_id,
                    sensor=sensor_name,
                    measurement=key
                )

                if mapping_key not in mapping:
                    mapping[mapping_key] = []

                mapping[mapping_key].append(mapping_model)

            # make default timestamp mapping
            mapping_key = sensor.unit_id + ":" + "local_timestamp" + ":" + sensor_name
            mapping[mapping_key] = [
                MappingModel(
                    unit_id=sensor.unit_id,
                    sensor=sensor_name,
                    measurement="LocalTimestamp"
                )
            ]

        return mapping

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

 **core/drivers/environment_config_parser**

class EnvironmentConfigurationParser:

    def __init__(self, config_file: str):
        self._config_file = config_file
        self._sensors: list[SensorModel] = []
        self._standard_sensors: list[BaseSensorModel] = []

    def parse_config_file(self):
        try:
            with open(self._config_file) as json_file:
                config = json.load(json_file)
                self._sensors = [SensorModel.model_validate(sensor) for sensor in config["sensors"]]
        except Exception as e:
            _logger.warning("Configuration file not found on disk!", e)

    def create_units(self) -> list[UnitModel]:
        units: dict[str, UnitModel] = {}
        for sensor in self._sensors:
            standard_sensor = self._create_standard_sensor(sensor)

            if sensor.type == "site":
                self._standard_sensors.append(standard_sensor)
            else:
                unit_id = sensor.unit_id
                if sensor.unit_id not in units:
                    unit = UnitModel(
                        id=unit_id,
                        name=unit_id
                    )
                    units[unit_id] = unit
                units[unit_id].sensors.append(standard_sensor)

        return [units[key] for key in units]

    def get_standard_sensors(self) -> list[BaseSensorModel]:
        return self._standard_sensors

    @staticmethod
    def _create_standard_sensor(sensor: SensorModel) -> BaseSensorModel:
        model: BaseSensorModel = BaseSensorModel()

        depth = "dynamic_depth"
        if sensor.depth is not None:
            model.position.depth = sensor.depth
            depth = str(int(sensor.depth)) + "m"

        namespace_uri = "http://www.opcfoundation.org/UA/units/un/cefact"
        if sensor.sensor_type == EnvironmentSensorType.OXYGEN_SATURATION:
            model = OxygenSaturationSensorModel()
            model.name = "OxygenSaturation_" + depth
            model.oxygen_saturation.engineering_units.namespace_uri = namespace_uri
            model.oxygen_saturation.engineering_units.display_name = "%"
            model.oxygen_saturation.engineering_units.description = "Percentage"
        elif sensor.sensor_type == EnvironmentSensorType.OXYGEN_CONCENTRATION:
            model = OxygenConcentrationSensorModel()
            model.name = "OxygenConcentration_" + depth
            model.oxygen_concentration.engineering_units.namespace_uri = namespace_uri
            model.oxygen_concentration.engineering_units.display_name = "mg/l"
            model.oxygen_concentration.engineering_units.description = "Milligram per liter"
            model.salinity.engineering_units.namespace_uri = namespace_uri
            model.salinity.engineering_units.display_name = "ppt"
            model.salinity.engineering_units.description = "Parts per thousand"
        elif sensor.sensor_type == EnvironmentSensorType.TEMPERATURE:
            model = TemperatureSensorModel()
            model.name = "Temperature_" + depth
            model.temperature.engineering_units.namespace_uri = namespace_uri
            model.temperature.engineering_units.display_name = "C°"
            model.temperature.engineering_units.description = "Celsius"
        elif sensor.sensor_type == EnvironmentSensorType.SALINITY:
            model = SalinitySensorModel()
            model.name = "Salinity_" + depth
            model.salinity.engineering_units.namespace_uri = namespace_uri
            model.salinity.engineering_units.display_name = "ppt"
            model.salinity.engineering_units.description = "Parts per thousand"
        elif sensor.sensor_type == EnvironmentSensorType.SEA_CURRENT:
            model = SeaCurrentSensorModel()
            model.name = "SeaCurrent_" + depth
            model.direction.engineering_units.namespace_uri = namespace_uri
            model.direction.engineering_units.display_name = "Absolute North"
            model.direction.engineering_units.description = "Absolute direction in degrees"

            model.speed.engineering_units.namespace_uri = namespace_uri
            model.speed.engineering_units.display_name = "cm/s"
            model.speed.engineering_units.description = "Centimeter per second"
        elif sensor.sensor_type == EnvironmentSensorType.NTU:
            model = NTUSensorModel()
            model.name = "NTU_" + depth
            model.ntu.engineering_units.namespace_uri = namespace_uri
            model.ntu.engineering_units.display_name = "NTU"
            model.ntu.engineering_units.description = "Nephelometric Turbidity Units"
        elif sensor.sensor_type == EnvironmentSensorType.FTU:
            model = FTUSensorModel()
            model.name = "FTU_" + depth
            model.ftu.engineering_units.namespace_uri = namespace_uri
            model.ftu.engineering_units.display_name = "FTU"
            model.ftu.engineering_units.description = "Formazin Turbidity Units"
        elif sensor.sensor_type == EnvironmentSensorType.PH:
            model = PHSensorModel()
            model.name = "PH_" + depth
            model.ph.engineering_units.namespace_uri = namespace_uri
            model.ph.engineering_units.display_name = "pH"
            model.ph.engineering_units.description = "pH"
        elif sensor.sensor_type == EnvironmentSensorType.LIGHT:
            model = LightSensorModel()
            model.name = "Light_" + depth
            model.lux.engineering_units.namespace_uri = namespace_uri
            model.lux.engineering_units.display_name = "lux"
            model.lux.engineering_units.description = "Lumen per square meter"

        return model

    @staticmethod
    def get_sensor_name(sensor: SensorModel):
        depth = "dynamic_depth"
        if sensor.depth is not None:
            depth = str(int(sensor.depth)) + "m"
        if sensor.sensor_type == EnvironmentSensorType.OXYGEN_SATURATION:
            return "OxygenSaturation_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.OXYGEN_CONCENTRATION:
            return "OxygenConcentration_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.TEMPERATURE:
            return "Temperature_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.SALINITY:
            return "Salinity_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.SEA_CURRENT:
            return "SeaCurrent_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.NTU:
            return "NTU_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.FTU:
            return "FTU_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.PH:
            return "PH_" + depth
        elif sensor.sensor_type == EnvironmentSensorType.LIGHT:
            return "Light_" + depth

    def create_mapping(self) -> dict[str, list[MappingModel]]:
        mapping: dict[str, list[MappingModel]] = {}
        for sensor in self._sensors:
            sensor_name = self.get_sensor_name(sensor)
            for key in sensor.mapping:

                if sensor.type == "site":
                    mapping_key = "site:" + sensor.mapping[key] + ":" + sensor_name
                else:
                    mapping_key = sensor.unit_id + ":" + sensor.mapping[key] + ":" + sensor_name

                mapping_model = MappingModel(
                    unit_id=sensor.unit_id,
                    sensor=sensor_name,
                    measurement=key
                )

                if mapping_key not in mapping:
                    mapping[mapping_key] = []

                mapping[mapping_key].append(mapping_model)

            # make default timestamp mapping
            if sensor.type == "site":
                mapping_key = "site:" + "local_timestamp" + ":" + sensor_name
            else:
                mapping_key = sensor.unit_id + ":" + "local_timestamp" + ":" + sensor_name
            mapping[mapping_key] = [
                MappingModel(
                    unit_id=sensor.unit_id,
                    sensor=sensor_name,
                    measurement="LocalTimestamp"
                )
            ]

        return mapping

**Contributing**

https://github.com/thinkboxas/aquacloud-iot-hub-vendor-plugin
