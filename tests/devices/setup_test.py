"""Base class with all setings for device testing."""

from unittest.mock import Mock, patch
from inelsmqtt.const import (
    MQTT_HOST,
    MQTT_PASSWORD,
    MQTT_PORT,
    MQTT_PROTOCOL,
    MQTT_USERNAME,
    PROTO_5,
)

from tests.const import (
    DOMAIN,
    TEST_HOST,
    TEST_INELS_MQTT_CLASS_NAMESPACE,
    TEST_INELS_MQTT_NAMESPACE,
    TEST_PASSWORD,
    TEST_PORT,
    TEST_USER_NAME,
)


class DeviceSetup:
    """Setup class."""

    domain = DOMAIN

    patches = [
        patch(f"{TEST_INELS_MQTT_NAMESPACE}.mqtt.Client", return_value=Mock()),
        patch(
            f"{TEST_INELS_MQTT_CLASS_NAMESPACE}._InelsMqtt__connect",
            return_value=Mock(),
        ),
        patch(
            f"{TEST_INELS_MQTT_NAMESPACE}.mqtt.Client.username_pw_set",
            return_value=Mock(),
        ),
        patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.subscribe", return_value=Mock()),
        patch(f"{TEST_INELS_MQTT_CLASS_NAMESPACE}.is_subscribed", return_value=Mock()),
        patch(f"{TEST_INELS_MQTT_NAMESPACE}._LOGGER", return_value=Mock()),
    ]

    config = {
        MQTT_HOST: TEST_HOST,
        MQTT_PORT: TEST_PORT,
        MQTT_USERNAME: TEST_USER_NAME,
        MQTT_PASSWORD: TEST_PASSWORD,
        MQTT_PROTOCOL: PROTO_5,
    }
