import config
import threading
import requests
import json
from logger import logger
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from redis_client import redis_client


def log_after(retry_state):
    logger.info(
        f"[THREAD] [Attempt Failed] attempt:{retry_state.attempt_number}")


def log_before(retry_state):
    logger.info(
        f"[THREAD] [Attempting Now] attempt:{retry_state.attempt_number}")


class DeliveryThread(threading.Thread):
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
        response = requests.post(
            f"http://localhost:{self.port}/", json=payload)
        response.raise_for_status()
        logger.info(f"Successfully delivered at port {self.port}")

    def run(self):
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
                    f"Delivering payload: {payload} to {self.port}")

                try:
                    self.post_the_payload(payload)
                except requests.RequestException as e:
                    print(f'FAILED: {e}')
                    # store the request id as failed
                    redis_client.append(
                        self.thread_failures_in_redis, f", {request_payload_ingestion_id}")
                finally:
                    # successful or not, we have to move on to next payload to deliver
                    # hence updating
                    redis_client.set(self.thread_status_in_redis,
                                     request_payload_ingestion_id)

    def stop(self):
        self.running = False
