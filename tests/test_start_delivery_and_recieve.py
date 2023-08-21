import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


class TestDeliveryThread(unittest.TestCase):

    @patch("src.delivery_thread.requests.post")
    def test_post_the_payload_success(self, mock_post):

        mock_response = mock_post.return_value
        mock_response.status_code = 200

        start_delivery_response = client.post("/start_delivery?port=5555")

        payload = {"user_id": "123456", "payload": "This is a test payload"}
        collect_api_response = client.post("/collect_api", json=payload)

        # Assert that requests.post was called with the expected arguments
        mock_post.assert_called_once()
        client.post("/stop_delivery")


if __name__ == "__main__":
    unittest.main()
