from unittest.mock import Mock

import pytest
from fastapi import FastAPI, Request, status
from fastapi.testclient import TestClient

from src.trace_deidentifier.anonymizer.anonymizer import Anonymizer
from src.trace_deidentifier.api.dependencies import get_anonymizer
from src.trace_deidentifier.api.routers.anonymize import router


class TestAnonymize:
    """Test suite for the anonymize endpoint."""

    @pytest.fixture
    def mock_request(self, mock_logger: Mock) -> Request:
        """
        Create a mocked request with logger.

        :param mock_logger: Mocked logger
        :return: Mocked FastAPI Request object
        """
        request = Mock(spec=Request)
        request.state.logger = mock_logger
        return request

    @pytest.fixture
    def mock_anonymizer(self) -> Mock:
        """
        Create a mocked Anonymizer instance.

        :return: Mocked Anonymizer with configured anonymize method
        """
        return Mock(spec=Anonymizer)

    @pytest.fixture
    def app(self, mock_anonymizer: Mock) -> FastAPI:
        """
        Create a test FastAPI app with mocked anonymizer.

        :param mock_anonymizer: Mocked Anonymizer instance
        :return: Configured FastAPI test app
        """
        app = FastAPI()
        app.dependency_overrides[get_anonymizer] = lambda: mock_anonymizer
        app.include_router(router)
        return app

    @pytest.fixture
    def client(self, app: FastAPI) -> TestClient:
        """
        Create a test client.

        :param app: FastAPI test app
        :return: Configured test client
        """
        return TestClient(app)

    @pytest.mark.asyncio
    async def test_get_anonymizer(self, mock_request: Request) -> None:
        """
        Test anonymizer dependency initialization.

        :param mock_request: Mocked request with logger
        """
        anonymizer = await get_anonymizer(mock_request)

        assert isinstance(anonymizer, Anonymizer)
        assert len(anonymizer.strategies) > 0
        assert anonymizer.logger == mock_request.state.logger

    def test_anonymize_trace_success(
        self,
        client: TestClient,
        mock_anonymizer: Mock,
    ) -> None:
        """
        Test successful trace anonymization.

        :param client: FastAPI test client
        :param mock_anonymizer: Mocked Anonymizer instance
        """
        input_data = {
            "trace": {
                "data": {
                    "actor": {
                        "mbox": "mailto:john@doe.com",
                    },
                    "object": {
                        "id": "http://example.com/activities/course-001",
                    },
                    "verb": {"id": "http://example.com/verbs/completed"},
                },
            },
        }

        response = client.post("/anonymize", json=input_data)

        assert response.status_code == status.HTTP_200_OK
        assert "trace" in response.json()
        mock_anonymizer.anonymize.assert_called_once()

    def test_anonymize_trace_invalid_input(self, client: TestClient) -> None:
        """
        Test trace anonymization with invalid input format.

        :param client: FastAPI test client
        :asserting: Returns 422 status code with validation error details
        """
        # Input qui ne correspond pas au schéma attendu
        invalid_data = {"invalid": "data"}

        response = client.post("/anonymize", json=invalid_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "detail" in response.json()
