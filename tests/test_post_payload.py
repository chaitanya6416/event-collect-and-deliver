import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from requests import RequestException
from src.main import app
import time

client = TestClient(app)


class TestDeliveryThread(unittest.TestCase):

    @patch("src.delivery_thread.requests.post")
    def test_positive_post_the_payload(self, mock_post):

        mock_response = mock_post.return_value
        mock_response.status_code = 200

        client.post("/start_delivery?port=5555")

        payload = {"user_id": "123456", "payload": "This is a test payload"}
        client.post("/collect_api", json=payload)

        mock_post.assert_called_once()
        client.post("/stop_delivery")

    @patch("src.delivery_thread.requests.post")
    def test_positive_retry_post_the_payload(self, mock_post):
        client.post("/stop_delivery")
        mock_response_400 = MagicMock()
        mock_response_400.status_code = 400

        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200

        mock_post.side_effect = [mock_response_400, mock_response_200]

        client.post("/start_delivery?port=5555")

        payload = {"user_id": "123456", "payload": "This is a test payload"}
        client.post("/collect_api", json=payload)
        assert mock_post.call_count >= 1
        client.post("/stop_delivery")

    def test_negative_post_the_payload(self):
        # lets not mock the delivery post
        client.post("/start_delivery?port=5555")
        payload = {"user_id": "123456", "payload": "This is a test payload"}
        client.post("/collect_api", json=payload)
        self.assertRaises(RequestException)
        client.post("/stop_delivery")


if __name__ == "__main__":
    unittest.main()
