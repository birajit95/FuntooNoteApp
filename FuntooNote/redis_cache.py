import redis
class Cache:
    obj = None
    @staticmethod
    def getCacheInstance():
        global obj
        if Cache.obj is None:
            Cache.obj = redis.Redis(host='localhost', port=6379)
        return Cache.obj
