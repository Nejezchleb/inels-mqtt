"""Unit tests for Device class
    handling device operations
"""
from unittest.mock import Mock, patch
from unittest import TestCase
from inelsmqtt import InelsMqtt
from inelsmqtt.util import DeviceValue
from inelsmqtt.devices import Device, DeviceInfo
from inelsmqtt.const import Platform, Element
from inelsmqtt.const import (
    BATTERY,
    MANUFACTURER,
    STATE_CLOSED,
    STATE_OPEN,
    STOP_UP,
    DEVICE_TYPE_DICT,
    FRAGMENT_DEVICE_TYPE,
    FRAGMENT_DOMAIN,
    FRAGMENT_SERIAL_NUMBER,
    FRAGMENT_UNIQUE_ID,
    SWITCH_OFF_SET,
    SWITCH_ON_SET,
    SWITCH_ON_STATE,
    SWITCH_OFF_STATE,
    TEMP_IN,
    TEMP_OUT,
    TEMPERATURE,
    TOPIC_FRAGMENTS,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_PROTOCOL,
    PROTO_5,
    VERSION,
)

from tests.const import (
    TEST_COVER_RFJA_12_INELS_STATE_CLOSED,
    TEST_COVER_RFJA_12_INELS_STATE_OPEN,
    TEST_COVER_RFJA_12_SET_CLOSE,
    TEST_COVER_RFJA_12_SET_OPEN,
    TEST_COVER_RFJA_12_SET_STOP_UP,
    TEST_COVER_RFJA_12_TOPIC_CONNECTED,
    TEST_COVER_RFJA_12_TOPIC_STATE,
    TEST_LIGH_STATE_HA_VALUE,
    TEST_LIGH_STATE_INELS_VALUE,
    TEST_LIGHT_DIMMABLE_TOPIC_STATE,
    TEST_LIGHT_SET_INELS_VALUE,
    TEST_CLIMATE_RFATV_2_OPEN_TO_40_STATE_VALUE,
    TEST_CLIMATE_RFATV_2_TOPIC_CONNECTED,
    TEST_CLIMATE_RFATV_2_TOPIC_STATE,
    TEST_SENSOR_TOPIC_STATE,
    TEST_AVAILABILITY_OFF,
    TEST_AVAILABILITY_ON,
    TEST_SWITCH_WITH_TEMP_STATE_OFF_VALUE,
    TEST_SWITCH_WITH_TEMP_STATE_ON_VALUE,
    TEST_SWITCH_WITH_TEMP_TOPIC_CONNECTED,
    TEST_SWITCH_WITH_TEMP_TOPIC_STATE,
    TEST_TEMPERATURE_DATA,
    TEST_SWITICH_TOPIC_CONNECTED,
    TEST_SWITCH_TOPIC_STATE,
    TEST_INELS_MQTT_NAMESPACE,
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_HOST,
    TEST_PORT,
    TEST_USER_NAME,
    TEST_PASSWORD,
    TEST_BUTTON_RFGB_40_TOPIC_STATE,
    TEST_BUTTON_RFGB_40_TOPIC_CONNECTED,
    TEST_BUTTON_RFGB_40_STATE_VALUE,
    TEST_SENSOR_RFTC_10_G_TOPIC_STATE,
    TEST_SENSOR_RFTC_10_G_STATE_VALUE,
)


class DeviceTest(TestCase):
    """Device class tests

    Args:
        TestCase (_type_): Base class of unit testing
    """

    def setUp(self) -> None:
        """Setup all patches and instances for device testing"""
        self.patches = [
            patch(f"{TEST_INELS_MQTT_NAMESPACE}.mqtt.Client", return_value=Mock()),
            patch(
                f"{TEST_INELS_MQTT_NAMESPACE}.mqtt.Client.username_pw_set",
                return_value=Mock(),
            ),
            patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.subscribe", return_value=Mock()),
            patch(
                f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.is_subscribed", return_value=Mock()
            ),
            patch(f"{TEST_INELS_MQTT_NAMESPACE}._LOGGER", return_value=Mock()),
        ]

        for item in self.patches:
            item.start()

        config = {
            MQTT_HOST: TEST_HOST,
            MQTT_PORT: TEST_PORT,
            MQTT_USERNAME: TEST_USER_NAME,
            MQTT_PASSWORD: TEST_PASSWORD,
            MQTT_PROTOCOL: PROTO_5,
        }

        self.switch = Device(InelsMqtt(config), TEST_SWITCH_TOPIC_STATE, "Switch")
        self.sensor = Device(InelsMqtt(config), TEST_SENSOR_TOPIC_STATE, "Sensor")
        self.light = Device(InelsMqtt(config), TEST_LIGHT_DIMMABLE_TOPIC_STATE, "Light")
        self.shutter = Device(
            InelsMqtt(config), TEST_COVER_RFJA_12_TOPIC_STATE, "Shutter"
        )
        self.valve = Device(
            InelsMqtt(config), TEST_CLIMATE_RFATV_2_TOPIC_STATE, Platform.CLIMATE
        )
        self.button = Device(
            InelsMqtt(config), TEST_BUTTON_RFGB_40_TOPIC_STATE, Platform.BUTTON
        )

        self.switch_with_temp = Device(
            InelsMqtt(config), TEST_SWITCH_WITH_TEMP_TOPIC_STATE, "Switch"
        )

        self.rftc_10_g = Device(
            InelsMqtt(config), TEST_SENSOR_RFTC_10_G_TOPIC_STATE, "Sensor"
        )

    def tearDown(self) -> None:
        """Destroy all instances and stop patches"""
        self.switch = None
        self.sensor = None
        self.light = None
        self.shutter = None
        self.valve = None
        self.button = None
        self.switch_with_temp = None
        self.rftc_10_g = None

    def test_initialize_device(self) -> None:
        """Test initialization of device object"""
        title = "Device 1"

        # device without title
        dev_no_title = Device(Mock(), TEST_SWITCH_TOPIC_STATE)
        # device with title
        dev_with_title = Device(Mock(), TEST_SWITCH_TOPIC_STATE, title)

        self.assertIsNotNone(dev_no_title)
        self.assertIsNotNone(dev_with_title)

        self.assertIsInstance(dev_no_title, Device)
        self.assertIsInstance(dev_with_title, Device)

        self.assertEqual(dev_no_title.title, dev_no_title.unique_id)
        self.assertEqual(dev_with_title.title, title)

        fragments = TEST_SWITCH_TOPIC_STATE.split("/")

        set_topic = f"{fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]}/set/{fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]}"  # noqa: 501

        self.assertEqual(
            dev_no_title.unique_id, fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]
        )
        self.assertEqual(
            dev_no_title.device_type,
            DEVICE_TYPE_DICT[fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]],
        )
        self.assertEqual(
            dev_no_title.parent_id, fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]
        )

        self.assertEqual(dev_no_title.set_topic, set_topic)
        self.assertEqual(dev_with_title.set_topic, set_topic)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    @patch("inelsmqtt.InelsMqtt.messages")
    def test_set_payload(self, mock_messages, mock_publish) -> None:
        """Test set payload of the device."""
        self.assertTrue(self.switch.set_ha_value(True))

        # SWITCH_ON needs to be encoded becasue broker returns value as a byte
        mock_messages.return_value = {TEST_SWITCH_TOPIC_STATE: SWITCH_ON_STATE.encode()}
        mock_publish.return_value = True

        rt_val = self.switch.get_value()
        self.assertTrue(rt_val.ha_value)
        self.assertEqual(rt_val.inels_status_value, SWITCH_ON_STATE)
        self.assertEqual(rt_val.inels_set_value, SWITCH_ON_SET)

        self.assertTrue(self.switch.set_ha_value(False))

        mock_messages.return_value = {
            TEST_SWITCH_TOPIC_STATE: SWITCH_OFF_STATE.encode()
        }
        mock_publish.return_value = False

        rt_val = self.switch.get_value()
        self.assertFalse(rt_val.ha_value)
        self.assertEqual(rt_val.inels_status_value, SWITCH_OFF_STATE)
        self.assertEqual(rt_val.inels_set_value, SWITCH_OFF_SET)

    def test_info_serialized(self) -> None:
        """Test of the serialized info."""
        self.assertIsInstance(self.switch.info_serialized(), str)

    def test_switch_info(self) -> None:
        """Test of the info."""
        info = self.switch.info()

        self.assertIsInstance(info, DeviceInfo)
        self.assertEqual(info.manufacturer, MANUFACTURER)
        self.assertEqual(info.model_number, self.switch.inels_type)
        self.assertEqual(info.sw_version, VERSION)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_is_available(self, mock_messages) -> None:
        """Test of the device availability."""

        mock_messages.return_value = {
            TEST_SWITICH_TOPIC_CONNECTED: TEST_AVAILABILITY_ON
        }
        is_avilable = self.switch.is_available

        self.assertTrue(is_avilable)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_is_not_available(self, mock_messages) -> None:
        """Test of the device availability wit result false."""

        mock_messages.return_value = {
            TEST_SWITICH_TOPIC_CONNECTED: TEST_AVAILABILITY_OFF
        }
        is_avilable = self.switch.is_available

        self.assertFalse(is_avilable)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_connected_topic_is_not_available(self, mock_messages) -> None:
        """Test handling is_available fnc when connected topic is not available."""

        mock_messages.return_value = {
            TEST_SWITCH_WITH_TEMP_TOPIC_STATE: TEST_SWITCH_WITH_TEMP_STATE_OFF_VALUE
        }

        is_available = self.switch.is_available

        self.assertFalse(is_available)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_rfti_10b(self, mock_message) -> None:
        """Test parsing teperature data to relevant format."""
        mock_message.return_value = {TEST_SENSOR_TOPIC_STATE: TEST_TEMPERATURE_DATA}

        temp_in_decimal_result = 27.4
        temp_out_decimal_result = 26.7
        batter_decimal_result = 100

        data = self.sensor.state

        self.assertEqual(temp_in_decimal_result, data.temp_in)
        self.assertEqual(temp_out_decimal_result, data.temp_out)
        self.assertEqual(batter_decimal_result, data.battery)

        self.assertIsNotNone(self.sensor.features)
        self.assertEqual(len(self.sensor.features), 3)
        self.assertEqual(self.sensor.features, [TEMP_IN, TEMP_OUT, BATTERY])

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_rftc_10g(self, mock_message) -> None:
        """Test connectivity and data from device type 12."""
        mock_message.return_value = {
            TEST_SENSOR_RFTC_10_G_TOPIC_STATE: TEST_SENSOR_RFTC_10_G_STATE_VALUE
        }

        temp = 21.0
        battery_level = 100

        data = self.rftc_10_g.state

        self.assertEqual(temp, data.temperature)
        self.assertEqual(battery_level, data.battery)

        # change state of the topic
        mock_message.return_value = {
            TEST_SENSOR_RFTC_10_G_TOPIC_STATE: b"2C\n00\n81\n00\n00\n"
        }

        temp = 22.0
        battery_level = 0

        self.rftc_10_g.get_value()
        data = self.rftc_10_g.state

        self.assertEqual(temp, data.temperature)
        self.assertEqual(battery_level, data.battery)

        self.assertIsNotNone(self.rftc_10_g.features)
        self.assertEqual(len(self.rftc_10_g.features), 2)
        self.assertEqual(self.rftc_10_g.features, [TEMPERATURE, BATTERY])

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_dimmable_light_test_values(self, mock_message) -> None:
        """Test if the light is on."""
        mock_message.return_value = {
            TEST_LIGHT_DIMMABLE_TOPIC_STATE: TEST_LIGH_STATE_INELS_VALUE
        }

        values = self.light.get_value()

        self.assertEqual(self.light.state, TEST_LIGH_STATE_HA_VALUE)
        self.assertEqual(values.ha_value, TEST_LIGH_STATE_HA_VALUE)
        self.assertEqual(
            values.inels_status_value, TEST_LIGH_STATE_INELS_VALUE.decode()
        )
        self.assertEqual(values.inels_set_value, TEST_LIGHT_SET_INELS_VALUE)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_set_not_support_dimmable_light_value(
        self, mock_message, mock_publish
    ) -> None:
        """Test result ha and inels value when ha value is not supported in inels."""
        mock_message.return_value = {
            TEST_LIGHT_DIMMABLE_TOPIC_STATE: TEST_LIGH_STATE_INELS_VALUE
        }
        mock_publish.return_value = True

        self.light.set_ha_value(24)

        self.assertEqual(self.light.state, TEST_LIGH_STATE_HA_VALUE)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_support_cover_initialized(self, mock_message) -> None:
        """Test covers all props. initialization."""
        mock_message.return_value = {
            TEST_COVER_RFJA_12_TOPIC_STATE: TEST_COVER_RFJA_12_INELS_STATE_OPEN,
            TEST_COVER_RFJA_12_TOPIC_CONNECTED: TEST_AVAILABILITY_ON,
        }

        self.assertTrue(self.shutter.is_available)
        self.assertEqual(self.shutter.device_type, Platform.COVER)
        self.assertEqual(self.shutter.inels_type, Element.RFJA_12)
        self.assertEqual(self.shutter.state, STATE_OPEN)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_support_cover_open_stop_and_close(
        self, mock_message, mock_publish
    ) -> None:
        """Test open the shutter."""
        mock_message.return_value = {
            TEST_COVER_RFJA_12_TOPIC_STATE: TEST_COVER_RFJA_12_INELS_STATE_CLOSED,
        }
        mock_publish.return_value = True

        self.assertNotEqual(self.shutter.state, STATE_OPEN)
        self.assertEqual(self.shutter.state, STATE_CLOSED)

        values: DeviceValue = self.shutter.get_value()

        self.assertIsInstance(values, DeviceValue)
        self.assertEqual(
            values.inels_status_value, TEST_COVER_RFJA_12_INELS_STATE_CLOSED.decode()
        )
        self.assertEqual(values.inels_set_value, TEST_COVER_RFJA_12_SET_CLOSE)

        self.shutter.set_ha_value(STATE_OPEN)

        mock_message.return_value = {
            TEST_COVER_RFJA_12_TOPIC_STATE: TEST_COVER_RFJA_12_INELS_STATE_OPEN,
        }

        values: DeviceValue = self.shutter.get_value()

        self.assertIsInstance(values, DeviceValue)
        self.assertEqual(
            values.inels_status_value, TEST_COVER_RFJA_12_INELS_STATE_OPEN.decode()
        )
        self.assertEqual(values.inels_set_value, TEST_COVER_RFJA_12_SET_OPEN)
        self.assertEqual(self.shutter.state, STATE_OPEN)
        self.assertNotEqual(self.shutter.state, STATE_CLOSED)

        self.shutter.set_ha_value(STOP_UP)
        self.assertEqual(
            self.shutter.values.inels_set_value, TEST_COVER_RFJA_12_SET_STOP_UP
        )
        self.assertEqual(
            self.shutter.values.inels_status_value,
            TEST_COVER_RFJA_12_INELS_STATE_OPEN.decode(),
        )
        self.assertEqual(self.shutter.state, STATE_OPEN)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_support_climate_initialized(self, mock_message) -> None:
        """Test climate all props. initialization."""
        mock_message.return_value = {
            TEST_CLIMATE_RFATV_2_TOPIC_STATE: TEST_CLIMATE_RFATV_2_OPEN_TO_40_STATE_VALUE,
            TEST_CLIMATE_RFATV_2_TOPIC_CONNECTED: TEST_AVAILABILITY_ON,
        }

        self.valve.get_value()

        self.assertTrue(self.valve.is_available)
        self.assertEqual(self.valve.device_type, Platform.CLIMATE)
        self.assertEqual(self.valve.inels_type, Element.RFATV_2)
        self.assertEqual(self.valve.state.current, 26.0)
        self.assertEqual(self.valve.state.required, 32.0)
        self.assertEqual(self.valve.state.open_in_percentage, 40.0)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_set_climate_valve_value(self, mock_message, mock_publish) -> None:
        """Test valve value."""
        mock_message.return_value = {
            TEST_CLIMATE_RFATV_2_TOPIC_STATE: TEST_CLIMATE_RFATV_2_OPEN_TO_40_STATE_VALUE
        }
        mock_publish.return_value = True

        state = self.valve.state
        state.required = 30.0

        self.valve.set_ha_value(state)

        self.assertEqual(self.valve.values.inels_set_value, "00 3C 00")

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_support_button_initialized(self, mock_message) -> None:
        """Test button all props. initialization."""
        mock_message.return_value = {
            TEST_BUTTON_RFGB_40_TOPIC_STATE: TEST_BUTTON_RFGB_40_STATE_VALUE,
            TEST_BUTTON_RFGB_40_TOPIC_CONNECTED: TEST_AVAILABILITY_ON,
        }

        self.button.get_value()

        self.assertTrue(self.button.is_available)
        self.assertEqual(self.button.device_type, Platform.BUTTON)
        self.assertEqual(self.button.inels_type, Element.RFGB_40)
        self.assertTrue(self.button.state)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_device_switch_with_temp(self, mock_message) -> None:
        """Test switch with temperature."""
        mock_message.return_value = {
            TEST_SWITCH_WITH_TEMP_TOPIC_CONNECTED: TEST_AVAILABILITY_ON,
            TEST_SWITCH_WITH_TEMP_TOPIC_STATE: TEST_SWITCH_WITH_TEMP_STATE_ON_VALUE,
        }

        self.switch_with_temp.get_value()

        self.assertTrue(self.switch_with_temp.is_available)
        self.assertEqual(self.switch_with_temp.device_type, Platform.SWITCH)
        self.assertEqual(self.switch_with_temp.inels_type, Element.RFSTI_11B)
        self.assertTrue(self.switch_with_temp.state.on)
        self.assertIsNotNone(self.switch_with_temp.state.temperature)
        self.assertEqual(self.switch_with_temp.state.temperature, 24.5)

        mock_message.return_value = {
            TEST_SWITCH_WITH_TEMP_TOPIC_CONNECTED: TEST_AVAILABILITY_ON,
            TEST_SWITCH_WITH_TEMP_TOPIC_STATE: TEST_SWITCH_WITH_TEMP_STATE_OFF_VALUE,
        }

        self.switch_with_temp.get_value()

        self.assertFalse(self.switch_with_temp.state.on)
        self.assertEqual(self.switch_with_temp.state.temperature, 21.0)
