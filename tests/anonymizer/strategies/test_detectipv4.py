# flake8: noqa: S104
from unittest.mock import Mock

import pytest

from src.trace_deidentifier.anonymizer.strategies.detect_ipsv4 import (
    Ipv4DetectionStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace


class TestIpv4DetectionStrategy:
    """Test suite for IPv4 detection strategy."""

    @pytest.fixture
    def strategy(self, mock_logger: Mock) -> Ipv4DetectionStrategy:
        """
        Create a Ipv4DetectionStrategy instance.

        :return: A strategy instance
        """
        strategy = Ipv4DetectionStrategy()
        strategy.logger = mock_logger
        return strategy

    @pytest.mark.parametrize(
        ("input_data", "expected_data"),
        [
            pytest.param(
                {"ip": "192.168.1.1"},
                {"ip": "0.0.0.0"},
                id="simple-ip",
            ),
            pytest.param(
                {"text": "IP address is 10.0.0.1 in this text"},
                {"text": "IP address is 0.0.0.0 in this text"},
                id="ip-in-text",
            ),
            pytest.param(
                {"ips": ["172.16.0.1", "192.168.0.1"]},
                {"ips": ["0.0.0.0", "0.0.0.0"]},
                id="multiple-ips",
            ),
            pytest.param(
                {"ip": "999.999.999.999"},
                {"ip": "0.0.0.0"},
                id="invalid-ip-numbers",
            ),
            pytest.param(
                {"ip": "001.002.003.004"},
                {"ip": "0.0.0.0"},
                id="ipv4-leading-zeros",
            ),
            pytest.param(
                {"ip": "192-168-0-1"},
                {"ip": "192-168-0-1"},
                id="ipv4-invalid-separators",
            ),
            pytest.param(
                {"nested": {"ip": "192.168.1.1"}},
                {"nested": {"ip": "0.0.0.0"}},
                id="nested-ipv4",
            ),
            pytest.param(
                {"not_ip": "just.some.dots.here"},
                {"not_ip": "just.some.dots.here"},
                id="dot-separated-text",
            ),
            pytest.param(
                {"safe": "text without ip"},
                {"safe": "text without ip"},
                id="no-ip",
            ),
        ],
    )
    def test_ipv4_detection(
        self,
        strategy: Ipv4DetectionStrategy,
        input_data: dict,
        expected_data: dict,
    ) -> None:
        """
        Test IPv4 detection and replacement in various contexts.

        :param strategy: The strategy to test
        :param input_data: Input data with IPs to test
        :param expected_data: Expected result after anonymization
        """
        trace = Trace.model_construct(data=input_data)
        strategy.anonymize(trace)
        assert trace.data == expected_data
