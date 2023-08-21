import config
import threading
import requests
import json
from logger import logger
from tenacity import retry, stop_after_attempt, wait_fixed
from redis_client import redis_client


class DeliveryThread(threading.Thread):
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.delivered_key = f"port_{port}_delivered"
        self.running = True

    @retry(stop=stop_after_attempt(config.RETRY_ATTEMPTS), wait=wait_fixed(config.WAIT_BETWEEN_REQUESTS))
    def post_the_payload(self, payload):
        try:
            response = requests.post(
                f"http://localhost:{self.port}/", json=payload)
            response.raise_for_status()
            logger.info(f"Successfully delivered at port {self.port}")
        except requests.RequestException as e:
            logger.error(f"Delivery failed at port {self.port}: {e}")

    def run(self):
        while self.running:
            num_delivered = int(redis_client.get(self.delivered_key) or 0)
            num_requests = int(redis_client.get("sequence_number") or 0)

            if num_delivered >= num_requests:
                continue  # No new requests, wait

            logger.info(
                f"Processing {num_requests - num_delivered} new requests.")

            for i in range(num_requests - num_delivered - 1, -1, -1):
                request_payload_json = redis_client.lindex(
                    "delivery_requests", i)
                if request_payload_json:
                    request_payload = json.loads(request_payload_json)

                    payload = {
                        "user_id": request_payload["user_id"],
                        "payload": request_payload["payload"],
                        "sequence_number": request_payload["sequence_number"]
                    }

                    logger.info(
                        f"Delivering payload: {payload} to {self.port}")

                    try:
                        # Using the decorated method
                        self.post_the_payload(payload)
                    except requests.RequestException:
                        logger.warning("Delivery failed after 3 retries.")

                    # Update delivered count and store in Redis (backup)
                    redis_client.incr(self.delivered_key)

    def stop(self):
        self.running = False
