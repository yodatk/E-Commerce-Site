from src.domain.system.data_handler import DataHandler
from src.logger.log import Log


class PersistencyHandler:
    def __init__(self, data_handler: DataHandler):
        self.logger = Log.get_instance().get_logger()
        self._data_handler = data_handler

    def create_all(self, init_app):
        self._data_handler.create_all(init_app)

    def insert_some_fun(self):
        self._data_handler.insert_some_fun()

    def commit_session(self):
        self._data_handler.commit_session()