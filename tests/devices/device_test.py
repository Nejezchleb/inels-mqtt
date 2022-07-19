"""Unit tests for Device class
    handling device operations
"""
from unittest.mock import Mock, patch
from unittest import TestCase
from inelsmqtt import InelsMqtt

from inelsmqtt.devices import Device, DeviceInfo
from inelsmqtt.const import (
    DEVICE_TYPE_DICT,
    FRAGMENT_DEVICE_TYPE,
    FRAGMENT_DOMAIN,
    FRAGMENT_SERIAL_NUMBER,
    FRAGMENT_UNIQUE_ID,
    SWITCH_ON,
    SWITCH_OFF,
    TOPIC_FRAGMENTS,
    MQTT_HOST,
    MQTT_PORT,
    MQTT_USERNAME,
    MQTT_PASSWORD,
    MQTT_PROTOCOL,
    PROTO_5,
)

from tests.const import (
    TEST_TOPIC_STATE,
    TEST_INELS_MQTT_NAMESPACE,
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_HOST,
    TEST_PORT,
    TEST_USER_NAME,
    TEST_PASSWORD,
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

        self.device = Device(InelsMqtt(config), TEST_TOPIC_STATE, "Device")

    def tearDown(self) -> None:
        """Destroy all instances and stop patches"""
        self.device = None

    def test_initialize_device(self) -> None:
        """Test initialization of device object"""
        title = "Device 1"

        # device without title
        dev_no_title = Device(Mock(), TEST_TOPIC_STATE)
        # device with title
        dev_with_title = Device(Mock(), TEST_TOPIC_STATE, title)

        self.assertIsNotNone(dev_no_title)
        self.assertIsNotNone(dev_with_title)

        self.assertIsInstance(dev_no_title, Device)
        self.assertIsInstance(dev_with_title, Device)

        self.assertEqual(dev_no_title.title, dev_no_title.unique_id)
        self.assertEqual(dev_with_title.title, title)

        fragments = TEST_TOPIC_STATE.split("/")

        set_topic = f"{fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]}/set/{fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]}/{fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]}"  # noqa: 501

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
    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.subscribe")
    def test_set_paylod(self, mock_subscribe, mock_publish) -> None:
        """Test set payload of the device."""
        self.assertTrue(self.device.set_ha_value(True))

        mock_subscribe.return_value = SWITCH_ON
        mock_publish.return_value = True

        rt_val = self.device.get_value()
        self.assertTrue(rt_val.ha_value)
        self.assertEqual(rt_val.inels_value, SWITCH_ON)

        self.assertTrue(self.device.set_ha_value(False))

        mock_subscribe.return_value = SWITCH_OFF
        mock_publish.return_value = False

        rt_val = self.device.get_value()
        self.assertFalse(rt_val.ha_value)
        self.assertEqual(rt_val.inels_value, SWITCH_OFF)

    def test_info_serialized(self) -> None:
        """Test of the serialized info."""
        self.assertIsInstance(self.device.info_serialized(), str)

    def test_info(self) -> None:
        """Test of the info."""
        info = self.device.info()
        fragments = TEST_TOPIC_STATE.split("/")

        self.assertIsInstance(info, DeviceInfo)
        self.assertEqual(info.manufacturer, fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]])
