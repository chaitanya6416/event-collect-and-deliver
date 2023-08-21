import config
import redis

redis_client = redis.StrictRedis(
    host=config.REDIS_HOST, 
    port=config.REDIS_PORT, 
    db=config.REDIS_DB, 
    decode_responses=True
)
