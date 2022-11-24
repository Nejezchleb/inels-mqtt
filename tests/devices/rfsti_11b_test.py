"""RFSTI 11B switch tests."""
from copy import copy

from unittest import TestCase
from unittest.mock import patch

from inelsmqtt.const import Platform, Element, SWITCH_ON_WITH_TEMP_SET
from inelsmqtt.devices.switch import InelsSwitch
from inelsmqtt import InelsMqtt


from tests.const import (
    TEST_TOPIC_STATE_RFSTI_11B,
    TEST_TOPIC_SET_RFSTI_11B,
    TEST_TOPIC_CONNECTED_RFSTI_11B,
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_TOPIC_STATUS_VALUE_ON_RFSTI_11B,
    TEST_TOPIC_STATUS_VALUE_OFF_RFSTI_11B,
    TEST_AVAILABILITY_ON,
    TEST_AVAILABILITY_OFF,
)
from tests.devices.setup_test import DeviceSetup


class Rfsti_11b(DeviceSetup, TestCase):
    """RFSTI 11b class

    Args:
        TestCase (_type_): Base class of unit testing
    """

    NAME = "RFSTI-11B"

    def setUp(self) -> None:
        """Setup all patches and instances for switch test."""

        self.patches.append(
            patch(
                f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages",
                return_value={
                    TEST_TOPIC_STATE_RFSTI_11B: TEST_TOPIC_STATUS_VALUE_ON_RFSTI_11B,
                    TEST_TOPIC_CONNECTED_RFSTI_11B: TEST_AVAILABILITY_ON,
                },
            )
        )

        for item in self.patches:
            item.start()

        self.instance = InelsSwitch(
            InelsMqtt(self.config), TEST_TOPIC_STATE_RFSTI_11B, self.NAME
        )
        self.instance.get_value()

    def tearDown(self) -> None:
        """Destroy all instances and stop patches"""
        self.instance = None

    def test_setup_rfsti_11b(self) -> None:
        """Test setup the object."""
        i = self.instance

        self.assertEqual(i.device_type, Platform.SWITCH)
        self.assertEqual(i.set_topic, TEST_TOPIC_SET_RFSTI_11B)
        self.assertEqual(i.connected_topic, TEST_TOPIC_CONNECTED_RFSTI_11B)
        self.assertEqual(i.inels_type, Element.RFSTI_11B)
        self.assertTrue(i.is_subscribed)
        self.assertIsNotNone(i.mqtt)
        self.assertTrue(isinstance(i.mqtt, InelsMqtt))

        self.assertEqual(i.title, self.NAME)
        self.assertIsNotNone(i.unique_id)
        self.assertEqual(i.domain, self.domain)

        # RFSTI-11B has one feature [Temperature]
        self.assertIsNotNone(i.features)
        self.assertEqual(len(i.features), 1)

        # listener registered in mqtt borker
        self.assertEqual(len(i.mqtt.list_of_listeners), 1)
        # subscribed into the broker
        self.assertTrue(TEST_TOPIC_STATE_RFSTI_11B in i.mqtt.messages.return_value)

    def test_is_available(self) -> None:
        """Test if is available."""
        self.assertTrue(self.instance.is_available)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_is_not_available(self, mock_mqtt_message) -> None:
        """Test when device is not available."""
        mock_mqtt_message.return_value = {
            TEST_TOPIC_CONNECTED_RFSTI_11B: TEST_AVAILABILITY_OFF
        }

        self.assertFalse(self.instance.is_available)

    def test_subscribe_listener(self) -> None:
        """Test register listner for temperature."""
        # register listerner for dummy function
        self.instance.subscribe_listerner(self.instance.unique_id, lambda x: x + 2)

        self.assertEqual(len(self.instance.listeners), 1)

    def test_state(self) -> None:
        """Get value and check if conversion is find and all attributes are presented."""
        self.assertIsInstance(self.instance.state, object)

        self.assertTrue(self.instance.state.on)
        self.assertEqual(self.instance.state.temperature, 23.7)

    def test_update_value(self) -> None:
        """Test update value in state."""

        prev_state = copy(self.instance.state)

        self.instance.update_value(TEST_TOPIC_STATUS_VALUE_OFF_RFSTI_11B)

        curr_state = self.instance.state

        self.assertTrue(prev_state.on)
        self.assertFalse(curr_state.on)
        self.assertNotEqual(prev_state.on, curr_state.on)

        self.assertNotEqual(prev_state.temperature, curr_state.temperature)

    def test_features(self) -> None:
        """Test list of features."""
        # RFSTI-11B has only one feature and it is temperature sensor
        self.assertTrue(len(self.instance.features) == 1)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.publish")
    def test_set_ha_value(self, mock_publish) -> None:
        """Test set HA value and covert into the inels binary value."""
        mock_publish.return_value = True

        # switch should be off then we would like to turn on
        result: bool = self.instance.set_ha_value(True)

        self.assertEqual(self.instance.values.inels_set_value, SWITCH_ON_WITH_TEMP_SET)

        self.assertEqual(result, mock_publish.return_value)
        self.assertTrue(self.instance.state.on)

        result = self.instance.set_ha_value(False)
        self.assertFalse(self.instance.state.on)
