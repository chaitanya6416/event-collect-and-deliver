from fastapi.testclient import TestClient

from src.main import app 

client = TestClient(app)


def false_test_main():
    response = client.get("/")
    assert response.status_code != 200
