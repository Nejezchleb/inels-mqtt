"""Discovery class handle find all device in broker and create devices."""
import logging
from typing import Any

from inelsmqtt import InelsMqtt
from inelsmqtt.devices import Device
from inelsmqtt.devices import sensor, light, switch
from inelsmqtt.const import (
    Platform,
    DEVICE_TYPE_DICT,
    TOPIC_FRAGMENTS,
    FRAGMENT_DEVICE_TYPE,
)


_LOGGER = logging.getLogger(__name__)


class InelsDiscovery(object):
    """Handling discovery mqtt topics from broker."""

    def __init__(self, mqtt: InelsMqtt) -> None:
        """Initilize inels mqtt discovery"""
        self.__mqtt = mqtt
        self.__devices: list[Any] = []
        self.__coordinators: list[str] = []
        self.__coordinators_with_devices: dict[str, list[Any]] = {}

    @property
    def coordinators(self) -> list[str]:
        """Coordinators list

        Returns:
            _type_: list of coordinator serial numbers
        """
        return self.__coordinators

    @property
    def devices(self) -> list[Any]:
        """List of devices

        Returns:
            list[Device]: all devices handled with discovery object
        """
        return self.__devices

    def discovery(self) -> dict[str, list[Any]]:
        """Discover and create device list

        Returns:
            list[Device]: List of Device object
        """
        devs = self.__mqtt.discovery_all()

        for item in devs:
            fragments = item.split("/")

            # defragmentace
            dev_type: Platform = DEVICE_TYPE_DICT[
                fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]
            ]

            dev = None

            if dev_type == Platform.SWITCH:
                dev = switch.Switch(self.__mqtt, item)
            elif dev_type == Platform.LIGHT:
                dev = light.Light(self.__mqtt, item)
            elif dev_type == Platform.SENSOR:
                dev = sensor.Sensor(self.__mqtt, item)
            else:
                dev = Device(self.__mqtt, item)

            self.__devices.append(dev)

        for item in self.__devices:
            if item.parent_id not in self.__coordinators:
                self.__coordinators.append(item.parent_id)
                self.__coordinators_with_devices[item.parent_id] = []

            self.__coordinators_with_devices[item.parent_id].append(item)

        _LOGGER.info("Discovered %s devices", len(self.__devices))

        return self.__devices
