REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

RETRY_ATTEMPTS = 3
WAIT_BETWEEN_REQUESTS = 1

delivery_threads = []

redis_client = None

def get_stream_name():
    return "delivery_requests_stream"
