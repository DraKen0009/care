from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from care.utils.sms.backend.base import SmsBackendBase


class TextMessage:
    """
    Represents a text message for transmission to one or more recipients.
    """

    def __init__(
        self,
        content: str = "",
        sender: str | None = None,
        recipients: list[str] | None = None,
        backend: type["SmsBackendBase"] | None = None,
    ) -> None:
        """
        Initialize a TextMessage instance.

        Args:
            content (str): The message content.
            sender (Optional[str]): The sender's phone number.
            recipients (Optional[List[str]]): List of recipient phone numbers.
            backend (Optional[SmsBackendBase]): Backend for sending the message.
        """
        self.content = content
        self.sender = sender or getattr(settings, "DEFAULT_SMS_SENDER", "")
        self.recipients = recipients or []
        self.backend = backend

        if isinstance(self.recipients, str):
            raise ValueError("Recipients should be a list of phone numbers.")

    def establish_backend(self, fail_silently: bool = False) -> "SmsBackendBase":
        """
        Obtain or initialize the backend for sending messages.

        Args:
            fail_silently (bool): Whether to suppress errors during backend initialization.

        Returns:
            SmsBackendBase: An instance of the configured backend.
        """
        if not self.backend:
            self.backend = get_sms_backend(fail_silently=fail_silently)
        return self.backend

    def dispatch(self, fail_silently: bool = False) -> int:
        """
        Send the message to all designated recipients.

        Args:
            fail_silently (bool): Whether to suppress errors during message sending.

        Returns:
            int: Count of successfully sent messages.
        """
        if not self.recipients:
            return 0

        connection = self.establish_backend(fail_silently)
        return connection.send_messages([self])


def initialize_backend(
    backend_name: str | None = None, fail_silently: bool = False, **kwargs
) -> "SmsBackendBase":
    """
    Load and configure an SMS backend.

    Args:
        backend_name (Optional[str]): The dotted path to the backend class. If None, the default backend from settings is used.
        fail_silently (bool): Whether to handle exceptions quietly. Defaults to False.

    Returns:
        SmsBackendBase: An initialized instance of the specified SMS backend.
    """
    backend_class = import_string(backend_name or settings.SMS_BACKEND)
    return backend_class(fail_silently=fail_silently, **kwargs)


def send_text_message(
    content: str = "",
    sender: str | None = None,
    recipients: str | list[str] | None = None,
    fail_silently: bool = False,
    backend_instance: type["SmsBackendBase"] | None = None,
) -> int:
    """
    Send a single SMS message to one or more recipients.

    Args:
        content (str): The message content to be sent. Defaults to an empty string.
        sender (Optional[str]): The sender's phone number. Defaults to None.
        recipients (Union[str, List[str], None]): A single recipient or a list of recipients. Defaults to None.
        fail_silently (bool): Whether to suppress exceptions during sending. Defaults to False.
        backend_instance (Optional[SmsBackendBase]): A pre-configured SMS backend instance. Defaults to None.

    Returns:
        int: The number of messages successfully sent.
    """
    if isinstance(recipients, str):
        recipients = [recipients]
    message = TextMessage(
        content=content, sender=sender, recipients=recipients, backend=backend_instance
    )
    return message.dispatch(fail_silently=fail_silently)


def get_sms_backend(
    backend_name: str | None = None, fail_silently: bool = False, **kwargs
) -> "SmsBackendBase":
    """
    Load and return an SMS backend instance.

    Args:
        backend_name (Optional[str]): The dotted path to the backend class. If None, the default backend from settings is used.
        fail_silently (bool): Whether to suppress exceptions quietly. Defaults to False.
        **kwargs: Additional arguments passed to the backend constructor.

    Returns:
        SmsBackendBase: An initialized instance of the specified SMS backend.
    """
    return initialize_backend(
        backend_name=backend_name or settings.SMS_BACKEND,
        fail_silently=fail_silently,
        **kwargs,
    )
