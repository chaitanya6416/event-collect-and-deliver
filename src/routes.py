''' endpoints in the application and the respective actions are defined here '''

import json
from fastapi import FastAPI, HTTPException
import redis

import config
from delivery_thread import DeliveryThread
from redis_client import RedisClient
from logger import logger


def setup_routes(app: FastAPI):
    ''' instead of defining all routes in main, we have moved them here, 
    so setup_routes will be simply called in main'''

    @app.post("/collect_api")
    async def collect_api(payload: dict):
        ''' payload collection endpoint'''

        user_id = payload.get("user_id")
        actual_payload = payload.get("payload")

        if user_id is None or actual_payload is None:
            raise HTTPException(
                status_code=400, detail="Both user_id and payload are required")

        payload_to_store = {
            "user_id": user_id,
            "payload": actual_payload
        }
        payload_json = json.dumps(payload_to_store)

        redis_client = RedisClient().get_client_instance()
        # Add payload to the Redis Stream
        redis_client.xadd(config.get_stream_name(),
                          {"payload": payload_json})

        return {"message": "Payload collected and append to stream"}

    @app.post("/start_delivery")
    async def start_delivery(port: int):
        ''' adding a delivery to a destination port is handled here '''
        redis_client = RedisClient().get_client_instance()
        # first check if this destination thread is already running
        if redis_client.get(f"last_delivered_m_id_to_{port}") is not None:
            logger.warning(
                "[Thread] to destination port = %s is already active", port)
            return

        thread = DeliveryThread(port=port)

        # Initialize the thread_status to last-entry timestamp
        try:
            stream_meta_info = redis_client.xinfo_stream(
                config.get_stream_name())
            last_entry_timestamp = stream_meta_info["last-entry"][0]
        except redis.exceptions.ResponseError as ex:
            if "no such key" in str(ex).lower():
                # Handle the case when the stream doesn't exist
                last_entry_timestamp = '0'
            else:
                # Handle other Redis response errors here
                raise ex

        redis_client.set(thread.thread_status_in_redis, last_entry_timestamp)
        thread.start()
        config.delivery_threads.append(thread)
        return {"message": f"Delivery thread for port {port} started"}

    @app.post("/stop_delivery")
    async def stop_delivery():
        ''' stop after current delivery ends '''
        for thread in config.delivery_threads:
            thread.stop()

        for thread in config.delivery_threads:
            thread.join()
        config.delivery_threads.clear()
        return {"message": "All delivery threads stopped"}
