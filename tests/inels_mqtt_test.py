"""Unit tests for InelsMqtt class
    handling mqtt broker communication.
"""
from unittest.mock import patch, Mock
from unittest import TestCase

from inelsmqtt import InelsMqtt

from tests.const import (
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_INELS_MQTT_NAMESPACE,
    TEST_HOST,
    TEST_PORT,
    TEST_USER_NAME,
    TEST_PASSWORD,
    TEST_DEBUG_TRUE,
)


class InelsMqttTest(TestCase):
    """Testing class for InelsMqtt."""

    def setUp(self) -> None:
        """Setup all patches and instances for testing

        Returns:
            InelsMqttTest: self instance of the testing class
        """

        # mocking mqtt broker client
        self.patches = [
            patch(f"{TEST_INELS_MQTT_NAMESPACE}.MqttClient", return_value=Mock()),
            patch(
                f"{TEST_INELS_MQTT_NAMESPACE}.MqttClient.username_pw_set",
                return_value=Mock(),
            ),
            patch(f"{TEST_INELS_MQTT_NAMESPACE}._LOGGER", return_value=Mock()),
        ]

        for item in self.patches:
            item.start()

        self.mqtt = InelsMqtt(
            TEST_HOST, TEST_PORT, TEST_USER_NAME, TEST_PASSWORD, TEST_DEBUG_TRUE
        )

    def tearDown(self) -> None:
        """Destroy all instances and stop all patches

        Returns:
            InelsMqttTest: self instance of the testing class
        """
        patch.stopall()
        self.patches = None

    def test_instance_initialization(self) -> None:
        """Testing initialization of all props. InelsMqtt class."""
        self.assertEqual(
            self.mqtt._InelsMqtt__host, TEST_HOST  # pylint: disable=protected-access
        )
        self.assertEqual(
            self.mqtt._InelsMqtt__port, TEST_PORT  # pylint: disable=protected-access
        )
        self.assertEqual(
            self.mqtt._InelsMqtt__user_name,  # pylint: disable=protected-access
            TEST_USER_NAME,
        )
        self.assertEqual(
            self.mqtt._InelsMqtt__password,  # pylint: disable=protected-access
            TEST_PASSWORD,
        )
        self.assertEqual(
            self.mqtt._InelsMqtt__debug,  # pylint: disable=protected-access
            TEST_DEBUG_TRUE,
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

    def test_is_available_false_based_on__on_connection_failed(self) -> None:
        """Testing if is broker not available with result False."""

        # is_available is default false, so wee need to managed this by
        # calling __on_connect with success result_code
        self.mqtt._InelsMqtt__on_connect(  # pylint: disable=protected-access
            self.mqtt, Mock(), Mock(), 0, None
        )
        self.assertEqual(self.mqtt.is_available, True)

        # now we can call __on_connect_fail to test setter of is_available
        self.mqtt._InelsMqtt__on_connect_fail(  # pylint: disable=protected-access
            self.mqtt, Mock()
        )
        self.assertEqual(self.mqtt.is_available, False)

    @patch(
        f"{TEST_INELS_MQTT_CLASS_NAMESPACE}._InelsMqtt__connect", return_value=Mock()
    )
    @patch(f"{TEST_INELS_MQTT_NAMESPACE}.MqttClient.subscribe", return_value=Mock())
    def test_discovery_all_with_tree_messages(
        self, mock_connect, mock_broker_subscribe
    ) -> None:
        """Test discovery funct to find and register all interested topics."""

        # initialize three topics with status
        items = {
            "inels/45464654/status/01/457544": "rrqeraad",
            "inels/45464654/status/01/74544": "eeeqqq",
            "inels/45464654/status/01/8887": "adfadfefe",
            "some/kind/of/different/topic/in/broker": "adfadf",  # should be filtered out
        }

        for item in items.items():
            msg = type("msg", (object,), {"topic": item[0], "payload": item[1]})
            self.mqtt._InelsMqtt__on_discover(  # pylint: disable=protected-access
                self.mqtt, Mock(), msg
            )

        devices = self.mqtt.discover_all()
        self.assertEqual(len(devices), 3)

    @patch(
        f"{TEST_INELS_MQTT_CLASS_NAMESPACE}._InelsMqtt__connect", return_value=Mock()
    )
    @patch(f"{TEST_INELS_MQTT_NAMESPACE}.MqttClient.subscribe", return_value=Mock())
    def test_subscribe_message(self, mock_connect, mock_broker_subscribe) -> None:
        """Testing subscribtion of the message from the broker."""

        topic = "inels/45464654/status/01/457544"
        msg = type(
            "msg",
            (object,),
            {"topic": topic, "payload": "adfadfadf"},
        )

        self.mqtt._InelsMqtt__on_message(  # pylint: disable=protected-access
            self.mqtt, Mock(), msg
        )

        payload = self.mqtt.subscribe(topic=topic)

        self.assertEqual(msg.payload, payload)

    def test_message_property(self) -> None:
        """Test if message property returns right data."""
        dictionary = {
            "inels/555555/status/01/3423452435": "first",
            "inels/555555/status/01/3424524222": "second",
            "inels/555555/status/02/452435234": "third",
            "inels/222222/status/01/85034495": "fourth",
        }

        # fill up __message prop
        self.mqtt._InelsMqtt__messages = dictionary  # pylint: disable=protected-access

        self.assertIsNotNone(self.mqtt.messages)
        self.assertEqual(len(self.mqtt.messages), 4)
        self.assertDictEqual(self.mqtt.messages, dictionary)