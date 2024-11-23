# file: backend/services/data_store.py
class DataStore:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataStore, cls).__new__(cls)
            cls._instance.data = {}
        return cls._instance

    def set_data(self, key, value):
        self.data[key] = value

    def get_data(self, key):
        return self.data.get(key)

    def get_all_keys(self):
        return list(self.data.keys())

    def clear(self):
        self.data = {}
