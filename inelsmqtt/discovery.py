"""Discovery class handle find all device in broker and create devices."""
import logging

from inelsmqtt import InelsMqtt
from inelsmqtt.devices import Device


_LOGGER = logging.getLogger(__name__)


class InelsDiscovery:
    """Handling discovery mqtt topics from broker."""

    def __init__(self, mqtt: InelsMqtt) -> None:
        """Initilize inels mqtt discovery"""
        self.__mqtt = mqtt
        self.__devices: list[Device] = []

    def discovery(self) -> list[Device]:
        """Discover and create device list

        Returns:
            list[Device]: List of Device object
        """
        self.__devices = [
            Device(self.__mqtt, item[0], item[1]) for item in self.__mqtt.discover_all()
        ]

        _LOGGER.info("Discovered %s devices", len(self.__devices))

        return self.__devices
