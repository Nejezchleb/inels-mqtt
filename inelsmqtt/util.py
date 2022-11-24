"""Utility classes."""
import logging

from operator import itemgetter
from typing import Any, Dict

from inelsmqtt.mqtt_client import GetMessageType

from .const import Platform, Element
from .const import (
    ANALOG_REGULATOR_SET_BYTES,
    BATTERY,
    CLIMATE_TYPE_09_DATA,
    CURRENT_TEMP,
    DEVICE_TYPE_05_DATA,
    DEVICE_TYPE_05_HEX_VALUES,
    BUTTON_TYPE_19_DATA,
    BUTTON_DEVICE_AMOUNT,
    BUTTON_NUMBER,
    DEVICE_TYPE_07_DATA,
    DEVICE_TYPE_10_DATA,
    DEVICE_TYPE_12_DATA,
    REQUIRED_TEMP,
    SENSOR_RFTC_10_G_LOW_BATTERY,
    SHUTTER_SET,
    SHUTTER_STATE_LIST,
    SHUTTER_STATES,
    SWITCH_SET,
    SWITCH_STATE,
    OPEN_IN_PERCENTAGE,
    STATE,
    IDENTITY,
    SWITCH_WITH_TEMP_SET,
    TEMP_IN,
    TEMP_OUT,
    TEMPERATURE,
)

ConfigType = Dict[str, str]
_LOGGER = logging.getLogger(__name__)


def new_object(**kwargs):
    """Create new anonymouse object."""
    return type("Object", (), kwargs)


class DeviceValue(object):
    """Device value interpretation object."""

    def __init__(
        self,
        device_type: Platform,
        inels_type: str,
        inels_value: str = None,
        ha_value: Any = None,
        last_value: Any = None,
    ) -> None:
        """initializing device info."""
        self.__inels_status_value = inels_value
        self.__inels_set_value: Any = None
        self.__ha_value = ha_value
        self.__device_type = device_type
        self.__inels_type = inels_type
        self.__last_value = last_value

        if self.__ha_value is None:
            self.__find_ha_value()

        if self.__inels_status_value is None:
            self.__find_inels_value()

    def __find_ha_value(self) -> None:
        """Find and crete device value object."""
        if self.__device_type is Platform.SWITCH:
            if self.__inels_type is Element.RFSTI_11B:
                state = int(
                    self.__trim_inels_status_values(DEVICE_TYPE_07_DATA, STATE, ""), 16
                )

                temp = (
                    int(
                        self.__trim_inels_status_values(
                            DEVICE_TYPE_07_DATA, TEMP_OUT, ""
                        ),
                        16,
                    )
                    / 100
                )

                self.__ha_value = new_object(on=(state == 1), temperature=temp)
                self.__inels_set_value = SWITCH_WITH_TEMP_SET[self.__ha_value.on]
            else:
                self.__ha_value = SWITCH_STATE[self.__inels_status_value]
                self.__inels_set_value = SWITCH_SET[self.__ha_value]
        elif self.__device_type is Platform.SENSOR:
            if self.__inels_type is Element.RFTI_10B:
                hex_temp_in = self.__trim_inels_status_values(
                    DEVICE_TYPE_10_DATA, TEMP_IN, ""
                )
                hex_temp_out = self.__trim_inels_status_values(
                    DEVICE_TYPE_10_DATA, TEMP_OUT, ""
                )
                hex_battery = self.__trim_inels_status_values(
                    DEVICE_TYPE_10_DATA, BATTERY, ""
                )

                temp_in = int(hex_temp_in, 16) / 100
                temp_out = int(hex_temp_out, 16) / 100
                battery_level = 100 if int(hex_battery, 16) == 0 else 0

                self.__ha_value = new_object(
                    temp_in=temp_in,
                    temp_out=temp_out,
                    battery=battery_level,
                )
            elif self.__inels_type is Element.RFTC_10_G:
                hex_temp = self.__trim_inels_status_values(
                    DEVICE_TYPE_12_DATA, TEMPERATURE, ""
                )
                hex_battery = self.__trim_inels_status_values(
                    DEVICE_TYPE_12_DATA, BATTERY, ""
                )

                temperature = int(hex_temp, 16) * 0.5
                battery_level = (
                    0 if hex_battery == SENSOR_RFTC_10_G_LOW_BATTERY else 100
                )

                self.__ha_value = new_object(
                    temperature=temperature,
                    battery=battery_level,
                )
            else:
                self.__ha_value = self.__inels_status_value
        elif self.__device_type is Platform.LIGHT:
            if self.__inels_type is Element.RFDAC_71B:
                self.__ha_value = DEVICE_TYPE_05_HEX_VALUES[self.__inels_status_value]

                trimmed_data = self.__trim_inels_status_values(
                    DEVICE_TYPE_05_DATA, Element.RFDAC_71B.value, " "
                )
                self.__inels_set_value = f"{ANALOG_REGULATOR_SET_BYTES[Element.RFDAC_71B.value]} {trimmed_data}"  # noqa: E501
            else:
                self.__ha_value = self.__inels_status_value
        elif self.__device_type is Platform.COVER:
            ha_val = SHUTTER_STATES.get(self.__inels_status_value)

            self.__ha_value = ha_val if ha_val is not None else self.__last_value
            self.__inels_set_value = SHUTTER_SET[self.__ha_value]
        elif self.__device_type is Platform.CLIMATE:
            if self.__inels_type is Element.RFATV_2:
                temp_current_hex = self.__trim_inels_status_values(
                    CLIMATE_TYPE_09_DATA, CURRENT_TEMP, ""
                )
                temp_current = int(temp_current_hex, 16) * 0.5
                temp_required_hex = self.__trim_inels_status_values(
                    CLIMATE_TYPE_09_DATA, REQUIRED_TEMP, ""
                )
                temp_required = int(temp_required_hex, 16) * 0.5
                battery_hex = self.__trim_inels_status_values(
                    CLIMATE_TYPE_09_DATA, BATTERY, ""
                )
                open_to_hex = self.__trim_inels_status_values(
                    CLIMATE_TYPE_09_DATA, OPEN_IN_PERCENTAGE, ""
                )
                open_to_percentage = int(open_to_hex, 16) * 0.5
                batter = int(battery_hex, 16)
                self.__ha_value = new_object(
                    battery=batter,
                    current=temp_current,
                    required=temp_required,
                    open_in_percentage=open_to_percentage,
                )
            else:
                self.__ha_value = self.__inels_status_value
        elif self.__device_type is Platform.BUTTON:
            if self.__inels_type is Element.RFGB_40:
                state = self.__trim_inels_status_values(BUTTON_TYPE_19_DATA, STATE, "")
                state_hex_str = f"0x{state}"
                state_bin_str = f"{int(state_hex_str, 16):0>8b}"

                identity = self.__trim_inels_status_values(
                    BUTTON_TYPE_19_DATA, IDENTITY, ""
                )

                self.__ha_value = new_object(
                    number=BUTTON_NUMBER.get(identity),
                    battery=100 if state_bin_str[4] == "0" else 0,
                    pressing=state_bin_str[3] == "1",
                    changed=state_bin_str[2] == "1",
                    amount=BUTTON_DEVICE_AMOUNT.get(self.__inels_type),
                )

    def __trim_inels_status_values(
        self, selector: dict[str, Any], fragment: str, jointer: str
    ) -> str:
        """Trim inels status from broker into the pure string."""
        data = self.__inels_status_value.split("\n")[:-1]

        selected = itemgetter(*selector[fragment])(data)
        return jointer.join(selected)

    def __find_inels_value(self) -> None:
        """Find inels mqtt value for specific device."""
        if self.__device_type is Platform.SWITCH:
            if self.__inels_type == Element.RFSTI_11B:
                self.__inels_set_value = SWITCH_WITH_TEMP_SET.get(self.__ha_value.on)
            else:
                self.__inels_status_value = self.__find_keys_by_value(
                    SWITCH_STATE, self.__ha_value, self.__last_value
                )
                self.__inels_set_value = SWITCH_SET.get(self.__ha_value)
        elif self.__device_type is Platform.LIGHT:
            if self.__inels_type is Element.RFDAC_71B:
                self.__inels_status_value = self.__find_keys_by_value(
                    DEVICE_TYPE_05_HEX_VALUES,
                    round(self.__ha_value, -1),
                    self.__last_value,
                )
                trimmed_data = self.__trim_inels_status_values(
                    DEVICE_TYPE_05_DATA, Element.RFDAC_71B.value, " "
                )
                self.__inels_set_value = f"{ANALOG_REGULATOR_SET_BYTES[Element.RFDAC_71B.value]} {trimmed_data}"  # noqa: E501
                self.__ha_value = DEVICE_TYPE_05_HEX_VALUES[self.__inels_status_value]
        elif self.__device_type is Platform.COVER:
            if self.__inels_type is Element.RFJA_12:
                self.__inels_status_value = self.__find_keys_by_value(
                    SHUTTER_STATES, self.__ha_value, self.__last_value
                )
                self.__inels_set_value = SHUTTER_SET.get(self.__ha_value)
                # speical behavior. We need to find right HA state for the cover
                prev_val = SHUTTER_STATES.get(self.__inels_status_value)
                ha_val = (
                    self.__ha_value
                    if self.__ha_value in SHUTTER_STATE_LIST
                    else prev_val
                )
                self.__ha_value = ha_val
        elif self.__device_type is Platform.CLIMATE:
            if self.__inels_type is Element.RFATV_2:
                required_temp = int(round(self.__ha_value.required * 2, 0))
                self.__inels_set_value = f"00 {required_temp:x} 00".upper()
        elif self.__device_type is Platform.BUTTON:
            self.__ha_value = ha_val

    def __find_keys_by_value(self, array: dict, value, last_value) -> Any:
        """Return key from dict by value

        Args:
            array (dict): dictionary where should I have to search
            value Any: by this value I'm goning to find key
        Returns:
            Any: value of the dict key
        """
        keys = list(array.keys())
        vals = list(array.values())
        try:
            index = vals.index(value)
            return keys[index]
        except ValueError as err:
            index = vals.index(last_value)
            _LOGGER.warning(
                "Value %s is not in list of %s. Stack %s", value, array, err
            )

        return keys[index]

    @property
    def ha_value(self) -> Any:
        """Converted value from inels mqtt broker into
           the HA format

        Returns:
            Any: object to corespond to HA device
        """
        return self.__ha_value

    @property
    def inels_status_value(self) -> str:
        """Raw inels value from mqtt broker

        Returns:
            str: quated string from mqtt broker
        """
        return self.__inels_status_value

    @property
    def inels_set_value(self) -> str:
        """Raw inels value for mqtt broker

        Returns:
            str: this is string format value for mqtt broker
        """
        return self.__inels_set_value


def get_value(status: GetMessageType, platform: str) -> Any:
    """Get value from pyload message."""
    if platform == Platform.SWITCH:
        return SWITCH_STATE[status]

    return None


def get_state_topic(cfg: ConfigType) -> str:
    """Get state topic."""
    return cfg["DDD"]


def get_set_topic(cfg: ConfigType) -> str:
    """Get set topic."""
    return cfg["OOO"]


def get_name(cfg: ConfigType) -> str:
    """Get name of the entity."""
    return cfg["Name"]
