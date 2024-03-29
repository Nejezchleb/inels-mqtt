"""Unit tests for InelsMqtt class
    handling mqtt broker communication.
"""
from typing import Any
from unittest.mock import patch, Mock
from unittest import TestCase

from inelsmqtt import InelsMqtt

from tests.const import (
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_INELS_MQTT_NAMESPACE,
    TEST_HOST,
    TEST_PORT,
    TEST_CLIMATE_RFATV_2_TOPIC_STATE,
    TEST_BUTTON_RFGB_40_TOPIC_STATE,
)
from tests.devices.setup_test import DeviceSetup


class InelsMqttTest(DeviceSetup, TestCase):
    """Testing class for InelsMqtt."""

    def setUp(self) -> None:
        """Setup all patches and instances for testing

        Returns:
            InelsMqttTest: self instance of the testing class
        """
        for item in DeviceSetup.patches:
            item.start()

        self.mqtt = InelsMqtt(self.config)

    def tearDown(self) -> None:
        """Destroy all instances and stop all patches

        Returns:
            InelsMqttTest: self instance of the testing class
        """
        self.patches = None

    def test_instance_initialization(self) -> None:
        """Testing initialization of all props. InelsMqtt class."""
        self.assertEqual(
            self.mqtt._InelsMqtt__host, TEST_HOST  # pylint: disable=protected-access
        )
        self.assertEqual(
            self.mqtt._InelsMqtt__port, TEST_PORT  # pylint: disable=protected-access
        )

    def test_is_available_true_false_based_on__on_connect_function(self) -> None:
        """Testing if is broker available with result True."""

        def on_connect(self, reason_code) -> None:
            """Inner helper method for on_connect call

            Args:
                reason_code (number): Reason code determined by broker
                List of all reason codes:
                https://emqx.medium.com/mqtt-5-0-new-features-2-reason-code-and-ack-8503ee712ba5
            """
            # call __on_connect function with params which is represented successfull connection
            self.mqtt._InelsMqtt__on_connect(  # pylint: disable=protected-access
                self.mqtt, Mock(), Mock(), reason_code, None
            )

        # reason_code = 0 is connectes successfull
        on_connect(self, 0)
        self.assertEqual(self.mqtt.is_available, True)

        # reason_code = 135 not authorized
        on_connect(self, 135)
        self.assertEqual(self.mqtt.is_available, False)

    @patch(
        f"{TEST_INELS_MQTT_CLASS_NAMESPACE}._InelsMqtt__connect", return_value=Mock()
    )
    @patch(f"{TEST_INELS_MQTT_NAMESPACE}.mqtt.Client.subscribe", return_value=Mock())
    def test_discovery_all_with_tree_messages(
        self, mock_connect, mock_broker_subscribe
    ) -> None:
        """Test discovery funct to find and register all interested topics."""

        # initialize three topics with status
        items = {
            "inels/status/45464654/02/457544": "rrqeraad",
            "inels/status/45464654/02/74544": "eeeqqq",
            "inels/status/45464654/02/8887": "adfadfefe",
            "some/kind/of/different/topic/in/broker": "adfadf",  # should be filtered out
        }

        for item in items.items():
            msg = type("msg", (object,), {"topic": item[0], "payload": item[1]})
            self.mqtt._InelsMqtt__on_discover(  # pylint: disable=protected-access
                self.mqtt, Mock(), msg
            )

        devices = self.mqtt.discovery_all()
        self.assertEqual(len(devices), 3)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.subscribe")
    def test_subscribe_message(self, mock_broker_subscribe) -> None:
        """Testing subscribtion of the message from the broker."""

        mock_broker_subscribe.return_value = "adfadfadf"

        topic = "inels/status/45464654/02/457544"
        msg = type(
            "msg",
            (object,),
            {"topic": topic, "payload": mock_broker_subscribe.return_value},
        )

        self.mqtt._InelsMqtt__on_message(  # pylint: disable=protected-access
            self.mqtt, Mock(), msg
        )

        payload = self.mqtt.subscribe(topic=topic)

        self.assertEqual(msg.payload, payload)

    @patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.messages")
    def test_message_property(self, mock_messages) -> None:
        """Test if message property returns right data."""

        mock_messages.return_value = {
            "inels/status/555555/02/3423452435": "first",
            "inels/status/555555/02/3424524222": "second",
            "inels/status/555555/03/452435234": "third",
            "inels/status/222222/02/85034495": "fourth",
        }

        self.assertIsNotNone(self.mqtt.messages())
        self.assertEqual(len(self.mqtt.messages()), 4)
        self.assertDictEqual(self.mqtt.messages(), mock_messages.return_value)

    def test_subscribe_listenres(self) -> None:
        """Test listerner subscription."""

        def dummy_callback(prm) -> Any:
            """Dummy callback function"""
            return prm

        self.mqtt.subscribe_listener(TEST_BUTTON_RFGB_40_TOPIC_STATE, dummy_callback)
        self.mqtt.subscribe_listener(TEST_CLIMATE_RFATV_2_TOPIC_STATE, dummy_callback)

        self.assertEqual(2, len(self.mqtt.list_of_listeners))

    def test_unsubscribe_listers(self) -> None:
        """Test unsubscribe all listenres."""

        def dummy_callback(prm) -> Any:
            """Dummy callback function"""
            return prm

        self.mqtt.subscribe_listener(TEST_BUTTON_RFGB_40_TOPIC_STATE, dummy_callback)
        self.mqtt.subscribe_listener(TEST_CLIMATE_RFATV_2_TOPIC_STATE, dummy_callback)

        self.assertEqual(2, len(self.mqtt.list_of_listeners))

        self.mqtt.unsubscribe_listeners()

        self.assertEqual(0, len(self.mqtt.list_of_listeners))
