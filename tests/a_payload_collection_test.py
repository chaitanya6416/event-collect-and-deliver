import pytest
from fastapi.testclient import TestClient
from main import app
import routes

client = TestClient(app)


class RedisMock:
    def __init__(self):
        self.streams = {}

    def xadd(self, stream_name, payload):
        print(f"{payload=} is added to {stream_name=}")
        assert True


def test_collect_api_endpoint(monkeypatch):

    def get_a_redis_mock_instance():
        return RedisMock()

    # monkey patch before calling
    monkeypatch.setattr(routes, 'get_redis_instance',
                        get_a_redis_mock_instance)

    payload = {"user_id": "123456", "payload": "This is a test payload"}
    client.post("/collect_api", json=payload)
