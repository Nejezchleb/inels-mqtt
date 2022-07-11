"""Discovery class handle find all device in broker and create devices."""
import logging

from inelsmqtt import InelsMqtt
from inelsmqtt.devices import Device


_LOGGER = logging.getLogger(__name__)


class InelsDiscovery(object):
    """Handling discovery mqtt topics from broker."""

    def __init__(self, mqtt: InelsMqtt) -> None:
        """Initilize inels mqtt discovery"""
        self.__mqtt = mqtt
        self.__devices: list[Device] = []

    @property
    def devices(self) -> list[Device]:
        """List of devices

        Returns:
            list[Device]: all devices handled with discovery object
        """
        return self.__devices

    def discovery(self) -> list[Device]:
        """Discover and create device list

        Returns:
            list[Device]: List of Device object
        """
        devs = self.__mqtt.discovery_all()

        self.__devices = [Device(self.__mqtt, item, devs[item]) for item in devs]

        _LOGGER.info("Discovered %s devices", len(self.__devices))

        return self.__devices
