from unittest.mock import Mock

import pytest

from src.trace_deidentifier.anonymizer.strategies.detect_geolocation import (
    GeoLocationDetectionStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace


class TestGeoLocationDetectionStrategy:
    """Test suite for GeoLocationDetectionStrategy."""

    @pytest.fixture
    def strategy(self, mock_logger: Mock) -> GeoLocationDetectionStrategy:
        """
        Create a GeoLocationDetectionStrategy instance.

        :return: A strategy instance
        """
        strategy = GeoLocationDetectionStrategy()
        strategy.logger = mock_logger
        return strategy

    @pytest.mark.parametrize(
        ("input_data", "expected_data"),
        [
            # Decimal degrees
            pytest.param(
                {"location": "45.123°N 2.345°E"},
                {"location": '{"lat":0,"lon":0}'},
                id="decimal-degrees",
            ),
            # DMS format
            pytest.param(
                {"location": "48°51'24\"N 2°21'08\"E"},
                {"location": '{"lat":0,"lon":0}'},
                id="dms-format",
            ),
            # JSON format
            pytest.param(
                {"location": '{"lat": 45.123, "lng": 2.345}'},
                {"location": '{"lat":0,"lon":0}'},
                id="json-format",
            ),
            # UTM format
            pytest.param(
                {"location": "31U 430959 5239573"},
                {"location": '{"lat":0,"lon":0}'},
                id="utm-format",
            ),
            # Nested structures
            pytest.param(
                {
                    "data": {
                        "user": {
                            "location": "45.123°N 2.345°E",
                            "other": "data",
                        },
                    },
                },
                {
                    "data": {
                        "user": {
                            "location": '{"lat":0,"lon":0}',
                            "other": "data",
                        },
                    },
                },
                id="nested-location",
            ),
            # Multiple occurrences
            pytest.param(
                {
                    "locations": [
                        "45.123°N 2.345°E",
                        '{"lat": 48.8534, "lng": 2.3488}',
                    ],
                },
                {
                    "locations": [
                        '{"lat":0,"lon":0}',
                        '{"lat":0,"lon":0}',
                    ],
                },
                id="multiple-formats",
            ),
            # Text with numbers that should not be detected
            pytest.param(
                {"text": "Temperature is 45.123° today and angle is 90°"},
                {"text": "Temperature is 45.123° today and angle is 90°"},
                id="text-with-numbers",
            ),
            pytest.param(
                {"text": "Score: 31U points, Time: 430959ms"},
                {"text": "Score: 31U points, Time: 430959ms"},
                id="utm-like-numbers",
            ),
            pytest.param(
                {
                    "text": "Coordinates in text 45.123°N 2.345°E and some other numbers 42.5, 123.45",
                },
                {
                    "text": 'Coordinates in text {"lat":0,"lon":0} and some other numbers 42.5, 123.45',
                },
                id="mixed-content",
            ),
            # No coordinates
            pytest.param(
                {"text": "Just some random text"},
                {"text": "Just some random text"},
                id="no-coordinates",
            ),
        ],
    )
    def test_geo_location_detection(
        self,
        strategy: GeoLocationDetectionStrategy,
        input_data: dict,
        expected_data: dict,
    ) -> None:
        """
        Test geographic coordinate detection and replacement in various formats.

        :param strategy: The strategy to test
        :param input_data: Input data
        :param expected_data: Expected result after anonymization
        """
        trace = Trace.model_construct(data=input_data)
        strategy.anonymize(trace)
        assert trace.data == expected_data
