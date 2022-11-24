"""RFDAC-71B light tests."""
from copy import copy

from unittest import TestCase
from unittest.mock import patch

from inelsmqtt.const import Platform, Element
from inelsmqtt.devices.light import InelsLight
from inelsmqtt import InelsMqtt


from tests.const import (
    TEST_TOPIC_STATE_RFDAC_71B,
    TEST_TOPIC_CONNECTED_RFDAC_71B,
    TEST_TOPIC_SET_RFDAC_71B,
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_TOPIC_SET_LIGHT_10_RFDAC_71B,
    TEST_AVAILABILITY_ON,
    TEST_AVAILABILITY_OFF,
    TEST_TOPIC_STATE_LIGHT_10_RFDAC_71B,
    TEST_TOPIC_STATE_LIGHT_80_RFDAC_71B,
)
from tests.devices.setup_test import DeviceSetup


class Rfdac_71b(DeviceSetup, TestCase):
    """RFDAC-71b class

    Args:
        TestCase (_type_): Base class of unit testing
    """

    NAME = "RFDAC-71B"

    def setUp(self) -> None:
        """Setup all patches and instances for light test."""

        self.patches.append(
            patch(
                f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages",
                return_value={
                    TEST_TOPIC_STATE_RFDAC_71B: TEST_TOPIC_STATE_LIGHT_10_RFDAC_71B,
                    TEST_TOPIC_CONNECTED_RFDAC_71B: TEST_AVAILABILITY_ON,
                },
            )
        )

        for item in self.patches:
            item.start()

        self.instance = InelsLight(
            InelsMqtt(self.config), TEST_TOPIC_STATE_RFDAC_71B, self.NAME
        )
        self.instance.get_value()

    def tearDown(self) -> None:
        """Destroy all instances and stop patches"""
        self.instance = None

    def test_setup_rfdac_71b(self) -> None:
        """Test setup the object."""
        i = self.instance

        self.assertEqual(i.device_type, Platform.LIGHT)
        self.assertEqual(i.set_topic, TEST_TOPIC_SET_RFDAC_71B)
        self.assertEqual(i.connected_topic, TEST_TOPIC_CONNECTED_RFDAC_71B)
        self.assertEqual(i.inels_type, Element.RFDAC_71B)
        self.assertTrue(i.is_subscribed)
        self.assertIsNotNone(i.mqtt)
        self.assertTrue(isinstance(i.mqtt, InelsMqtt))

        self.assertEqual(i.title, self.NAME)
        self.assertIsNotNone(i.unique_id)
        self.assertEqual(i.domain, self.domain)

        # RFSTI-11B has one feature [Temperature]
        self.assertIsNone(i.features)

        # listener registered in mqtt borker
        self.assertEqual(len(i.mqtt.list_of_listeners), 1)
        # subscribed into the broker
        self.assertTrue(TEST_TOPIC_STATE_RFDAC_71B in i.mqtt.messages.return_value)

    def test_is_available(self) -> None:
        """Test if is available."""
        self.assertTrue(self.instance.is_available)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_is_not_available(self, mock_mqtt_message) -> None:
        """Test when device is not available."""
        mock_mqtt_message.return_value = {
            TEST_TOPIC_CONNECTED_RFDAC_71B: TEST_AVAILABILITY_OFF
        }

        self.assertFalse(self.instance.is_available)

    def test_subscribe_listener(self) -> None:
        """Test register listner for temperature."""
        # register listerner for dummy function
        self.instance.subscribe_listerner(self.instance.unique_id, lambda x: x + 2)

        self.assertEqual(len(self.instance.listeners), 1)

    def test_state(self) -> None:
        """Get value and check if conversion is find and all attributes are presented."""
        self.assertIsInstance(self.instance.state, int)

        self.assertEqual(self.instance.state, 10)

    def test_update_value(self) -> None:
        """Test update value in state."""

        prev_state = copy(self.instance.state)

        self.instance.update_value(TEST_TOPIC_STATE_LIGHT_80_RFDAC_71B)

        curr_state = self.instance.state

        self.assertEqual(prev_state, 10)
        self.assertEqual(curr_state, 80)
        self.assertNotEqual(prev_state, curr_state)

    def test_features(self) -> None:
        """Test list of features."""
        # this device does not have any features
        self.assertIsNone(self.instance.features)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    def test_set_ha_value(self, mock_publish) -> None:
        """Test set HA value and covert into the inels binary value."""
        mock_publish.return_value = True

        # switch should be off then we would like to turn on
        result: bool = self.instance.set_ha_value(10)

        self.assertEqual(
            self.instance.values.inels_set_value, TEST_TOPIC_SET_LIGHT_10_RFDAC_71B
        )

        self.assertEqual(result, mock_publish.return_value)
        self.assertEqual(self.instance.state, 10)

        result = self.instance.set_ha_value(80)
        self.assertEqual(self.instance.state, 80)
