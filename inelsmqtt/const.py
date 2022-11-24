"""Constances of inels-mqtt."""
from __future__ import annotations
from typing import Final
from enum import Enum

DISCOVERY_TIMEOUT_IN_SEC = 5

NAME = "inels-mqtt"


class Platform(Enum):
    """Entity platforms."""

    SWITCH = "switch"
    SENSOR = "sensor"
    LIGHT = "light"
    COVER = "cover"
    CLIMATE = "climate"
    BUTTON = "button"


class Element(Enum):
    """Inels element names."""

    RFSC_61 = "RFSC-61"
    RFTI_10B = "RFTI-10B"
    RFDAC_71B = "RFDAC-71B"
    RFJA_12 = "RFJA-12"
    RFATV_2 = "RFATV-2"
    RFGB_40 = "RFGB-40"
    RFKEY_40 = "RFKEY-40"
    RFSTI_11B = "RFSTI-11B"
    RFTC_10_G = "RFTC-10/G"


# device types
DEVICE_TYPE_DICT = {
    "02": Platform.SWITCH,
    "03": Platform.COVER,
    "05": Platform.LIGHT,
    "07": Platform.SWITCH,
    "09": Platform.CLIMATE,
    "10": Platform.SENSOR,
    "19": Platform.BUTTON,
    "12": Platform.SENSOR,
}

INELS_DEVICE_TYPE_DICT = {
    "02": Element.RFSC_61,
    "03": Element.RFJA_12,
    "05": Element.RFDAC_71B,
    "07": Element.RFSTI_11B,
    "09": Element.RFATV_2,
    "10": Element.RFTI_10B,
    "19": Element.RFGB_40,
    "12": Element.RFTC_10_G,
}

BATTERY = "battery"
TEMP_IN = "temp_in"
TEMP_OUT = "temp_out"
TEMPERATURE = "temperature"
CURRENT_TEMP = "current_temp"
REQUIRED_TEMP = "required_temp"
OPEN_IN_PERCENTAGE = "open_in_percentage"
RAMP_UP = "ramp_up"  # náběh
TIME_RAMP_UP = "time_ramp"  # časový náběh
TIME_RAMP_DOWN = "time_ramp_down"  # časový doběh
TEST_COMMUNICATION = "test_communication"
PULL_DOWN = "pull_down"
PULL_UP = "pull_up"
PUSH_BUTTON_DOWN = "push_button_down"
PUSH_BUTTON_UP = "push_button_up"
RELEASE_BUTTON_DOWN = "release_button_down"
RELEASE_BUTTON_UP = "relese_button_up"
SET_TIME_UP = "set_time_up"
SET_TIME_DOWN = "set_time_down"
STOP_DOWN = "stop_down"
STOP_UP = "stop_up"
STOP = "stop"
STATE = "state"
IDENTITY = "identity"
ON = "on"

STATE_OPEN = "open"
STATE_CLOSED = "closed"

COVER_SET_BYTES = {
    PULL_DOWN: "01",
    PULL_UP: "02",
    PUSH_BUTTON_DOWN: "03",
    RELEASE_BUTTON_DOWN: "04",
    PUSH_BUTTON_UP: "05",
    RELEASE_BUTTON_UP: "06",
    SET_TIME_UP: "07",
    SET_TIME_DOWN: "08",
    TEST_COMMUNICATION: "09",
}

COVER_TIME_SET_CONSTANT = 0.06577

SHUTTER_STATE_LIST = [STATE_OPEN, STATE_CLOSED]

SHUTTER_STATES = {
    "03\n01\n": STATE_OPEN,
    "03\n00\n": STATE_CLOSED,
}

SHUTTER_SET = {
    STATE_OPEN: "02 00 00",
    STATE_CLOSED: "01 00 00",
    STOP_DOWN: "03 00 00",
    STOP_UP: "05 00 00",
}

ANALOG_REGULATOR_SET_BYTES = {
    Element.RFDAC_71B.value: "01",
    RAMP_UP: "02",
    TIME_RAMP_UP: "05",
    TIME_RAMP_DOWN: "06",
    TEST_COMMUNICATION: "07",
}

DEVICE_TYPE_05_HEX_VALUES = {
    "D8\nEF\n": 0,
    "D1\n1F\n": 10,
    "C9\n4F\n": 20,
    "C1\n7F\n": 30,
    "B9\nAF\n": 40,
    "B1\nDF\n": 50,
    "AA\n0F\n": 60,
    "A2\n3F\n": 70,
    "9A\n6F\n": 80,
    "92\n9F\n": 90,
    "8A\nCF\n": 100,
}

DEVICE_TYPE_07_DATA = {STATE: [1], TEMP_OUT: [3, 2]}
DEVICE_TYPE_05_DATA = {Element.RFDAC_71B.value: [0, 1]}
DEVICE_TYPE_10_DATA = {BATTERY: [0], TEMP_IN: [2, 1], TEMP_OUT: [4, 3]}
SHUTTER_TYPE_03_DATA = {Element.RFJA_12.value: [1]}
BUTTON_TYPE_19_DATA = {STATE: [0], IDENTITY: [1]}
CLIMATE_TYPE_09_DATA = {
    OPEN_IN_PERCENTAGE: [0],
    CURRENT_TEMP: [1],
    BATTERY: [2],
    REQUIRED_TEMP: [3],
}
DEVICE_TYPE_12_DATA = {TEMPERATURE: [0], BATTERY: [2]}

BUTTON_NUMBER = {
    "01": 1,
    "02": 2,
    "04": 3,
    "08": 4,
    "16": 5,
    "32": 6,
}

BUTTON_DEVICE_AMOUNT = {Element.RFGB_40.value: 4}

FRAGMENT_DOMAIN = "fragment_domain"
FRAGMENT_SERIAL_NUMBER = "fragment_serial_number"
FRAGMENT_STATE = "fragment_state"
FRAGMENT_DEVICE_TYPE = "fragment_device_type"
FRAGMENT_UNIQUE_ID = "fragment_unique_id"

MQTT_BROKER_CLIENT_NAME = "inels-mqtt"
MQTT_DISCOVER_TOPIC = "inels/status/#"

TOPIC_FRAGMENTS = {
    FRAGMENT_DOMAIN: 0,
    FRAGMENT_STATE: 1,
    FRAGMENT_SERIAL_NUMBER: 2,
    FRAGMENT_DEVICE_TYPE: 3,
    FRAGMENT_UNIQUE_ID: 4,
}

DEVICE_CONNCTED = {
    "on\n": True,
    "off\n": False,
}

SWITCH_ON_STATE = "02\n01\n"
SWITCH_OFF_STATE = "02\n00\n"

SWITCH_ON_SET = "01\n00\n00\n"
SWITCH_OFF_SET = "02\n00\n00\n"

SWITCH_SET = {
    True: SWITCH_ON_SET,
    False: SWITCH_OFF_SET,
}

SWITCH_STATE = {
    SWITCH_ON_STATE: True,
    SWITCH_OFF_STATE: False,
}

SWITCH_ON_WITH_TEMP_SET = "01\n00\n"
SWITCH_OFF_WITH_TEMP_SET = "02\n00\n"

SWITCH_WITH_TEMP_SET = {
    True: SWITCH_ON_WITH_TEMP_SET,
    False: SWITCH_OFF_WITH_TEMP_SET,
}

SENSOR_RFTC_10_G_LOW_BATTERY = "81"

MQTT_TRANSPORTS = {"tcp", "websockets"}

MQTT_TIMEOUT: Final = "timeout"
MQTT_HOST: Final = "host"
MQTT_USERNAME: Final = "username"
MQTT_PASSWORD: Final = "password"
MQTT_PORT: Final = "port"
MQTT_CLIENT_ID: Final = "client_id"
MQTT_PROTOCOL: Final = "protocol"
MQTT_TRANSPORT: Final = "transport"
PROTO_31 = "3.1"
PROTO_311 = "3.1.1"
PROTO_5 = 5

VERSION = "0.1.0"

MANUFACTURER: Final = "ELKO EP s.r.o"
