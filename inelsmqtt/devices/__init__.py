"""Class handle base info about device."""
import logging

from inelsmqtt import InelsMqtt

_LOGGER = logging.getLogger(__name__)


class Device(object):
    """Carry basic device stuff

    Args:
        object (_type_): default object it is new style of python class coding
    """

    def __init__(
        self,
        mqtt: InelsMqtt,
        device_type: str,
        unique_id: str,
        state_topic: str,
        set_topic: str,
        payload: str,
        title: str = None,
    ) -> None:
        """Initialize instance of device

        Args:
            mqtt (InelsMqtt): instance of mqtt broker
            device_type (str): Type of the device in readable form
            unique_id (str): Unique id of the device (serial number)
            status_topic (str): String format of status topic
            set_topic (str): Sring format of set topic
            payload (str): Value carried inside of the topic
            title (str, optional): Formal name of the device. When None
            then will be same as unique_id. Defaults to None.
        """
