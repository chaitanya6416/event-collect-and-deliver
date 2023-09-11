''' we are testing /start_delivery endpoint '''

import os
import time
from fastapi.testclient import TestClient
from unittest.mock import patch
import json

from requests.models import Response
from main import app
from redis_client import RedisClient
client = TestClient(app)


@patch('src.simulate_service.deliver_and_get_response')
def test_successful_delivery_and_check_redis_status(mock_response):
    response = Response() 
    response.status_code = 200
    response._content = json.dumps({
        'status': 200,
        'message': 'all okay',
        'error_details': 'no error'
    }).encode('utf-8')

    mock_response = response

    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()

    TEMP_ENV_VARS = {
        'RETRY_MULTIPLIER': '1',
        'RETRY_MIN': '1',
        'RETRY_MAX': '1',
        'RETRY_ATTEMPTS': '1'
    }

    os.environ.update(TEMP_ENV_VARS)
    # assert os.getenv('WAIT_BETWEEN_REQUESTS') == '1'
    # assert os.getenv('RETRY_ATTEMPTS') == '1'

    client.post("/stop_delivery")
    client.post("/start_delivery?port=6666")
    time.sleep(5)
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    time.sleep(5)
    l = redis_client.keys("*")
    print(l)
    assert redis_client.get("failed_m_id_6666") is None
    client.post("/stop_delivery")
    redis_client.flushall()
