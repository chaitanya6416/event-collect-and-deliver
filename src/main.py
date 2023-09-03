''' this is main.py, defined system lifespan events and setup all endpoints (routes) '''

from contextlib import asynccontextmanager
from fastapi import FastAPI
from uvicorn import run

import config
from delivery_thread import DeliveryThread
from logger import logger
from routes import setup_routes
from redis_client import RedisClient
from backups.backup_tasks import scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    This part of code runs a set of commands before the endpoints become available.
    '''
    # startup
    logger.info(
        "[IN SYSTEM STARTUP] [REDIS SERVER CHECK] [SPAWNING EXISITING THREADS]")

    # Redis server up check
    try:
        redis_client = RedisClient().get_client_instance()
        config.redis_client = redis_client
    except Exception as ex:
        logger.error("Couldnt establish REDIS Connection. Exception: %s", ex)
        raise ex

    # Load already existing threads, by checking from redis
    fetch_already_existing_threads = redis_client.keys(
        "last_delivered_m_id_to_*")
    for each_thread in fetch_already_existing_threads:
        port_number = each_thread.split("_")[-1]
        logger.info(
            '''[IN STARTUP] Found history in Redis [Spawing thread to Destination] port: %s''', port_number)
        thread = DeliveryThread(port=each_thread.split("_")[-1])
        thread.start()
        logger.info(
            "[IN STARTUP] [Thread to] port: %s [Active Now]", port_number)
        config.delivery_threads.append(thread)
    logger.info("[STARTUP DONE]")

    # #begin redis backups
    scheduler.start()
    yield
    # shutdown
    # Gracefully terminate all threads
    logger.info("[IN SHUTDOWN] Terminating all Threads")
    for thread in config.delivery_threads:
        thread.stop()
        thread.join()
    config.delivery_threads.clear()
    scheduler.shutdown()
    logger.info("[IN SHUTDOWN] Done")


app = FastAPI(lifespan=lifespan)
setup_routes(app)


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, reload=True)
