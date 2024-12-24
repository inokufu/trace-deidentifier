from .regex_detect import RegexDetectionStrategy


class Ipv6DetectionStrategy(RegexDetectionStrategy):
    """Strategy to replace IPv6 addresses in all fields."""

    def __init__(self) -> None:
        """
        Initialize IPv6 detection with patterns matching common IP formats.

        Prioritizes catching potential IP addresses over strict validation to ensure better privacy protection.
        """
        super().__init__(
            pattern=r"(?<![\w])(::[0-9a-fA-F]{1,4}|([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4})(?![\w:.])",
            replacement="::",
        )
