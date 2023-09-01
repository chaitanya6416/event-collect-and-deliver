import config
import redis
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from logger import logger


def log_after(retry_state):
    logger.warning(
        f"[REDIS CONNECTING...] [Attempt Failed] attempt:{retry_state.attempt_number}")


def log_before(retry_state):
    logger.info(
        f"[REDIS CONNECTING...] [Attempting Now] attempt:{retry_state.attempt_number}")


class RedisClient():
    def __init__(self):
        self.redis_host = config.REDIS_HOST
        self.redis_port = config.REDIS_PORT
        self.redis_db = config.REDIS_DB
        self.redis_client = None

    @retry(
        reraise=True,
        retry=retry_if_exception_type(),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),
        before=log_before,
        after=log_after
    )
    def get_client_instance(self):
        self.redis_client = redis.StrictRedis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            decode_responses=True
        )
        ping_response = self.redis_client.ping()
        if ping_response:
            print("Connected to Redis server successfully")
            return self.redis_client
        else:
            print("Retrying... redis connection")
