from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from care.utils.sms.backend.base import SmsBackendBase
from care.utils.sms.message import TextMessage

try:
    import boto3
    from botocore.exceptions import ClientError

    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False


class SnsBackend(SmsBackendBase):
    """
    Sends SMS messages using AWS SNS.
    """

    def __init__(self, fail_silently: bool = False, **kwargs) -> None:
        """
        Initialize the SNS backend.

        Args:
            fail_silently (bool): Whether to suppress exceptions during initialization. Defaults to False.
            **kwargs: Additional arguments for backend configuration.

        Raises:
            ImproperlyConfigured: If required AWS SNS settings are missing or boto3 is not installed.
        """
        super().__init__(fail_silently=fail_silently, **kwargs)

        if not HAS_BOTO3 and not self.fail_silently:
            raise ImproperlyConfigured("Boto3 library is required but not installed.")

        self.region_name = getattr(settings, "SNS_REGION", None)
        self.access_key_id = getattr(settings, "SNS_ACCESS_KEY", None)
        self.secret_access_key = getattr(settings, "SNS_SECRET_KEY", None)

        self.sns_client = None
        if HAS_BOTO3:
            if getattr(settings, "SNS_ROLE_BASED_MODE", False):
                if not self.region_name:
                    raise ImproperlyConfigured(
                        "AWS SNS is not configured. Check 'SNS_REGION' in settings."
                    )
                self.sns_client = boto3.client(
                    "sns",
                    region_name=self.region_name,
                )
            else:
                if (
                    not self.region_name
                    or not self.access_key_id
                    or not self.secret_access_key
                ):
                    raise ImproperlyConfigured(
                        "AWS SNS credentials are not fully configured. Check 'SNS_REGION', 'SNS_ACCESS_KEY', and 'SNS_SECRET_KEY' in settings."
                    )
                self.sns_client = boto3.client(
                    "sns",
                    region_name=self.region_name,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                )

    def send_message(self, message: TextMessage) -> int:
        """
        Send a text message using AWS SNS.

        Args:
            message (TextMessage): The message to be sent.

        Returns:
            int: The number of messages successfully sent.
        """
        if not self.sns_client:
            return 0

        successful_sends = 0
        for recipient in message.recipients:
            try:
                self.sns_client.publish(
                    PhoneNumber=recipient,
                    Message=message.content,
                )
                successful_sends += 1
            except ClientError as error:
                if not self.fail_silently:
                    raise error
        return successful_sends
