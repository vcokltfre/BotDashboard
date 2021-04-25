from time import time


class Ratelimiter:
    def __init__(self, timeout: int):
        self.buckets = {}
        self.timeout = timeout

    def trigger(self, bucket):
        when = self.buckets.get(bucket, 0)

        if when < time():
            self.buckets[bucket] = time() + self.timeout
            return False

        return True
