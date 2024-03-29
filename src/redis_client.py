'''
This file initiates the redis client & checks if the redis server is up.
If down, retries few times and then raises necessary exception.
'''

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import redis

import config


class RedisClient():
    '''Before running any redis command, we need to check if the server is up & running.'''

    def __init__(self):
        self.redis_host = config.REDIS_HOST
        self.redis_port = config.REDIS_PORT
        self.redis_db = config.REDIS_DB
        self.redis_client = None

    def __del__(self):
        self.redis_client.close()

    @retry(
        reraise=True,
        retry=retry_if_exception_type(),
        stop=stop_after_attempt(3),
        wait=wait_fixed(3),

    )
    def get_client_instance(self):
        '''return the redis client instance'''
        self.redis_client = redis.StrictRedis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            decode_responses=True
        )
        ping_response = self.redis_client.ping()
        if ping_response:
            return self.redis_client
        return None


def get_redis_instance():
    return RedisClient().get_client_instance()