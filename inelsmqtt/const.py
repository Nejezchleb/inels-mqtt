"""Constances of inels-mqtt."""
from __future__ import annotations

from typing import Final


NAME = "inels-mqtt"

SWITCH = "switch"
LIGHT = "light"

# device types
DEVICE_TYPE_DICT = {"01": SWITCH}

DISCOVERY_TIMEOUT_IN_SEC = 5

FRAGMENT_DOMAIN = "fragment_domain"
FRAGMENT_SERIAL_NUMBER = "fragment_serial_number"
FRAGMENT_STATE = "fragment_state"
FRAGMENT_DEVICE_TYPE = "fragment_device_type"
FRAGMENT_UNIQUE_ID = "fragment_unique_id"

MQTT_BROKER_CLIENT_NAME = "inels-mqtt"
MQTT_DISCOVER_TOPIC = "inels/#"

TOPIC_FRAGMENTS = {
    FRAGMENT_DOMAIN: 0,
    FRAGMENT_SERIAL_NUMBER: 1,
    FRAGMENT_STATE: 2,
    FRAGMENT_DEVICE_TYPE: 3,
    FRAGMENT_UNIQUE_ID: 4,
}

SWITCH_ON = "FF\\n50\\n32\\nAC\\n"
SWITCH_OFF = "FF\\nFF\\nFF\\nFF\\n"

SWITCH_STATE = {
    SWITCH_ON: True,
    SWITCH_OFF: False,
}

LIGHT_ON = "Aadfadfadf"
LIGHT_OFF = "adfwerafad"

DEVICE_PLATFORMS = {
    SWITCH: {SWITCH_ON: True, SWITCH_OFF: False},
    LIGHT: {LIGHT_ON: True, LIGHT_OFF: False},
}

MQTT_TIMEOUT: Final = "timeout"
MQTT_HOST: Final = "host"
MQTT_USERNAME: Final = "username"
MQTT_PASSWORD: Final = "password"
MQTT_PORT: Final = "port"
MQTT_CLIENT_ID: Final = "client_id"
MQTT_PROTOCOL: Final = "protocol"
PROTO_31 = "3.1"
PROTO_311 = "3.1.1"
PROTO_5 = 5

VERSION = "0.0.1"
