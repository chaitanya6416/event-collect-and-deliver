''' we are testing /start_delivery endpoint '''

import os
import threading
import time
from fastapi.testclient import TestClient

from src.main import app
from src.redis_client import RedisClient
client = TestClient(app)


def test_failed_delivery_and_check_redis_status():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()

    TEMP_ENV_VARS = {
        'RETRY_MULTIPLIER': '1',
        'RETRY_MIN': '1',
        'RETRY_MAX': '1',
        'RETRY_ATTEMPTS': '1'
    }

    os.environ.update(TEMP_ENV_VARS)

    client.post("/stop_delivery")
    client.post("/start_delivery?port=5555")
    time.sleep(10)
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    time.sleep(60)
    l = redis_client.keys("*")
    print(l)
    assert redis_client.get("failed_m_id_5555") is not None
    client.post("/stop_delivery")
    redis_client.flushall()
    # assert True
