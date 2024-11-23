# python
class StepsCache:
    def __init__(self):
        self.cache = {}

    def get(self, key):
        return self.cache.get(key)

    def set(self, key, value):
        self.cache[key] = value

    def has(self, key):
        return key in self.cache

    def clear(self):
        self.cache = {}
