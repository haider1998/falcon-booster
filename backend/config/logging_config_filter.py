# backend/config/logging_config.py
import logging
import threading


class CorrelationIdFilter(logging.Filter):
    def __init__(self, name=""):
        super().__init__(name)
        self.local = threading.local()

    def get_request_id(self):
        return self.local.request_id

    def get_session_id(self):
        return self.local.session_id

    def get_correlation_ids(self):
        return self.local.request_id, self.local.session_id

    def set_correlation_ids(self, request_id, session_id):
        self.local.request_id = request_id
        self.local.session_id = session_id

    def filter(self, record):
        record.request_id = getattr(self.local, 'request_id', 'N/A')
        record.session_id = getattr(self.local, 'session_id', 'N/A')
        return True
