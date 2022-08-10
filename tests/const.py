"""Constances for testing purposes."""

TEST_HOST = "127.0.0.1"
TEST_PORT = 9883
TEST_USER_NAME = "test"
TEST_PASSWORD = "test_password"
TEST_DEBUG_TRUE = True
TEST_DEBUG_FALSE = False

TEST_INELS_MQTT_NAMESPACE = "inelsmqtt"
TEST_INELS_MQTT_CLASS_NAMESPACE = "inelsmqtt.InelsMqtt"

TEST_SWITCH_TOPIC_STATE = "inels/status/4254524524/02/452454"
TEST_SWITCH_TOPIC_SET = "inels/set/4254524524/02/452454"
TEST_SWITICH_TOPIC_CONNECTED = "inels/connected/4254524524/02/452454"

TEST_AVAILABILITY_ON = "on\n"
TEST_AVAILABILITY_OFF = "off\n"

TEST_SENSOR_TOPIC_STATE = "inels/status/4254524524/10/454354"
TEST_SENSOR_TOPIC_CONNECTED = "inels/connected/4254524524/10/454354"
TEST_TEMPERATURE_DATA = b"00\nB4\n0A\n6E\n0A\n"

TEST_LIGHT_DIMMABLE_TOPIC_STATE = "inels/status/4254524524/05/88556633"
TEST_LIGHT_DIMMABLE_CONNECTED = "inels/connected/4254524524/05/88556633"
TEST_LIGH_STATE_HA_VALUE = 20
TEST_LIGH_STATE_INELS_VALUE = b"C9\n4F\n"
TEST_LIGHT_SET_INELS_VALUE = "01 C9 4F"

TEST_COVER_RFJA_12_TOPIC_STATE = "inels/status/4254524524/03/444555225"
TEST_COVER_RFJA_12_TOPIC_CONNECTED = "inels/connected/4254524524/03/444555225"
TEST_COVER_RFJA_12_INELS_STATE_OPEN = b"03\n01\n"
TEST_COVER_RFJA_12_INELS_STATE_CLOSED = b"03\n00\n"
TEST_COVER_RFJA_12_HA_STATE_OPEN = "open"
TEST_COVER_RFJA_12_HA_STATE_CLOSED = "closed"
TEST_COVER_RFJA_12_SET_OPEN = "02 00 00"
TEST_COVER_RFJA_12_SET_CLOSE = "01 00 00"
TEST_COVER_RFJA_12_SET_STOP = "04 00 00"
