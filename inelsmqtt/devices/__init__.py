"""Class handle base info about device."""
import logging
import json

from inelsmqtt import InelsMqtt
from inelsmqtt.const import (
    DEVICE_TYPE_DICT,
    FRAGMENT_DOMAIN,
    TOPIC_FRAGMENTS,
    FRAGMENT_DEVICE_TYPE,
    FRAGMENT_SERIAL_NUMBER,
    FRAGMENT_UNIQUE_ID,
)

_LOGGER = logging.getLogger(__name__)


class Device(object):
    """Carry basic device stuff

    Args:
        object (_type_): default object it is new style of python class coding
    """

    def __init__(
        self,
        mqtt: InelsMqtt,
        state_topic: str,
        payload: str,
        title: str = None,
    ) -> None:
        """Initialize instance of device

        Args:
            mqtt (InelsMqtt): instance of mqtt broker
            status_topic (str): String format of status topic
            set_topic (str): Sring format of set topic
            payload (str): Value carried inside of the topic
            title (str, optional): Formal name of the device. When None
            then will be same as unique_id. Defaults to None.
        """
        fragments = state_topic.split("/")

        self.__mqtt = mqtt
        self.__device_type = DEVICE_TYPE_DICT[
            fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]
        ]
        self.__unique_id = fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]
        self.__parent_id = fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]
        self.__state_topic = state_topic
        self.__set_topic = f"""
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]}/
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]}/
            set/
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]}/
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]}"""
        self.__payload = payload
        self.__title = title if title is not None else self.__unique_id
        self.__domain = fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]

    @property
    def unique_id(self) -> str:
        """Get unique_id of the device

        Returns:
            str: Unique ID
        """
        return self.__unique_id

    @property
    def device_type(self) -> str:
        """Get type of the device

        Returns:
            str: Type
        """
        return self.__device_type

    @property
    def parent_id(self) -> str:
        """Get Id of the controller (PLC, Bridge)

        Returns:
            str: Parent ID
        """
        return self.__parent_id

    @property
    def title(self) -> str:
        """Get name of the device

        Returns:
            str: Name
        """
        return self.__title

    @property
    def is_available(self) -> bool:
        """Get info about availability of device

        Returns:
            bool: True/False
        """
        return self.__mqtt.is_available

    @property
    def value(self) -> str:
        """Get value from the mqtt broker."""
        return self.__mqtt.subscribe(self.__state_topic)

    @value.setter
    def value(self, payload) -> bool:
        """Set the value into the broker

        Args:
            payload (str): Data inserted into the set topic

        Returns:
            bool: Result of publish
        """
        self.__payload = payload
        return self.__mqtt.publish(self.__set_topic, self.__payload)

    @property
    def set_topic(self) -> str:
        """Set topic

        Returns:
            str: string of the set topic
        """
        return self.__set_topic

    @property
    def state_topic(self) -> str:
        """State topic

        Returns:
            str: string of the status topic
        """
        return self.__state_topic

    @property
    def domain(self) -> str:
        """Domain name of the topic
           it should represent the manufacturer

        Returns:
            str: Name of the domain
        """
        return self.__domain

    def info(self):
        """Device info."""
        return DeviceInfo(self)

    def info_serialized(self) -> str:
        """Device info in json format string

        Returns:
            str: JSON string format
        """
        info = {
            "name": self.__title,
            "device_type": self.__device_type,
            "id": self.__unique_id,
            "via_device": self.__parent_id,
        }

        json_serialized = json.dumps(info)
        _LOGGER.info("Device: %s", json_serialized)

        return json_serialized


class DeviceInfo(object):
    """Device info class."""

    def __init__(self, device: Device) -> None:
        """Create object of the class

        Args:
            device (Device): device object
        """
        self.__device = device

    @property
    def manufacturer(self) -> str:
        """Manufacturer property."""
        return self.__device.domain

    @property
    def model_number(self) -> str:
        """Modle of the device."""
        return "TODO: model"

    @property
    def sw_version(self) -> str:
        """Sw version of the device."""
        return "TODO: Sw version"

    @property
    def serial_number(self) -> str:
        """Serial number of the device."""
        return self.__device.unique_id
