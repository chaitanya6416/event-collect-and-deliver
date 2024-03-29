''' we are testing /start_delivery endpoint '''

import os
import time
from fastapi.testclient import TestClient
from unittest.mock import patch
from requests.models import Response
import json

from main import app
from redis_client import RedisClient
client = TestClient(app)


@patch('src.simulate_service.deliver_and_get_response')
def test_failed_delivery_and_check_redis_status(mock_response):
    response = Response()
    response.status_code = 400
    response._content = json.dumps({
        'status': 400,
        'message': 'Bad Request',
        'error_details': 'Invalid payload'
    }).encode('utf-8')

    mock_response = response

    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()

    TEMP_ENV_VARS = {
        'RETRY_MULTIPLIER': '2',
        'RETRY_MIN': '1',
        'RETRY_MAX': '2',
        'RETRY_ATTEMPTS': '2'
    }

    os.environ.update(TEMP_ENV_VARS)

    client.post("/stop_delivery")
    client.post("/start_delivery?port=5555")
    time.sleep(1)
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    time.sleep(10)
    l = redis_client.keys("*")
    print(l)
    print(redis_client.get("failed_m_id_5555"))
    assert redis_client.get("failed_m_id_5555") != '0'
    client.post("/stop_delivery")
    redis_client.flushall()
