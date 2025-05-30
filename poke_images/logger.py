import logging

def get_logger(module_name: str):
    logger = logging.getLogger(module_name)
    handler = logging.FileHandler(f'logs/{module_name}.log')
    formatter = logging.Formatter('%(asctime)s {%(module)s} {%(endpoint)s} {%(funcName)s} %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger
