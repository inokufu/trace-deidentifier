from unittest.mock import Mock

import pytest

from src.trace_deidentifier.anonymizer.strategies.detect_emails import (
    EmailDetectionStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace


class TestEmailDetectionStrategy:
    """Tests email detection and replacement in traces."""

    @pytest.fixture
    def strategy(self, mock_logger: Mock) -> EmailDetectionStrategy:
        """
        Create a EmailDetectionStrategy instance.

        :return: A strategy instance
        """
        strategy = EmailDetectionStrategy()
        strategy.logger = mock_logger
        return strategy

    def test_anonymize_emails_in_trace(self, strategy: EmailDetectionStrategy) -> None:
        """Test email replacement in a complete xAPI trace with emails in various contexts."""
        trace = Trace.model_construct(
            data={
                "actor": {
                    "name": "John Doe",
                    "mbox": "john.doe@company.com",
                    "description": "Contact at john.doe@company.com or backup@company.com",
                },
                "verb": {
                    "id": "http://example.com/verbs/sent",
                    "display": {"en-US": "sent email to support@company.com"},
                },
                "object": {
                    "definition": {
                        "name": {"en-US": "Email thread with admin@company.com"},
                        "extensions": {
                            "http://example.com/recipients": [
                                "recipient1@company.com",
                                "recipient2@company.com",
                            ],
                            "http://example.com/message": "Please contact admin@company.com",
                        },
                    },
                },
            },
        )

        strategy.anonymize(trace=trace)

        expected = {
            "actor": {
                "name": "John Doe",
                "mbox": "anonymous@anonymous.org",
                "description": "Contact at anonymous@anonymous.org or anonymous@anonymous.org",
            },
            "verb": {
                "id": "http://example.com/verbs/sent",
                "display": {"en-US": "sent email to anonymous@anonymous.org"},
            },
            "object": {
                "definition": {
                    "name": {"en-US": "Email thread with anonymous@anonymous.org"},
                    "extensions": {
                        "http://example.com/recipients": [
                            "anonymous@anonymous.org",
                            "anonymous@anonymous.org",
                        ],
                        "http://example.com/message": "Please contact anonymous@anonymous.org",
                    },
                },
            },
        }

        assert trace.data == expected

    @pytest.mark.parametrize(
        "email",
        [
            # Basic formats
            "simple@example.com",
            "very.common@example.com",
            "disposable.style.email.with+symbol@example.com",
            # Uncommon but valid local parts
            "other.email-with-hyphen@example.com",
            "fully-qualified-domain@example.com",
            "user.name+tag+sorting@example.com",
            "x@example.com",  # One-letter local part
            "example-indeed@strange-example.com",
            "test/test@test.com",  # Slash in local part
            "admin@mailserver1",  # No TLD required
            "example@s.example",  # Short domain
            # Complex local parts
            "#!$%&'*+-/=?^_`{}|~@example.org",  # Special chars
            "customer/department=shipping@example.com",
            "$A12345@example.com",  # Starting with special char
            "!def!xyz%abc@example.com",
        ],
    )
    def test_complex_email_formats(
        self,
        email: str,
        strategy: EmailDetectionStrategy,
    ) -> None:
        """
        Test email replacement for complex email formats.

        :param strategy: The strategy to test
        :param email: Email to test
        """
        trace = Trace.model_construct(data={"email": email})
        strategy.anonymize(trace=trace)
        assert trace.data["email"] == "anonymous@anonymous.org"
