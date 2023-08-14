import logging


def setup_logger(log_file):
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] [%(module)s:%(lineno)d] %(message)s',
        filename=log_file,
        filemode='a'
    )


def get_logger(name):
    return logging.getLogger(name)
