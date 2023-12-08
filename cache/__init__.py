from flask_caching import Cache, request
from app import app

config = {
    "CACHE_TYPE": "RedisCache",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": 6379,
    "REDIS_PASSWORD": "",
    "REDIS_DB": 0,
    "CACHE_REDIS_URL": "redis://localhost:6379/0"
}

cache = Cache(app, config=config)


@app.after_request
def after_request(response):
    if request.method != 'GET':
        cache.clear()
    return response
