from fastapi.testclient import TestClient

from src.main import app
from src.redis_client import redis_client
client = TestClient(app)


def test_postive_collect_api():
    redis_client.flushall()
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Payload collected and stored"}
    assert redis_client.get("sequence_number") == '1'
    redis_client.flushall()


def test_negative_collect_api():
    redis_client.flushall()
    payload = {"payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    assert response.status_code == 400
    redis_client.flushall()
