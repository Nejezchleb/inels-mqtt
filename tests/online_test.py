"""Online tests.
"""
from unittest import TestCase
from inelsmqtt import InelsMqtt


class OnlineTest(TestCase):
    """Discovery class tests

    Args:
        TestCase (_type_): Base class of unit testing
    """

    def setUp(self) -> None:
        """Setup."""

    def tearDown(self) -> None:
        """Tear down."""

    def test_connect(self) -> None:
        """Connect test."""
        config = {
            "host": "192.168.2.5",
            "port": 2883,
            "username": "ufo",
            "password": "ufoufoufo",
            "protocol": 5,
        }

        mqtt = InelsMqtt(config)
        result = mqtt.test_connection()

        self.assertTrue(result)
