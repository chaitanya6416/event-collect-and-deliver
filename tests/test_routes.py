import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from fastapi import FastAPI
from routes import setup_routes
from redis_client import redis_client  # Import the actual redis_client here


# Mocked Redis client
class MockRedisClient:
    def __init__(self):
        self.data = {}

    def incr(self, key):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    def lpush(self, key, value):
        self.data[key] = self.data.get(key, [])
        self.data[key].insert(0, value)


# Mock FastAPI app
class MockApp(FastAPI):
    def __init__(self):
        super().__init__()
        setup_routes(self)


@pytest.fixture
def client():
    mock_redis = MockRedisClient()
    app = MockApp()
    app.dependency_overrides[redis_client] = mock_redis
    return TestClient(app)


def test_collect_api(client):
    payload = {"user_id": "user123", "payload": "data"}
    response = client.post("/collect_api", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Payload collected and stored"}


if __name__ == "__main__":
    pytest.main(["-sv", __file__])
