import logging
from datetime import datetime

def get_logger(module_name: str):
    logger = logging.getLogger(module_name)
    handler = logging.FileHandler(f'logs/{module_name}.log')
    formatter = logging.Formatter('%(asctime)s {%(module)s} {%(funcName)s} %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger
