"""Utility classes."""
from typing import Any

from .const import (
    DEVICE_TYPE_DICT,
    SWITCH,
    SWITCH_STATE,
)


class DeviceValue(object):
    """Device value interpretation object."""

    def __init__(
        self,
        device_type: DEVICE_TYPE_DICT,
        inels_value: str = None,
        ha_value: Any = None,
    ) -> None:
        """initializing device info."""
        self.__inels_value = inels_value
        self.__ha_value = ha_value
        self.__device_type = device_type

        if self.__ha_value is None:
            self.__find_ha_value()

        if self.__inels_value is None:
            self.__find_inels_value()

    def __find_ha_value(self) -> None:
        """Find and crete device value object."""
        if self.__device_type == SWITCH:
            self.__ha_value = SWITCH_STATE[self.__inels_value]

    def __find_inels_value(self) -> None:
        """Find inels mqtt value for specific device."""
        if self.__device_type == SWITCH:
            self.__inels_value = list(SWITCH_STATE.keys())[
                list(SWITCH_STATE.values()).index(self.__ha_value)
            ]

    @property
    def ha_value(self) -> Any:
        """Converted value from inels mqtt broker into
           the HA format

        Returns:
            Any: object to corespond to HA device
        """
        return self.__ha_value

    @property
    def inels_value(self) -> str:
        """Raw inels value from mqtt broker

        Returns:
            str: quated string from mqtt broker
        """
        return self.__inels_value
