''' we are testing /start_delivery endpoint '''

import threading
import time
from fastapi.testclient import TestClient

from main import app
from redis_client import RedisClient


def test_spawn_already_registered_thread_on_restart():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()
    threads_before_app_starts = threading.active_count()
    redis_client.set("last_delivered_m_id_to_5555", '111111111-0')
    redis_client.set("last_delivered_m_id_to_6666", '111111111-0')
    with TestClient(app) as client:
        time.sleep(10)
        threads_after_app_starts = threading.active_count()
        client.post("/stop_delivery")
        time.sleep(2)
        # assert threads_after_app_starts - threads_before_app_starts >= 3
    # time.sleep(5)
    # client = TestClient(app)
    # time.sleep(10)
    # threads_after_app_starts = threading.active_count()
    # client.post("/stop_delivery")
    # time.sleep(2)
    assert threads_after_app_starts - threads_before_app_starts >= 3
    