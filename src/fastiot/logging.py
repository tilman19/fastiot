
from fastiot.env import env_basic
from fastiot.helpers.log_config import get_log_config


def logging(name: str = None):
    """
    This logging is a wrapper for logging from python,
    """
    import logging.config
    logging.config.dictConfig(get_log_config(env_basic.log_level_no))
    return logging.getLogger(name)

