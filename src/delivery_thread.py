'''
this file contains the delivery thread start up and running functionalities
'''

import json
import threading
import requests
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


import config
from logger import logger
from redis_client import RedisClient

redis_client = RedisClient().get_client_instance()


def log_after(retry_state):
    ''' log after each @retry '''
    logger.info(
        "[THREAD] [Attempt Failed] attempt: %s", retry_state.attempt_number)


def log_before(retry_state):
    ''' log before each @retry '''
    logger.info(
        "[THREAD] [Attempting Now] attempt: %s", retry_state.attempt_number)


class DeliveryThread(threading.Thread):
    ''' every delivery thread spawned uses this class items & methods.'''
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.running = True
        self.thread_status_in_redis = f"last_delivered_m_id_to_{self.port}"
        self.thread_failures_in_redis = f"failed_m_id_{self.port}"

    @retry(
        reraise=True,
        retry=retry_if_exception_type(),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        before=log_before,
        after=log_after
    )
    def post_the_payload(self, payload):
        ''' delivery action needs retry with specific logic as to retry count, 
        wait time between retries.
        Hence, moved this particular action to a new function '''
        response = requests.post(
            f"http://localhost:{self.port}/", json=payload, timeout = 5)
        response.raise_for_status()
        logger.info("Successfully delivered at port: %s", self.port)

    def run(self):
        ''' threads active will keep running & 
        check the redis stream & then call post_the_payload '''
        while self.running:
            # Read from the Redis Stream using XREAD
            response = redis_client.xread(
                {config.get_stream_name(): redis_client.get(
                    self.thread_status_in_redis)},
                count=1
            )

            if not response:
                continue  # No new requests, wait

            request_payload_ingestion_id = response[0][1][0][0]

            request_payload_json = response[0][1][0][1]['payload']

            if request_payload_json:
                payload = json.loads(request_payload_json)

                logger.info(
                    "Delivering payload: %s to port: %s", payload, self.port)

                try:
                    self.post_the_payload(payload)
                except requests.RequestException as ex:
                    print("FAILED: %s", ex)
                    # store the request id as failed
                    redis_client.append(
                        self.thread_failures_in_redis, f", {request_payload_ingestion_id}")
                finally:
                    # successful or not, we have to move on to next payload to deliver
                    # hence updating
                    redis_client.set(self.thread_status_in_redis,
                                     request_payload_ingestion_id)

    def stop(self):
        ''' should be called to stop thread execution '''
        self.running = False
