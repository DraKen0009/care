from care.utils.sms.message import TextMessage


class SmsBackendBase:
    """
    Base class for all SMS backends.

    Subclasses should override `send_messages`.
    """

    def __init__(self, fail_silently: bool = False, **kwargs) -> None:
        self.fail_silently = fail_silently

    def send_message(self, message: TextMessage) -> int:
        """
        Send one or more text messages.

        Args:
            messages (List[TextMessage]): List of messages to send.

        Raises:
            NotImplementedError: If not implemented in subclass.

        Returns:
            int: Number of messages sent.
        """
        raise NotImplementedError("Subclasses must implement `send_messages`.")
