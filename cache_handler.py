from redis import Redis

class CacheHandler():

    redis_conn = None

    def __init__(self, redis_url):

        if redis_url:
            self.redis_conn = Redis.from_url(redis_url)

    def get(self, key, default):

        if self.redis_conn == None:
            return default

        return self.redis_conn.get(key) or default

    def set(self, key, val, expire=None):

        if self.redis_conn == None:
            return

        if expire == None:
            self.redis_conn.set(key, val)
        else:
            self.redis_conn.setex(key, val, expire)
