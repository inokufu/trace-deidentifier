from unittest.mock import Mock

import pytest

from src.trace_deidentifier.anonymizer.strategies.detect_ipsv6 import (
    Ipv6DetectionStrategy,
)
from src.trace_deidentifier.common.models.trace import Trace


class TestIpv6DetectionStrategy:
    """Test suite for IPv6 detection strategy."""

    @pytest.fixture
    def strategy(self, mock_logger: Mock) -> Ipv6DetectionStrategy:
        """
        Create a Ipv6DetectionStrategy instance.

        :return: A strategy instance
        """
        strategy = Ipv6DetectionStrategy()
        strategy.logger = mock_logger
        return strategy

    @pytest.mark.parametrize(
        ("input_data", "expected_data"),
        [
            pytest.param(
                {"ip": "2001:db8::1"},
                {"ip": "::"},
                id="simple-ipv6",
            ),
            pytest.param(
                {"text": "IPv6 is 2001:0db8:85a3:0000:0000:8a2e:0370:7334 here"},
                {"text": "IPv6 is :: here"},
                id="ipv6-in-text",
            ),
            pytest.param(
                {"ips": ["2001:db8::1", "fe80::1"]},
                {"ips": ["::", "::"]},
                id="multiple-ipv6s",
            ),
            pytest.param(
                {"ip": "fe80::dead:beef"},
                {"ip": "::"},
                id="link-local",
            ),
            pytest.param(
                {"ip": "::1"},
                {"ip": "::"},
                id="localhost-ipv6",
            ),
            pytest.param(
                {"nested": {"ipv6": "fe80::1"}},
                {"nested": {"ipv6": "::"}},
                id="nested-ipv6",
            ),
            pytest.param(
                {"safe": "no:colons:here"},
                {"safe": "no:colons:here"},
                id="colon-text",
            ),
            pytest.param(
                {"safe": "text without ip"},
                {"safe": "text without ip"},
                id="no-ipv6",
            ),
        ],
    )
    def test_ipv6_detection(
        self,
        strategy: Ipv6DetectionStrategy,
        input_data: dict,
        expected_data: dict,
    ) -> None:
        """
        Test IPv6 detection and replacement in various contexts.

        :param strategy: The strategy to test
        :param input_data: Input data with IPs to test
        :param input_data: Expected result after anonymization
        """
        trace = Trace.model_construct(data=input_data)
        strategy.anonymize(trace)
        assert trace.data == expected_data
