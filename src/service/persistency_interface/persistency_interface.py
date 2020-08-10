from src.domain.system.system_facade import SystemFacade
from src.logger.log import Log


class PersistencyInterface:

    def __init__(self):
        self.logger = Log.get_instance().get_logger()
        self.sys = SystemFacade.get_instance()

    def create_all(self, init_all):
        self.sys.create_all(init_all)

    def insert_some_fun(self):
        self.sys.insert_some_fun()

    def commit_session(self):
        self.sys.commit_session()

    def send_db_status_subject(self, dalSubject):
        self.sys.send_db_status_subject(dalSubject)