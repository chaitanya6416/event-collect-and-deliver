'''
this file contains the delivery thread start up and running functionalities
'''

import json
import threading
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, wait_exponential, retry_if_exception_type, sleep_using_event

import config
from logger import logger, log_with_thread_id
from redis_client import get_redis_instance
from simulate_service import deliver_and_get_response
from global_threading_event import get_global_threading_event


threads_gracekill_event = get_global_threading_event()


class CustomEndError(BaseException):
    def __init__(self, message="-_- Ending Threads Gracefully"):
        super().__init__(message)


def log_after(retry_state):
    ''' log after each @retry '''
    log_with_thread_id(
        "[THREAD] [Attempt Failed] attempt: %s", retry_state.attempt_number)


def log_before(retry_state):
    ''' log before each @retry '''
    log_with_thread_id(
        "[THREAD] [Attempting Now] [FIRST CHECKING threads_gracekill_event: %s ]attempt: %s", threads_gracekill_event.is_set(), retry_state.attempt_number)


class DeliveryThread(threading.Thread):
    ''' every delivery thread spawned uses this class items & methods.'''

    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True
        self.thread_status_in_redis = f"last_delivered_m_id_to_{self.port}"
        self.thread_failures_in_redis = f"failed_m_id_{self.port}"
        self._redis_client = get_redis_instance()

    @retry(
        reraise=True,
        retry=retry_if_exception_type(requests.RequestException),
        stop=stop_after_attempt(config.RETRY_ATTEMPTS),
        # wait=wait_fixed(config.WAIT_BETWEEN_REQUESTS),
        wait=wait_exponential(multiplier=config.RETRY_MULTIPLIER,
                              min=config.RETRY_MIN, max=config.RETRY_MAX),
        before=log_before,
        after=log_after,
        sleep=sleep_using_event(threads_gracekill_event)
    )
    def post_the_payload(self, payload):
        ''' delivery action needs retry with specific logic as to retry count, 
        wait time between retries.
        Hence, moved this particular action to a new function '''
        # un-comment the below line to make a true post request to a http port
        # endpoint in the localhost.
        # response = requests.post(
        #     f"http://localhost:{self.port}/", json=payload, timeout=5)

        if threads_gracekill_event.is_set():
            raise CustomEndError()

        response = deliver_and_get_response(self.port, payload)
        response.raise_for_status()

        log_with_thread_id("Successfully delivered at port: %s", self.port)

    def run(self):
        ''' threads active will keep running & 
        check the redis stream & then call post_the_payload '''
        while self.running:
            # Read from the Redis Stream using XREAD
            response = self._redis_client.xread(
                {config.get_stream_name(): self._redis_client.get(
                    self.thread_status_in_redis)},
                count=1
            )

            if not response:
                continue  # No new requests, wait

            request_payload_ingestion_id = response[0][1][0][0]

            request_payload_json = response[0][1][0][1]['payload']

            if request_payload_json:
                payload = json.loads(request_payload_json)

                log_with_thread_id(
                    "Delivering payload: %s to port: %s", payload, self.port)

                try:
                    self.post_the_payload(payload)
                    # succesful, hence update redis
                    self._redis_client.set(
                        self.thread_status_in_redis, request_payload_ingestion_id)
                except requests.RequestException as ex:
                    log_with_thread_id(
                        "[FAILED] Delivery. No other exceptions raised other than `requests.RequestException` (if any)")
                    # store the request id as failed
                    self._redis_client.append(
                        self.thread_failures_in_redis, f", {request_payload_ingestion_id}")
                    # tried max times, still failed, so move on to the next payload
                    self._redis_client.set(
                        self.thread_status_in_redis, request_payload_ingestion_id)
                except CustomEndError as ce:
                    log_with_thread_id(f"[Exiting] Delivery, msg= {ce}")

    def stop(self):
        ''' should be called to stop thread execution '''
        self.running = False
