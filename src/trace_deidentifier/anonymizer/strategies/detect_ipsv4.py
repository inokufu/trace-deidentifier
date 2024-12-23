from .regex_detect import RegexDetectionStrategy


class Ipv4DetectionStrategy(RegexDetectionStrategy):
    """Strategy to replace IPv4 addresses in all fields."""

    def __init__(self) -> None:
        """
        Initialize IPv4 detection with patterns matching common IP formats.

        Prioritizes catching potential IP addresses over strict validation to ensure better privacy protection.
        """
        super().__init__(
            pattern=r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}",
            replacement="0.0.0.0",  # noqa: S104
        )
