import json
import logging
import logging.config
import os
from datetime import datetime

import yaml


def default(o):
    if isinstance(o, datetime):
        return o.isoformat()


class RemoveLevelFilter(object):
    def __init__(self, levelToSkip):
        self.level = levelToSkip

    def filter(self, record):
        return self.getLogLevelName(record.levelno) != self.level

    def getLogLevelName(self, levelno):
        switcher = {
            10: "DEBUG",
            20: "INFO",
            30: "WARNING",
            40: "ERROR",
            50: "CRITICAL"
        }
        return switcher.get(levelno, "INVALID")


class LogRec:
    _msg: str
    _data: any = None

    def __init__(self, msg: str = None, data=None):
        self._msg = msg
        self._data = data

    def __repr__(self):
        res = {}
        if self._msg:
            res['message'] = self._msg
        if self._data:
            res['data'] = self._data
        return json.dumps(
            res,
            sort_keys=True,
            default=default
        )


class Log:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if Log.__instance is None:
            Log()
        return Log.__instance

    def setup_logging(self, logger_filename='logging.yaml'):
        base = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(base, logger_filename)
        if os.path.exists(path):
            with open(path, 'rt') as f:
                config = yaml.safe_load(f.read())
                logging.config.dictConfig(config)
        else:
            raise Exception(f"Path: {path} doesn't exists")

    def __init__(self):
        """ Virtually private constructor. """
        if Log.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Log.__instance = self
        self.setup_logging()

    def disable_logger(self):
        logging.disable(logging.CRITICAL)

    def enable_logger(self):
        logging.disable(logging.NOTSET)

    def get_logger(self, module=None):
        self.enable_logger()
        logger_name_to_return = 'main_app_logger'
        if module is not None:
            try:
                # Attempt module detection
                mod_name = module.split('.')[-1]
                if mod_name in list(logging.root.manager.loggerDict.keys()):
                    logger_name_to_return = mod_name
            except:
                pass
        return logging.getLogger(logger_name_to_return)
