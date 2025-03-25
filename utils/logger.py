import logging


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:

    logger_ = logging.getLogger(name)
    logger_.setLevel(level)

    console = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    console.setFormatter(formatter)
    logger_.addHandler(console)

    return logger_


logger = get_logger(__name__)
