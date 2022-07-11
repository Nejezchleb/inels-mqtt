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
    MQTT_BROKER_CLIENT_NAME,
    MQTT_DISCOVER_TOPIC,
)

__version__ = VERSION

_LOGGER = logging.getLogger(__name__)

# when no topic were detected, then stop discovery
__DISCOVERY_TIMEOUT__ = DISCOVERY_TIMEOUT_IN_SEC
__CONNECTION_TIMEOUT__ = 15  # it has seconds for connecting to broker


class InelsMqtt:
    """Wrapper for mqtt client."""

    def __init__(
        self,
        host: str,
        port: int,
        user_name: str = None,
        password: str = None,
        debug: bool = False,
    ) -> None:
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
        self.__published = False

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
        start_time = datetime.now()
        self.__is_available = self.__tried_to_connect = False

        if self.__debug is True:
            self.client.on_log = self.__on_log

        self.client.on_connect = self.__on_connect
        self.client.on_connect_fail = self.__on_connect_fail
        self.client.connect(self.__host, self.__port, properties=None)
        self.client.loop_start()

        while self.__tried_to_connect is False:  # waiting for connection
            time.sleep(0.5)

            time_delta = datetime.now() - start_time
            if time_delta.total_seconds() > __CONNECTION_TIMEOUT__:
                # there is some kind of connection issue. Broker is not responding
                break

    def __on_log(
        self,
        client: MqttClient,  # pylint: disable=unused-argument
        userdata,  # pylint: disable=unused-argument
        level,  # pylint: disable=unused-argument
        buf,
    ) -> None:  # pylint: disable=unused-argument
        """Log every event fired with mqtt broker it is used
           only for Debuging purposes

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
        properties=None,  # pylint: disable=unused-argument
    ) -> None:
        """On connection callback function

        Args:
            client (MqttClient): instance of mqtt client
            properties (_type_, optional): Props from mqtt sets. Defaults None
        """
        self.__tried_to_connect = True
        self.__is_available = reason_code == 0

        _LOGGER.info(
            "Mqtt broker %s:%s %s",
            self.__host,
            self.__port,
            "is connected" if reason_code == 0 else "is not connected",
        )

    def __on_connect_fail(
        self, client: MqttClient, userdata  # pylint: disable=unused-argument
    ) -> None:  # pylint: disable=unused-argument
        """On connect failed callback function. Logging not
        successing broker connection.
        Args:
            client (MqttClient): Instance of mqtt client
        """
        self.__tried_to_connect = True
        self.__is_available = False
        self.__disconnect()
        _LOGGER.info(
            "Mqtt broker %s %s:%s failed on connection",
            MQTT_BROKER_CLIENT_NAME,
            self.__host,
            self.__port,
        )

    def publish(self, topic, payload, qos=0, retain=True, properties=None) -> bool:
        """Publish to mqtt broker. Will automatically connect
        establish all neccessary callback functions. Made
        publishing and disconnect from broker

        Args:
            topic (str): topic string where to publish
            payload (str): data content
            qos (int, optional): quality of service
              https://mosquitto.org/man/mqtt-7.html. Defaults to 0.
            retain (bool, optional): Broke will keep message after sending it
              to all subscribers. Defaults to True.
            properties (_type_, optional): Props from mqtt sets.
              Defaults to None.
        """
        self.__connect()
        self.client.on_publish = self.__on_publish

        self.__published = False
        self.client.publish(topic, payload, qos, retain, properties)

        start_time = datetime.now()

        while True:
            # there should be timeout to discover all topics
            time_delta = datetime.now() - start_time
            if time_delta.total_seconds() > __DISCOVERY_TIMEOUT__:
                self.__published = False
                break

            time.sleep(0.1)

        self.__disconnect()

        return self.__published

    def __on_publish(
        self,
        client: MqttClient,
        userdata,  # pylint: disable=unused-argument
        mid,  # pylint: disable=unused-argument
    ) -> None:
        """Callback function called after publish
          has been created. Will log it.

        Args:
            client (MqttClient): Instance of mqtt broker
            userdata (object): Published data
            mid (_type_): MID
        """
        self.__published = True
        _LOGGER.log(f"Client: {client}")

    def subscribe(self, topic, qos=0, options=None, properties=None) -> str:
        """Subscribe to selected topic. Will connect, set all
        callback function and subscribe to the topic. After that
        will automatically disconnect from broker.

        Args:
            topic (str): Topic string representation
            qos (_type_): Quality of service.
            options (_type_): Options is not used, but callback must
              have implemented
            properties (_type_, optional): Props from mqtt set.
              Defaults to None.
        """
        self.__connect()
        self.client.on_message = self.__on_message
        self.client.on_subscribe = self.__on_subscribe
        self.client.subscribe(topic, qos, options, properties)

        start_time = datetime.now()

        while True:
            # there should be timeout to discover all topics
            time_delta = datetime.now() - start_time
            if time_delta.total_seconds() > __DISCOVERY_TIMEOUT__:
                break

            time.sleep(0.1)

        self.__disconnect()
        return self.__messages[topic]

    def discovery_all(self) -> dict[str, str]:
        """Subscribe to selected topic. This method is primary used for
        subscribing with wild-card (#,+).
        When wild-card is used, then all topic matching this will
        be subscribed and collected therir payloads and topic representation.

        e.g.: prefix/status/groundfloor/# - will match all groundfloor topics
                    prefix/status/groundfloor/kitchen/temp - yes
                    prefix/status/groundfloor/linvingroom/temp - yes
                    prefix/status/firstfloor/bathroom/temp - no
                    prefix/status/groundfloor/kitchen/fridge/temp - yes

              prefix/status/groundfoor/+/temp - will get all groundfloor temp
                    prefix/status/groundfloor/kitchen/temp - yes
                    prefix/status/groundfloor/kitchen/lamp - no
                    prefix/status/groundfloor/livingroom/temp - yes
                    prefix/status/groundfloor/kitchen/fridge/temp - no

        Returns:
            dict[str, str]: Dictionary of all topics with their payloads
        """
        self.__connect()
        self.client.on_message = self.__on_discover
        self.client.on_subscribe = self.__on_subscribe
        self.client.subscribe(MQTT_DISCOVER_TOPIC, 0, None, None)

        self.__discover_start_time = datetime.now()

        while True:
            # there should be timeout to discover all topics
            time_delta = datetime.now() - self.__discover_start_time
            if time_delta.total_seconds() > __DISCOVERY_TIMEOUT__:
                break

            time.sleep(0.1)

        self.__disconnect()
        return self.__messages

    def __on_discover(
        self,
        client: MqttClient,  # pylint: disable=unused-argument
        userdata,  # pylint: disable=unused-argument
        msg,
    ) -> None:
        """Special callback function used only in discover_all function
        placed in on_message. It is the same as on_mesage callback func,
        but do different things

        Args:
            client (MqttClient): Mqtt broker instance
            msg (object): Topic with payload from broker
        """
        # set discovery_start_time to now evry message was returned
        # will be doing till messages will rising
        self.__discover_start_time = datetime.now()

        # pass only those who belongs to known device types
        device_type = msg.topic.split("/")[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]

        if device_type in DEVICE_TYPE_DICT:
            self.__messages[msg.topic] = msg.payload

    def __on_message(
        self,
        client: MqttClient,  # pylint: disable=unused-argument
        userdata,  # pylint: disable=unused-argument
        msg,
    ) -> None:
        """Callback function which is used for subscription

        Args:
            client (MqttClient): Instance of mqtt broker
            userdata (_type_): Date about user
            msg (object): Topic with payload from broker
        """
        device_type = msg.topic.split("/")[TOPIC_FRAGMENTS[FRAGMENT_DEVICE_TYPE]]

        if device_type in DEVICE_TYPE_DICT:
            self.__messages[msg.topic] = msg.payload

    def __on_subscribe(
        self,
        client: MqttClient,  # pylint: disable=unused-argument
        userdata,  # pylint: disable=unused-argument
        mid,  # pylint: disable=unused-argument
        granted_qos,  # pylint: disable=unused-argument
        properties=None,  # pylint: disable=unused-argument
    ):
        """Callback for subscribe function. Is called after subscribe to
        the topic. Will handle disconnection from mqtt broker loop

        Args:
            client (MqttClient): Instance of mqtt broker
            userdata (_type_): Data about user
            mid (_type_): MID
            granted_qos (_type_): Quality of service is granted
            properties (_type_, optional): Props from broker set.
                Defaults to None.
        """
        _LOGGER.info(mid)

    def __disconnect(self) -> None:
        """Disconnecting from broker and stopping broker's loop"""
        self.client.disconnect()
        self.client.loop_stop()

    def disconnect(self) -> None:
        """Disconnect mqtt client."""
        return self.__disconnect()
