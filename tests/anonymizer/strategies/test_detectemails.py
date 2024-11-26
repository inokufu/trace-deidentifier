from src.trace_deidentifier.anonymizer.strategies.detect_emails import (
    EmailDetectionStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace


class TestEmailDetectionStrategy:
    """Tests email detection and replacement in traces."""

    def test_anonymize_emails_in_trace(self) -> None:
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
                    }
                },
            }
        )

        strategy = EmailDetectionStrategy()
        strategy.anonymize(trace)

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
                }
            },
        }

        assert trace.data == expected
