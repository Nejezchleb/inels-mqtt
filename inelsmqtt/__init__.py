"""Library specified for inels-mqtt."""
import logging
import time

from datetime import datetime

from paho.mqtt.client import Client as MqttClient, MQTTv5

from .const import (
    VERSION,
    DEVICE_TYPE_DICT,
    FRAGMENT_DEVICE_TYPE,
    TOPIC_FRAGMENTS,
    DISCOVERY_TIMEOUT_IN_SEC,
    MQTT_BROKER_CLIENT_NAME
)

__version__ = VERSION

_LOGGER = logging.getLogger(__name__)

# when no topic were detected, then stop discovery
__DISCOVERY_TIMEOUT__ = DISCOVERY_TIMEOUT_IN_SEC


class InelsMqtt:
    """Wrapper for mqtt client."""

    def __init__(self, host: str, port: int, user_name: str = None,
                 password: str = None, debug: bool = False) -> None:
        """InelsMqtt instance initialization.

        Args:
            host (str): mqtt broker host. Can be IP address
            port (int): broker port on which listening
            user_name (str): user name to sign in. It is optional
            password (str): password to auth into the broker. It is optional
            debug (bool): flag for debuging mqtt comunication. Default False
        """
        self.__host = host
        self.__port = port
        self.__user_name = user_name
        self.__password = password
        self.__debug = debug
        self.__messages = dict[str, str]()
        self.__is_available = False
        self.__tried_to_connect = False
        self.__discover_start_time = None

        self.client = MqttClient(MQTT_BROKER_CLIENT_NAME, protocol=MQTTv5)

        if self.__user_name is not None and self.__password is not None:
            self.client.username_pw_set(self.__user_name, self.__password)

    @property
    def messages(self) -> dict[str, str]:
        """List of all messages

        Returns:
            dist[str, str]: List of all messages (topics)
            from broker subscribed.
            It is key-value dictionary. Key is topic and value
            is payload of topic
        """
        return self.__messages

    @property
    def is_available(self) -> bool:
        """Is broker available

        Returns:
            bool: Get information of mqtt broker availability
        """
        return self.__is_available

    def test_connection(self) -> bool:
        """Test connection. It's used only for connection
            testing. After that is disconnected
        Returns:
            bool: Is broker available or not
        """
        self.__connect()
        self.__disconnect()

        return self.__is_available

    def __connect(self) -> None:
        """Create connection and register callback function to neccessary
        purposes.
        """
        self.__is_available = self.__tried_to_connect = False

        if self.__debug is True:
            self.client.on_log = self.__on_log

        self.client.on_connect = self.__on_connect
        self.client.on_connect_fail = self.__on_connect_fail
        self.client.connect(self.__host, self.__port, properties=None)
        self.client.loop_start()

        while self.__tried_to_connect is False:  # waiting for connection
            time.sleep(0.1)

    def __on_log(self,
                 client: MqttClient,  # pylint: disable=unused-argument
                 userdata,  # pylint: disable=unused-argument
                 level, buf) -> None:  # pylint: disable=unused-argument
        """Log every event fired with mqtt broker it is used only for Debuging purposes

        Args:
            client (MqttClient): _description_
            userdata (_type_): _description_
            level (_type_): _description_
            buf (_type_): _description_
        """
        _LOGGER.info(buf, __name__)

    def __on_connect(
        self,
        client: MqttClient,  # pylint: disable=unused-argument
        userdata,  # pylint: disable=unused-argument
        flag,  # pylint: disable=unused-argument
        reason_code,
        properties=None  # pylint: disable=unused-argument
    ) -> None:
        """On connect callback function."""
        self.__tried_to_connect = True
        self.__is_available = reason_code == 0

        _LOGGER.info(
            "Mqtt broker %s:%s %s",
            self.__host,
            self.__port,
            "is connected" if reason_code == 0 else "is not connected",
        )

    def __on_connect_fail(
            self,
            client: MqttClient,  # pylint: disable=unused-argument
            userdata) -> None:  # pylint: disable=unused-argument
        """Fail with connecting."""

        self.__tried_to_connect = True
        self.__disconnect()
        _LOGGER.info(
            "Mqtt broker %s %s:%s failed on connection",
            MQTT_BROKER_CLIENT_NAME,
            self.__host,
            self.__port,
        )

    def publish(self, topic, payload, qos=0,
                retain=True, properties=None) -> None:
        """Publish to the broker."""
        self.__connect()
        self.client.on_publish = self.__on_publish
        self.client.publish(topic, payload, qos, retain, properties)
        self.__disconnect()

    def __on_publish(self, client: MqttClient,
                     userdata, mid) -> None:  # pylint: disable=unused-argument
        """On publish callback function."""
        _LOGGER.log(f'Client: {client}')

    def subscribe(self, topic, qos, options, properties=None) -> None:
        """Subscribe to the broker."""
        self.__connect()
        self.client.on_message = self.__on_message
        self.client.on_subscribe = self.__on_subscribe
        self.client.subscribe(topic, qos, options, properties)
        self.__disconnect()

    def discover_all(self, topic: str) -> dict[str, str]:
        """Discover all devivce."""
        self.__connect()
        self.client.on_message = self.__on_discover
        self.client.on_subscribe = self.__on_subscribe
        self.client.subscribe(topic, 0, None, None)

        self.__discover_start_time = datetime.now()

        while True:
            # there should be timeout to discover all topics
            time_delta = datetime.now() - self.__discover_start_time
            if time_delta.total_seconds() > __DISCOVERY_TIMEOUT__:
                break

            time.sleep(0.1)

        self.__disconnect()
        return self.__messages.items()

    def __on_discover(
            self,
            client: MqttClient,  # pylint: disable=unused-argument
            userdata, msg) -> None:  # pylint: disable=unused-argument
        """Callback function with returned payload."""
        self.__discover_start_time = datetime.now()

        # pass only those who belongs to known device types
        device_type = msg.topic.split("/")[
            TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]

        if device_type in DEVICE_TYPE_DICT:
            self.__messages[msg.topic] = msg.payload

    def __on_message(self, client: MqttClient, userdata, msg) -> None:
        """Callback function with returned payload."""

    def __on_subscribe(
        self, client: MqttClient, userdata, mid, granted_qos, properties=None
    ):
        """Callback function for subscribtion."""

    def __disconnect(self) -> None:
        """Cloase loop and disconnect from the broker."""
        self.client.disconnect()
        self.client.loop_stop()
