import pytest
from fastapi.testclient import TestClient
from main import app
import routes

client = TestClient(app)
number_of_threads = 0


class RedisMock:
    def __init__(self):
        self.streams = {}

    def get(self, port_numer_status):
        pass

    def set(self, thread_status_in_redis, last_entry_timestamp):
        pass

    def xadd(self, stream_name, payload):
        pass

    def xinfo_stream(self, stream_name):
        return {'last-entry': ['1212121112-0']}


class DeliveryThreadMock():
    def __init__(self, port):
        global number_of_threads
        number_of_threads += 1
        self.port = port
        self.thread_status_in_redis = f"last_delivered_m_id_to_{port}"

    def start(self):
        pass

    def join(self):
        pass

    def stop(self):
        pass


# @pytest.fixture(scope='function')
def test_start_delivery(monkeypatch):

    def get_a_redis_mock_instance():
        return RedisMock()

    def spawn_a_new_thread(port):
        return DeliveryThreadMock(port)

    # monkey patch before calling
    monkeypatch.setattr(routes, 'get_redis_instance',
                        get_a_redis_mock_instance)
    monkeypatch.setattr(routes, 'DeliveryThread', spawn_a_new_thread)

    client.post("/start_delivery?port=6666")
    # time.sleep(1)
    client.post("/stop_delivery")
    # time.sleep(2)
    assert number_of_threads == 1


# @pytest.fixture(scope='function')
def test_start_delivery_duplicate(monkeypatch):

    
    class CustomRedisMock(RedisMock):
        def get(self, port_numer_status):
            return "something"
    
    def get_a_redis_mock_instance():
        return CustomRedisMock()
    
    def spawn_a_new_thread(port):
        return DeliveryThreadMock(port)
        
    monkeypatch.setattr(routes, 'get_redis_instance', get_a_redis_mock_instance)
    monkeypatch.setattr(routes, 'DeliveryThread', spawn_a_new_thread)
    client.post("/start_delivery?port=1234")
    threads_at_begin = number_of_threads

    client.post("/start_delivery?port=1234")
    client.post("/start_delivery?port=1234")
    
    client.post("/stop_delivery")

    assert number_of_threads - threads_at_begin  == 0 


    
