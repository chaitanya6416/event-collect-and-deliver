''' some dynamic or whole module wide used variables are here '''

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

RETRY_ATTEMPTS = 3
WAIT_BETWEEN_REQUESTS = 1

delivery_threads = []


def get_stream_name():
    ''' all input payloads go into this redis stream '''
    return "delivery_requests_stream"
