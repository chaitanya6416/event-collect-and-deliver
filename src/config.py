''' some dynamic or whole module wide used variables are here '''
import os


REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_DB = os.getenv('REDIS_DB', 0)

RETRY_ATTEMPTS = os.getenv('RETRY_ATTEMPTS', 10)
RETRY_MULTIPLIER = os.getenv('RETRY_MULTIPLIER', 1)
RETRY_MIN = os.getenv('RETRY_MIN', 4)
RETRY_MAX = os.getenv('RETRY_MAX', 10)

RDB_BACKUPS_INTERVAL = os.getenv('RDB_BACKUPS_INTERVAL', 1200)
AOF_BACKUPS_INTERVAL = os.getenv('AOF_BACKUPS_INTERVAL', 60)

delivery_threads = []


def get_stream_name():
    ''' all input payloads go into this redis stream '''
    return "delivery_requests_stream"
