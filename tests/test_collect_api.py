from fastapi.testclient import TestClient

from src.main import app 
from src.redis_client import redis_client
client = TestClient(app)


def test_collect_api():
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    assert response.status_code == 200
    assert response.json() == {"message": "Payload collected and stored"}
    assert redis_client.get("sequence_number") == '1'
