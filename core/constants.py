MARIA_DB_SENSOR_TABLE = "sensor"
MARIA_DB_SENSOR_DATA_CHANNEL_TABLE = "sensor_data_channel"
MARIA_DB_SENSOR_DATA_TABLE = "sensor_data"


class ServerType:
    OPC_UA_TYPE = "OPC-UA"
    MODBUS_TCP_TYPE = "MODBUS_TCP"
    VENDOR_SYSTEM_TYPE = "VENDOR_SYSTEM_TYPE"
    MARIADB_TYPE = "MARIA_DB",
    PIS_FEEDING_TYPE = "PIS_FEEDING"
    PIS_ENVIRONMENT_TYPE = "PIS_ENVIRONMENT"


class EnvironmentSensorType:
    OXYGEN_SATURATION_SENSOR = "OxygenSaturationSensorType"
    OXYGEN_CONCENTRATION_SENSOR = "OxygenConcentrationSensorType"
    TEMPERATURE_SENSOR = "TemperatureSensorType"
    SALINITY_SENSOR = "SalinitySensorType"
    SEA_CURRENT_SENSOR = "SeaCurrentSensorType"
    NTU_SENSOR = "NTUSensorType"
    FTU_SENSOR = "FTUSensorType"
    PH_SENSOR = "PHSensorType"
    LIGHT_SENSOR = "LightSensorType"


# CONFIG_PATH = '/opt/piscada-environment-vendor-plugin/config'
CONFIG_PATH = 'config'
FILES_PATH = 'files'
