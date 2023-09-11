''' we are testing /start_delivery endpoint '''

import threading
import time
from fastapi.testclient import TestClient

from main import app
from redis_client import RedisClient
client = TestClient(app)


def test_start_delivery_and_check_threads():
    threads_at_begin = threading.active_count()

    # Make the request to start the delivery thread
    response = client.post("/start_delivery?port=1598")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Delivery thread for port 1598 started"}

    # Wait for the thread to start
    time.sleep(10)

    # Get the number of threads running
    threads_at_end = threading.active_count()

    # Assert that one thread is created
    assert threads_at_end - threads_at_begin >= 1
    client.post("/stop_delivery")


def test_start_delivery_and_check_redis():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()
    client.post("/stop_delivery")
    client.post("/start_delivery?port=5555")
    time.sleep(10)
    assert redis_client.get("last_delivered_m_id_to_5555") == '0'
    client.post("/stop_delivery")
    redis_client.flushall()


def test_duplicate_start_delivery_and_check_threads():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()
    client.post("/stop_delivery")
    threads_at_begin = threading.active_count()
    client.post("/start_delivery?port=5555")
    client.post("/start_delivery?port=5555")
    client.post("/start_delivery?port=5555")
    time.sleep(10)
    threads_at_end = threading.active_count()
    assert threads_at_end - threads_at_begin >= 1
    client.post("/stop_delivery")
    redis_client.flushall()
