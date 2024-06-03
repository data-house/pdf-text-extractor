import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler

from root import ROOT_DIR


def init_logger() -> None:
    """
    Initialize logger for the application
    :return: None
    """
    sys.stdout.reconfigure(encoding='utf-8')
    try:
        os.mkdir(os.path.join(ROOT_DIR, "logs"))
    except FileExistsError:
        pass
    try:
        os.mkdir(os.path.join(ROOT_DIR, "logs", "queries"))
    except FileExistsError:
        pass

    logger = logging.getLogger("parsing_service")
    logger.setLevel(logging.DEBUG)

    # create file and console handler for logs
    fh = TimedRotatingFileHandler(os.path.join(ROOT_DIR, "logs/application_log.log"), when="midnight", backupCount=30,
                                  encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt='%(asctime)s.%(msecs)03d %(module)s %(lineno)d %(levelname)s: %(message)s',
                                  datefmt='%H:%M:%S')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)
