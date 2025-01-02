import sys
import threading

from care.utils.sms.backend.base import SmsBackendBase
from care.utils.sms.message import TextMessage


class ConsoleBackend(SmsBackendBase):
    """
    Outputs SMS messages to the console for debugging.
    """

    def __init__(self, *args, stream=None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.stream = stream or sys.stdout
        self._lock = threading.RLock()

    def send_messages(self, message: TextMessage) -> int:
        sent_count = 0
        with self._lock:
            for recipient in message.recipients:
                self.stream.write(
                    f"From: {message.sender}\nTo: {recipient}\nContent: {message.content}\n{'-' * 50}\n"
                )
                sent_count += 1
        return sent_count
