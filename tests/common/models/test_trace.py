import pytest

from src.trace_deidentifier.common.models.trace import InvalidTraceError, Trace


class TestTrace:
    """Test suite for Trace model."""

    def test_valid_trace(self) -> None:
        """Test creating a trace with valid xAPI data."""
        valid_data = {
            "actor": {"name": "test", "mbox": "mailto:test@test.com"},
            "verb": {"id": "http://example.com/verbs/test"},
            "object": {"id": "http://example.com/activities/test"},
        }
        trace = Trace(data=valid_data)
        assert trace.data == valid_data

    @pytest.mark.parametrize(
        "input_data",
        [
            pytest.param(None, id="missing-dict"),
            pytest.param({}, id="empty-dict"),
            pytest.param({"not": "xapi"}, id="invalid-data"),
            pytest.param({"actor": {}}, id="missing-required-fields"),
        ],
    )
    def test_invalid_trace_formats(self, input_data: dict | None) -> None:
        """
        Test various invalid trace formats.

        :param input_data: Invalid trace data to test
        :type input_data: dict
        """
        with pytest.raises(InvalidTraceError):
            Trace(data=input_data)
