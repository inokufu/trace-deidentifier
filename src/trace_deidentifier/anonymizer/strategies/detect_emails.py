from .regex_detect import RegexDetectionStrategy


class EmailDetectionStrategy(RegexDetectionStrategy):
    """
    Strategy to replace emails in all fields.

    It uses a regex for HTML email inputs from https://html.spec.whatwg.org/multipage/input.html#e-mail-state-(type%3Demail)
    which is a simplified version of the RFC 5322
    """

    def __init__(self) -> None:
        """Initialize the email detection strategy with a regex pattern, and replace most common formats with 'anonymous@anonymous.org'."""
        super().__init__(
            pattern=r"[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",
            replacement="anonymous@anonymous.org",
        )
