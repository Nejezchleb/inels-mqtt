"""Unit tests for Device class
    handling device operations
"""
from unittest.mock import Mock
from unittest import TestCase

from inelsmqtt.devices import Device, DeviceInfo
from inelsmqtt.const import (
    DEVICE_TYPE_DICT,
    FRAGMENT_DEVICE_TYPE,
    FRAGMENT_DOMAIN,
    FRAGMENT_SERIAL_NUMBER,
    FRAGMENT_UNIQUE_ID,
    TOPIC_FRAGMENTS,
)

from tests.const import TEST_TOPIC_STATE


class DeviceTest(TestCase):
    """Device class tests

    Args:
        TestCase (_type_): Base class of unit testing
    """

    def setUp(self) -> None:
        """Setup all patches and instances for device testing"""
        self.device = Device(Mock(), TEST_TOPIC_STATE, "Device")

    def tearDown(self) -> None:
        """Destroy all instances and stop patches"""
        self.device = None

    def test_initialize_device(self) -> None:
        """Test initialization of device object"""
        title = "Device 1"
        data = '{"power": "on"}'

        # device without title
        dev_no_title = Device(Mock(), TEST_TOPIC_STATE, data)
        # device with title
        dev_with_title = Device(Mock(), TEST_TOPIC_STATE, data, title)

        self.assertIsNotNone(dev_no_title)
        self.assertIsNotNone(dev_with_title)

        self.assertIsInstance(dev_no_title, Device)
        self.assertIsInstance(dev_with_title, Device)

        self.assertEqual(dev_no_title.title, dev_no_title.unique_id)
        self.assertEqual(dev_with_title.title, title)

        fragments = TEST_TOPIC_STATE.split("/")

        set_topic = f"""
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]]}/
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_SERIAL_NUMBER]]}/
            set/
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]}/
            {fragments[TOPIC_FRAGMENTS[FRAGMENT_UNIQUE_ID]]}"""

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

    def test_info_serialized(self) -> None:
        """Test of the serialized info."""
        self.assertIsInstance(self.device.info_serialized(), str)

    def test_info(self) -> None:
        """Test of the info."""
        info = self.device.info()
        fragments = TEST_TOPIC_STATE.split("/")

        self.assertIsInstance(info, DeviceInfo)
        self.assertEqual(info.manufacturer, fragments[TOPIC_FRAGMENTS[FRAGMENT_DOMAIN]])
