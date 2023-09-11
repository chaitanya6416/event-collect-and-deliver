''' this is main.py, defined system lifespan events and setup all endpoints (routes) '''

from contextlib import asynccontextmanager
from fastapi import FastAPI

import config
from delivery_thread import DeliveryThread
from logger import logger
from routes import setup_routes
from redis_client import get_redis_instance
from backups.backup_tasks import scheduler
from global_threading_event import get_global_threading_event


@asynccontextmanager
async def lifespan(app: FastAPI):
    '''
    This part of code runs a set of commands before the endpoints become available.
    '''
    # startup
    logger.info(
        "[IN SYSTEM STARTUP] [REDIS SERVER CHECK] [SPAWNING EXISITING THREADS]")

    # create a threading.event(), on which all the threads depend in case of
    # SIGKILL
    threads_gracekill_event = get_global_threading_event()

    # Redis server up check
    try:
        redis_client_instance = get_redis_instance()
        
    except Exception as ex:
        logger.error("Couldnt establish REDIS Connection. Exception: %s", ex)
        raise ex

    # Load already existing threads, by checking from redis
    fetch_already_existing_threads = redis_client_instance.keys(
        "last_delivered_m_id_to_*")
    for each_thread in fetch_already_existing_threads:
        port_number = each_thread.split("_")[-1]
        logger.info(
            '''[IN STARTUP] Found history in Redis [Spawing thread to Destination] port: %s''', port_number)
        thread = DeliveryThread(port=port_number)

        logger.info(
            "[IN STARTUP] [Thread to] port: %s [Activating Now...]", port_number)
        thread.start()
        config.delivery_threads.append(thread)
    logger.info("[STARTUP DONE]")

    # begin redis backups
    scheduler.start()
    yield
    # shutdown

    # set the below thread.event() to gracefully stop all threads
    # struck in @retry post_the_payload
    logger.info("[IN SHUTDOWN] Terminating all Threads")

    # turn running flag to false has to be done first
    for thread in config.delivery_threads:
        thread.stop()

    # set the thread.event()
    threads_gracekill_event.set()

    for thread in config.delivery_threads:
        thread.join()

    config.delivery_threads.clear()
    scheduler.shutdown()
    logger.info("[IN SHUTDOWN] Done")


app = FastAPI(lifespan=lifespan)
setup_routes(app)
