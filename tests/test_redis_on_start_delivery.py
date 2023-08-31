import threading
import time
from fastapi.testclient import TestClient

from src.main import app
from src.redis_client import redis_client
client = TestClient(app)


def test_start_delivery_and_check_threads():
    threads_at_begin = threading.active_count()

    # Make the request to start the delivery thread
    response = client.post("/start_delivery?port=5555")

    assert response.status_code == 200
    assert response.json() == {"message": "Delivery thread for port 5555 started"}

    # Wait for the thread to start
    time.sleep(1)

    # Get the number of threads running
    threads_at_end = threading.active_count()

    # Assert that one thread is created
    assert threads_at_end - threads_at_begin == 1
    client.post("/stop_delivery")


def test_start_delivery_and_check_redis():
    redis_client.flushall()
    client.post("/start_delivery?port=5555")
    time.sleep(1)
    assert redis_client.get("last_delivered_m_id_to_5555") == '0'
    client.post("/stop_delivery")
    redis_client.flushall()
