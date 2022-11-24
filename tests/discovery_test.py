"""Unit test for Discovery class
    handling device discovering
"""
from unittest.mock import patch
from unittest import TestCase

from inelsmqtt.discovery import InelsDiscovery
from inelsmqtt import InelsMqtt

from tests.const import (
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_SWITCH_TOPIC_STATE,
)
from tests.devices.setup_test import DeviceSetup


class DiscoveryTest(DeviceSetup, TestCase):
    """Discovery class tests

    Args:
        TestCase (_type_): Base class of unit testing
    """

    def setUp(self) -> None:
        """Setup all patches and instances for Discovery testing"""
        for item in DeviceSetup.patches:
            item.start()

        mqtt = InelsMqtt(self.config)

        self.i_dis = InelsDiscovery(mqtt)

    def tearDown(self) -> None:
        """Destroy all instances and stop patches"""
        self.patches = None
        self.i_dis = None

    def test_init_discovery(self) -> None:
        """Initialize test instance of the InelsDiscovery"""
        self.assertIsInstance(self.i_dis, InelsDiscovery)
        self.assertIsInstance(self.i_dis.devices, list)
        self.assertEqual(len(self.i_dis.devices), 0)

    @patch(
        f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.discovery_all",
        return_value={TEST_SWITCH_TOPIC_STATE: "data"},
    )
    def test_discovery(self, mock_discovery_all) -> None:
        """Test get list of devices"""

        coordinators_with_devices = self.i_dis.discovery()

        devices = self.i_dis.devices

        self.assertGreater(len(devices), 0)
        self.assertGreater(len(self.i_dis.coordinators), 0)
        self.assertGreater(len(coordinators_with_devices), 0)

        mock_discovery_all.assert_called()
        mock_discovery_all.assert_called_once()
