from .regex_detect import RegexDetectionStrategy


class EmailDetectionStrategy(RegexDetectionStrategy):
    """
    Strategy to replace emails in all fields.

    It uses a regex for HTML email inputs from https://html.spec.whatwg.org/multipage/input.html#e-mail-state-(type%3Demail)
    which is a simplified version of the RFC 5322
    """

    def __init__(self):
        super().__init__(
            pattern=r"[a-zA-Z0-9.!#$%&\'*+\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*",
            replacement="anonymous@anonymous.org",
        )
