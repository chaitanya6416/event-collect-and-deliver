''' we are testing whether backup tasks are creating rdb and aof backups '''

import os
import time
from fastapi.testclient import TestClient

from main import app
from redis_client import RedisClient


def test_rdb_aof_backup_tasks():

    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()

    with TestClient(app) as client:
        payload = {"user_id": "123456", "payload": "This is a test payload"}
        client.post("/collect_api", json=payload)
        client.post("/start_delivery?port=5555")

        time.sleep(20)
        assert len(os.listdir(os.path.join(os.getcwd(), "rdb_backups"))) >= 1
        assert len(os.listdir(os.path.join(os.getcwd(), "aof_backups"))) >= 1

    redis_client.flushall()
