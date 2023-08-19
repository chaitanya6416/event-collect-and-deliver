# routes.py
from fastapi import HTTPException
import json
# from logger import logger
from deliver_thread import DeliveryThread
from fastapi import FastAPI
from redis_client import redis_client

delivery_threads = []

def setup_routes(app: FastAPI):
    @app.post("/collect_api")
    async def collect_api(payload: dict):
        user_id = payload.get("user_id")
        actual_payload = payload.get("payload")

        if user_id is None or actual_payload is None:
            raise HTTPException(status_code=400, detail="Both user_id and payload are required")

        sequence_number = redis_client.incr("sequence_number")
        payload_to_store = {
            "user_id": user_id,
            "payload": actual_payload,
            "sequence_number": sequence_number
        }

        # Serialize the payload dictionary to JSON
        payload_json = json.dumps(payload_to_store)

        # Store serialized payload in Redis for delivery
        redis_client.lpush("delivery_requests", payload_json)
        return {"message": "Payload collected and stored"}
