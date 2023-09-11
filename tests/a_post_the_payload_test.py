from fastapi.testclient import TestClient
import pytest 
import requests
from requests.models import Response
import json 
import delivery_thread
import config

class RedisMock:
    def __init__(self):
        pass

    def xread(self, info_dict, count):
        pass

    def get(self, key):
        pass

    def set(self, thread_status_name, new_id):
        pass

    def append(self, key, value_to_append):
        pass


class globalthreadingevent:
    def __init_(self):
        self.val = False
    def is_set(self):
        print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
        print(f"{self.is_set=}")
        return self.val
    def set(self):
        self.val = True



def test_successful_post_the_payload(monkeypatch):

    external_service_calls = 0
    def get_a_mock_redis_instance():
        return RedisMock()
    
    def get_a_global_threading_event():
        return globalthreadingevent()

    def get_200_always(not_used_port, not_used_payload):
        nonlocal external_service_calls
        external_service_calls += 1
        response = Response()
        response.status_code = 200
        response._content = json.dumps({
            'status': 200,
            'message': 'OK',
            'data': 'looks okay'
        }).encode('utf-8')
        return response

    monkeypatch.setattr(delivery_thread, 'get_redis_instance', get_a_mock_redis_instance)
    monkeypatch.setattr(delivery_thread, 'get_global_threading_event', get_a_global_threading_event)
    monkeypatch.setattr(delivery_thread, 'deliver_and_get_response', get_200_always)
    thread =  delivery_thread.DeliveryThread(1234)

    thread.post_the_payload(payload = {"user_id": "123456", "payload": "This is a test payload"})


    assert external_service_calls == 1




# def test_fail_post_the_payload(monkeypatch):

#     external_service_calls = 0
#     def get_a_mock_redis_instance():
#         return RedisMock()
    
#     def get_a_global_threading_event():
#         return globalthreadingevent()

#     def get_400_always(not_used_port, not_used_payload):
#         nonlocal external_service_calls
#         external_service_calls += 1
#         response = Response()
#         response.status_code = 400
#         response._content = json.dumps({
#             'status': 400,
#             'message': 'not OK',
#             'data': 'not okay'
#         }).encode('utf-8')
#         return response

#     monkeypatch.setattr(delivery_thread, 'get_redis_instance', get_a_mock_redis_instance)
#     monkeypatch.setattr(delivery_thread, 'get_global_threading_event', get_a_global_threading_event)
#     monkeypatch.setattr(delivery_thread, 'deliver_and_get_response', get_400_always)
#     thread =  delivery_thread.DeliveryThread(1234)

#     try:
#         thread.post_the_payload(payload = {"user_id": "123456", "payload": "This is a test payload"})
#     except Exception as ex:
#         pass

#     assert external_service_calls == config.RETRY_ATTEMPTS



# def test_assert_exceptions_when_post_the_payload(monkeypatch):

#     external_service_calls = 0
#     def get_a_mock_redis_instance():
#         return RedisMock()
    
#     def get_a_global_threading_event():
#         return globalthreadingevent()

#     def get_400_always(not_used_port, not_used_payload):
#         nonlocal external_service_calls
#         external_service_calls += 1
#         response = Response()
#         response.status_code = 400
#         response._content = json.dumps({
#             'status': 400,
#             'message': 'not OK',
#             'data': 'not okay'
#         }).encode('utf-8')
#         return response

#     monkeypatch.setattr(delivery_thread, 'get_redis_instance', get_a_mock_redis_instance)
#     monkeypatch.setattr(delivery_thread, 'get_global_threading_event', get_a_global_threading_event)
#     monkeypatch.setattr(delivery_thread, 'deliver_and_get_response', get_400_always)
#     thread =  delivery_thread.DeliveryThread(1234)

#     with pytest.raises(requests.RequestException):
#         thread.post_the_payload(payload = {"user_id": "123456", "payload": "This is a test payload"})
