from .regex_detect import RegexDetectionStrategy


class GeoLocationDetectionStrategy(RegexDetectionStrategy):
    """
    Strategy to detect and replace complete geographic coordinates.

    Only matches patterns that contain both latitude and longitude together, to avoid false positives.
    """

    def __init__(self) -> None:
        """
        Initialize coordinate detection matching coordinate pairs.

        - Decimal degrees (e.g. "45.123°N 2.345°E")
        - DMS pairs (e.g. "48°51'24"N 2°21'08"E")
        - JSON format (e.g. {"lat": 45.123, "lng": 2.345})
        - UTM format (e.g. "31U 430959 5239573")
        """
        patterns = [
            # Decimal degrees with cardinal directions
            r"-?\d+\.?\d*°[NS][\s,]+-?\d+\.?\d*°[EW]",  # 45.123°N 2.345°E
            # Complete DMS pairs
            r"\d{1,3}°\d{1,2}\'(?:\d{1,2}(?:\.\d+)?)?\"[NS][\s,]+\d{1,3}°\d{1,2}\'(?:\d{1,2}(?:\.\d+)?)?\"[EW]",  # 48°51'24"N 2°21'08"E
            # JSON format
            r'\{["\']lat["\']:\s*-?\d+\.?\d*,\s*["\'](?:lon|lng)["\']:\s*-?\d+\.?\d*\}',  # {"lat":45.123,"lng":2.345}
            # UTM format
            r"\d{2}\s*[A-Z]\s+\d{6}\s+\d{7}",  # 31U 430959 5239573
        ]
        pattern = "|".join(f"({p})" for p in patterns)
        super().__init__(
            pattern=pattern,
            replacement='{"lat":0,"lon":0}',
        )
