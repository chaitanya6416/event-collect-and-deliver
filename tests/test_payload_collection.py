''' we are here indeed testing the collect_api/ endpoint '''

from fastapi.testclient import TestClient
from main import app
from redis_client import RedisClient
import config
client = TestClient(app)


def test_postive_collect_api():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()
    payload = {"user_id": "123456", "payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Payload collected and append to stream"}

    # get redis stream info
    stream_info = redis_client.xinfo_stream(config.get_stream_name())

    # get all details from info
    last_entry_timestamp = stream_info["last-entry"][0]
    number_of_entries_in_stream = stream_info["length"]
    last_entry_payload = stream_info["last-entry"][1]['payload']

    # assert expected outputs
    assert number_of_entries_in_stream == 1
    assert last_entry_timestamp != '0'
    assert '{"user_id": "123456", "payload": "This is a test payload"}' in last_entry_payload

    redis_client.flushall()


def test_negative_collect_api():
    redis_client = RedisClient().get_client_instance()
    redis_client.flushall()
    payload = {"payload": "This is a test payload"}
    response = client.post("/collect_api", json=payload)
    assert response.status_code == 400
    redis_client.flushall()
