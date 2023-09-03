''' we are testing /start_delivery endpoint '''

import threading
import time
from fastapi.testclient import TestClient

from src.main import app
from src.redis_client import RedisClient


def test_spawn_already_exisiting_thread_on_restart():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()
    threads_before_app_starts = threading.active_count()
    redis_client.set("last_delivered_m_id_to_5555", '111111111-0')
    redis_client.set("last_delivered_m_id_to_6666", '111111111-0')
    with TestClient(app) as client:
        threads_after_app_starts = threading.active_count()
        assert threads_after_app_starts - threads_before_app_starts >= 3
    
    client.post("/stop_delivery")

