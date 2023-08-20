import sys
import os
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
from src.routes import setup_routes
from src.redis_client import redis_client
import mock
import json

# Mocked Redis client
class MockRedisClient:
    def __init__(self):
        self.data = {}

    def incr(self, key):
        self.data[key] = self.data.get(key, 0) + 1
        return self.data[key]

    def lpush(self, key, value):
        self.data[key] = self.data.get(key, [])
        self.data[key].append(value)

@pytest.fixture
def client():
    # Create a custom mock Redis client behavior
    mock_redis = MockRedisClient()

    # Create a mock FastAPI app for testing
    app = FastAPI()
    setup_routes(app)

    # Patch the redis_client to return the mock instance
    with mock.patch("src.routes.redis_client", new=mock_redis):
        # Override the redis_client dependency in the app with the mock instance
        app.dependency_overrides[redis_client] = mock_redis
        yield TestClient(app)

def test_collect_api_positive(client):
    # Send a valid request with the `user_id` and `payload` fields using the testing client.
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)

    # Verify that the mock Redis client's incr and lpush methods were called as expected.
    assert response.status_code == 200
    assert response.json() == {"message": "Payload collected and stored"}

    # Verify that the mock Redis client's incr and lpush methods were called as expected.
    assert client.app.dependency_overrides[redis_client].incr("sequence_number") > 0
    assert client.app.dependency_overrides[redis_client].lpush("delivery_requests", json.dumps(payload)) == None
