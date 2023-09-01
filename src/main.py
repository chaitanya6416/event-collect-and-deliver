import config
import signal
from fastapi import FastAPI
from uvicorn import run
from routes import setup_routes
from contextlib import asynccontextmanager
from redis_client import RedisClient
from delivery_thread import DeliveryThread
from logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    logger.info("[IN SYSTEM STARTUP] [REDIS SERVER CHECK] [SPAWNING EXISITING THREADS]")

    # Redis server up check
    try:
        redis_client = RedisClient().get_client_instance()
        config.redis_client = redis_client
    except Exception as ex:
        logger.error(f"Couldnt establish REDIS Connection. Exception:{ex}")
        raise ex
    
    # Load already existing threads, by checking from redis
    fetch_already_existing_threads = redis_client.keys(
        "last_delivered_m_id_to_*")
    for each_thread in fetch_already_existing_threads:
        port_number = each_thread.split("_")[-1]
        logger.info(
            f"[IN STARTUP] Found history in Redis [Spawing thread to Destination] {port_number=}")
        thread = DeliveryThread(port=each_thread.split("_")[-1])
        thread.start()
        logger.info(f"[IN STARTUP] [Thread to] {port_number=} [Active Now]")
        config.delivery_threads.append(thread)
    logger.info(f"[STARTUP DONE]")
    yield
    # shutdown
    # Gracefully terminate all threads
    logger.info(f"[IN SHUTDOWN] Terminating all Threads")
    for thread in config.delivery_threads:
        thread.stop()
        thread.join()
    config.delivery_threads.clear()
    logger.info(f"[IN SHUTDOWN] Done")


app = FastAPI(lifespan=lifespan)
setup_routes(app)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, reload=True)
