from io import StringIO
from unittest.mock import MagicMock

from django.test import SimpleTestCase, override_settings

from care.utils import sms
from care.utils.sms.message import TextMessage


class BaseSmsBackendTests:
    sms_backend: str | None = None

    def setUp(self) -> None:
        self.settings_override = override_settings(SMS_BACKEND=self.sms_backend)
        self.settings_override.enable()

    def tearDown(self) -> None:
        self.settings_override.disable()


class ConsoleBackendTests(BaseSmsBackendTests, SimpleTestCase):
    sms_backend: str = "care.utils.sms.backend.console.ConsoleBackend"

    def test_console_stream_kwarg(self) -> None:
        stream = StringIO()
        connection = sms.initialize_backend(self.sms_backend, stream=stream)
        message = TextMessage("Content", "0600000000", ["0600000000"])
        connection.send_messages(message)
        messages = stream.getvalue().split("\n" + ("-" * 79) + "\n")
        self.assertIn("From: ", messages[0])


class AwsBackendTests(BaseSmsBackendTests, SimpleTestCase):
    sms_backend = "care.utils.sms.backend.sns.SnsBackend"

    def setUp(self) -> None:
        super().setUp()
        self._settings_override = override_settings(
            SNS_REGION="us-moon-3",
            SNS_ACCESS_KEY="AKIAFAKEACCESSKEYID",
            SNS_SECRET_KEY="fake_secret_access_key",
            SNS_ROLE_BASED_MODE=True,
        )
        self._settings_override.enable()

    def tearDown(self) -> None:
        self._settings_override.disable()
        super().tearDown()

    def test_send_messages(self) -> None:
        message = TextMessage(
            content="Here is the message",
            sender="+12065550100",
            recipients=["+441134960000"],
        )
        connection = sms.initialize_backend(self.sms_backend)
        connection.sns_client.publish = MagicMock()
        connection.send_message(message)
        connection.sns_client.publish.assert_called_with(
            PhoneNumber="+441134960000",
            Message="Here is the message",
        )
