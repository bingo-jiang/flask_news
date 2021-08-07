from redis import Redis
from setting import DevelopConfig


def connect():
    conn = Redis(host=DevelopConfig.REDIS_HOST, port=DevelopConfig.REDIS_PORT,
                 password=DevelopConfig.REDIS_PASSWORD)
    return conn


def redis_handle(key, value):
    connect = Redis(host=DevelopConfig.REDIS_HOST, port=DevelopConfig.REDIS_PORT,
                    password=DevelopConfig.REDIS_PASSWORD)
    connect.set(key, value)
    result = connect.get(key)
    return result
