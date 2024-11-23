# logging_config.py
import logging

from backend.config.logging_config_filter import CorrelationIdFilter


def configure_logging():
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s - RequestID: %(request_id)s - SessionID: %(session_id)s')
    filter = CorrelationIdFilter()
    logging.getLogger().addFilter(filter)
    return filter
