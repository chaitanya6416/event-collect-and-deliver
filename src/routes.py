from fastapi import HTTPException
import json
from delivery_thread import DeliveryThread
from fastapi import FastAPI
from redis_client import redis_client
import config
import redis


def setup_routes(app: FastAPI):
    @app.post("/collect_api")
    async def collect_api(payload: dict):
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

        # Add payload to the Redis Stream
        redis_client.xadd(config.get_stream_name(),
                          {"payload": payload_json})

        return {"message": "Payload collected and append to stream"}

    @app.post("/start_delivery")
    async def start_delivery(port: int):
        thread = DeliveryThread(port=port)

        # Initialize the thread_status to last-entry timestamp
        try:
            stream_meta_info = redis_client.xinfo_stream(
                config.get_stream_name())
            last_entry_timestamp = stream_meta_info["last-entry"][0]
        except redis.exceptions.ResponseError as e:
            if "no such key" in str(e).lower():
                # Handle the case when the stream doesn't exist
                last_entry_timestamp = '0'
            else:
                # Handle other Redis response errors here
                raise e

        redis_client.set(thread.thread_status_in_redis, last_entry_timestamp)
        thread.start()
        config.delivery_threads.append(thread)
        return {"message": f"Delivery thread for port {port} started"}

    @app.post("/stop_delivery")
    async def stop_delivery():
        for thread in config.delivery_threads:
            thread.stop()
            thread.join()
        config.delivery_threads.clear()
        return {"message": "All delivery threads stopped"}
