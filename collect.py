# package imports
from fastapi import FastAPI
import json
import redis
import uvicorn

# file imports
import config
from user_data_model import UserData, DestinationData


app = FastAPI()
redis_client = None


def _init_redis_client():
    return redis.StrictRedis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db
    )


@app.post("/store_data/")
async def store_data(user_data: UserData):
    try:
        data_to_deliver = user_data.dict()
        for destination in config.get_destination_list():
            redis_client.rpush(destination, json.dumps(data_to_deliver))
            print(f"[Request Queued] to {destination=}")
        return {"message": "User Payloads are queued to destinations"}
    except Exception as ex:
        print(ex)


@app.post("/register_destination/")
async def register_destination(destination_data: DestinationData):
    try:
        destination = destination_data.dict()["destination"]
        if destination.startswith("www.") and destination.endswith(".com"):
            config.destination_list.append(destination)
            return {"message": f"Destination {destination} appended to list"}
        else:
            return {"message": f"Destional given is of not proper format"}
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    redis_client = _init_redis_client()
    uvicorn.run(app, host="0.0.0.0", port=8000)
