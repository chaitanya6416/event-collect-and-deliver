''' we are testing /start_delivery endpoint '''

import threading
import time
from fastapi.testclient import TestClient

from src.main import app
from src.redis_client import RedisClient
client = TestClient(app)


def test_failed_delivery_and_check_redis_status():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()
    client.post("/stop_delivery")
    client.post("/start_delivery?port=5555")
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    time.sleep(20)
    assert redis_client.get("failed_m_id_5555") is not None
    client.post("/stop_delivery")
    redis_client.flushall()

