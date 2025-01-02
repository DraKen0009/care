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
    def __init__(self, fail_silently: bool = False, **kwargs) -> None:
        super().__init__(fail_silently=fail_silently, **kwargs)

        if not HAS_BOTO3 and not self.fail_silently:
            raise ImproperlyConfigured("Boto3 library is required but not installed.")

        self.region_name = getattr(settings, "SNS_REGION", None)
        self.access_key_id = getattr(settings, "SNS_ACCESS_KEY", None)
        self.secret_access_key = getattr(settings, "SNS_SECRET_KEY", None)

        self.sns_client = None
        if HAS_BOTO3:
            if settings.SNS_ROLE_BASED_MODE:
                if not self.region_name:
                    raise ImproperlyConfigured(
                        "AWS SNS is not configured. Check 'SNS_REGION' in settings."
                    )
                self.sns_client = boto3.client(
                    "sns",
                    region_name=settings.SNS_REGION,
                )
            else:
                if (
                    not self.region_name
                    or not self.access_key_id
                    or not self.secret_access_key
                ):
                    raise ImproperlyConfigured(
                        "AWS SNS credentials are not fully configured. Check 'SNS_REGION','SNS_SECRET_KEY', and 'SNS_ACCESS_KEY' in settings."
                    )
                self.sns_client = boto3.client(
                    "sns",
                    region_name=self.region_name,
                    aws_access_key_id=self.access_key_id,
                    aws_secret_access_key=self.secret_access_key,
                )

    def send_message(self, message: TextMessage) -> int:
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
