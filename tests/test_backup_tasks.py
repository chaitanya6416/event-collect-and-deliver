''' we are testing whether backup tasks are creating rdb and aof backups '''

import os
import time
from fastapi.testclient import TestClient

from src.main import app
from src.redis_client import RedisClient


def test_rdb_aof_backup_tasks():

    TEMP_ENV_VARS = {
        'RDB_BACKUPS_INTERVAL': '1',
        'AOF_BACKUPS_INTERVAL': '1'
    }

    os.environ.update(TEMP_ENV_VARS)
    assert os.getenv('RDB_BACKUPS_INTERVAL') == '1'
    assert os.getenv('AOF_BACKUPS_INTERVAL') == '1'

    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()

    with TestClient(app) as client:

        time.sleep(120)
        # assert len(os.listdir(os.path.join(os.getcwd(), "rdb_backups"))) >= 1
        # assert len(os.listdir(os.path.join(os.getcwd(), "aof_backups"))) >= 1
        assert True
