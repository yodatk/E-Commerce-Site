import enum
from abc import abstractmethod
from datetime import date, datetime
from socket import SocketIO

from src.domain.system.DAL import DAL
from src.domain.system.db_config import db
from src.external.publisher import Publisher
from src.protocol_classes.classes_utils import TypedList, TypedDict


class Emitter:
    @abstractmethod
    def emit(self, user_name: str, msg_type: str, msg) -> None:
        pass

    @abstractmethod
    def emit_group(self, msg_type: str, msg) -> None:
        pass


class SocketEmitter(Emitter):
    def __init__(self, socket: SocketIO):
        self._socket = socket

    def emit(self, user_name: str, msg_type: str, msg) -> None:
        self._socket.emit(msg_type, {'data': msg}, namespace=f"/{user_name}")

    def emit_group(self, msg_type: str, msg) -> None:
        self._socket.emit(msg_type, {'data': msg}, namespace=f"/{msg_type}")


class TestEmitter(Emitter):
    def __init__(self):
        self.notifications = TypedDict(str, TypedList)

    def emit(self, user_name: str, msg_type: str, msg) -> None:
        if user_name in self.notifications.keys():
            self.notifications[user_name].append(msg)
        else:
            self.notifications[user_name] = TypedList(str)


class Category(enum.Enum):
    system_manager = 1
    store_owner = 2
    store_manager = 3
    logged_in = 4
    guest = 5

    def to_string(self):
        if self == Category.system_manager:
            return "System Manager"
        elif self == Category.store_owner:
            return "Owner"
        elif self == Category.store_manager:
            return "Manager"
        elif self == Category.logged_in:
            return "Logged in"
        else:
            return "Guest"



class DailyStat(db.Model):
    __tablename__ = 'DailyStat'
    _date = db.Column(db.Date, default=date.today(), primary_key=True)
    _admin_counter = db.Column(db.Integer, default=0)
    _owner_counter = db.Column(db.Integer, default=0)
    _manager_counter = db.Column(db.Integer, default=0)
    _logged_in_counter = db.Column(db.Integer, default=0)
    _guest_counter = db.Column(db.Integer, default=0)

    def __init__(self, date, admin_counter, owner_counter, manager_counter, logged_in_counter, guest_counter):
        self._date = date
        self._admin_counter = admin_counter
        self._owner_counter = owner_counter
        self._manager_counter = manager_counter
        self._logged_in_counter = logged_in_counter
        self._guest_counter = guest_counter


    # deep copy that adds date
    def to_dictionary(self) -> dict:
        return {
            'date': self._date,
            Category.system_manager.to_string(): self._admin_counter,
            Category.store_owner.to_string(): self._owner_counter,
            Category.store_manager.to_string(): self._manager_counter,
            Category.logged_in.to_string(): self._logged_in_counter,
            Category.guest.to_string(): self._guest_counter
        }


class StatManager:
    __instance = None
    _dal: DAL = DAL.get_instance()

    def __init__(self):
        self.should_add = False


    @staticmethod
    def get_instance():
        """ Static access method. """
        if StatManager.__instance is None:
            StatManager.__instance = StatManager()
        return StatManager.__instance

    def resume_after_init(self):
        if not self.should_add:
            self.should_add = True
            self.daily_stat = DailyStat(date.today(), 0, 0, 0, 0, 0)
            self._dal.add(self.daily_stat, add_only=True)
            self.stat_dict = self._dal.get_all_stats()
            self.categ_name_to_field_dict = {
                Category.system_manager.to_string(): "_admin_counter",
                Category.store_owner.to_string(): "_owner_counter",
                Category.store_manager.to_string(): "_manager_counter",
                Category.logged_in.to_string(): "_logged_in_counter",
                Category.guest.to_string(): "_guest_counter",
            }

    def transition(self, new: str, old: str = None):
        if not self.should_add:
            return
        if old != new:
            self._dal.add(self.daily_stat, add_only=True)
            if date.today() != self.daily_stat._date:
                self.stat_dict[self.daily_stat._date] = self.daily_stat
                self._dal.add(self.daily_stat, add_only=True)
                self.daily_stat = DailyStat(date.today(), 0, 0, 0, 0, 0)
            elif old:
                setattr(self.daily_stat, self.categ_name_to_field_dict[old],
                        getattr(self.daily_stat, self.categ_name_to_field_dict[old]) - 1)
            setattr(self.daily_stat, self.categ_name_to_field_dict[new],
                    getattr(self.daily_stat, self.categ_name_to_field_dict[new]) + 1)
            self._dal.add(self.daily_stat, add_only=True)
            data_dict = self.daily_stat.to_dictionary()
            Publisher.get_instance().publish("stats", self.convert_entry_to_jsonable(data_dict))

    def get_stats_in_range(self, start: date = None, end: date = None):
        """

        :param start: start date
        :param end: end date
        :return: dictionary of data points for client
        """
        start = None if start >= date.today() else start
        end = None if end >= date.today() else end
        dict_to_ret = {}
        if start is None:
            dict_to_ret[self.daily_stat._date] = self.daily_stat.to_dictionary()
        else:
            if end is None:
                dict_to_ret = {}
                for key in self.stat_dict.keys():
                    self._dal.add(self.stat_dict[key], add_only=True)
                    if start <= key:
                        dict_to_ret[key] = self.stat_dict[key].to_dictionary()
                dict_to_ret[self.daily_stat._date] = self.daily_stat.to_dictionary()
            else:
                dict_to_ret = {}
                for key in self.stat_dict.keys():
                    if start <= key <= end:
                        dict_to_ret[key] = self.stat_dict[key].to_dictionary()
        return dict_to_ret

    def convert_entry_to_jsonable(self, entry_to_convert: dict):
        import copy
        new_dict = copy.deepcopy(entry_to_convert)
        new_dict['date'] = new_dict['date'].strftime('%d/%m/%Y')
        return new_dict

    def convert_dict_to_jsonable(self, dict_to_convert: dict):
        new_dict = {}
        for key, value in dict_to_convert.items():
            new_key = key.strftime('%d/%m/%Y')
            self.convert_entry_to_jsonable(dict_to_convert[key])
            new_dict[new_key] = self.convert_entry_to_jsonable(dict_to_convert[key])
        return new_dict



class PendingMessage(db.Model):
    __tablename__ = 'PendingMessages'
    _username = db.Column(db.VARCHAR(50), primary_key=True)
    _message = db.Column(db.VARCHAR(300), primary_key=True)
    _time = db.Column(db.DateTime, primary_key=True)
    _msg_type = db.Column(db.VARCHAR(50))

    def __init__(self, username: str, msg_type: str, message: str):
        self._username = username
        self._message = message
        self._msg_type = msg_type
        self._time = datetime.now()


class NotificationHandler:
    """
        Interface of Observer.
    """

    def __init__(self, emitter: Emitter):
        self._observers = {}
        self._emitter = emitter

    # creates observer if
    def connect(self, user_name: str) -> None:
        if user_name in self._observers.keys():
            print("found in observer list")
            self._observers[user_name]["logged_in"] = True
            pending = self._observers[user_name]["pending_messages"]
            if len(pending) > 0:
                for p in pending:
                    self._emitter.emit(user_name, *p)
                pending.clear()
                from src.domain.system.DAL import DAL
                DAL.get_instance().clear_pending_messages_for_user(user_name)

    def add_observer(self, user_name: str) -> None:
        if user_name not in self._observers.keys():
            self._observers[user_name] = {"logged_in": False, 'stats': False, "pending_messages": TypedList(tuple)}

    def disconnect(self, user_name: str) -> None:
        if user_name in self._observers.keys():
            self._observers[user_name]["logged_in"] = False

    def send_to_client(self, msg_type: str, msg: str, user_name: str = None) -> None:
        if user_name is None:
            self._emitter.emit_group(msg_type, msg)
            # print(f"in observer sent {msg} to group: {msg_type}")
        else:
            if user_name in self._observers.keys():
                if self._observers[user_name]["logged_in"]:
                    self._emitter.emit(user_name, msg_type, msg)
                    # print(f"in observer sent {msg} to user name: {user_name}")
                else:
                    # print(f"added to pending , message: {msg}")
                    pending_message: PendingMessage = PendingMessage(user_name, msg_type, msg)
                    from src.domain.system.DAL import DAL
                    DAL.get_instance().add(pending_message, add_only=True)
                    self._observers[user_name]["pending_messages"].append((msg_type, msg))

    def init_notification_handler(self):
        from src.domain.system.DAL import DAL
        d: DAL = DAL.get_instance()
        all_registered_users = d.get_all_registered_users()
        if len(all_registered_users) > 0:
            for user in all_registered_users:
                from src.domain.system.users_classes import LoggedInUser
                user: LoggedInUser = user
                self.add_observer(user.user_name)
        all_messages = d.get_all_pending_message()
        if len(all_messages) != 0:
            for m in all_messages:
                m: PendingMessage = m
                d.add(m, add_only=True)
                if m._username in self._observers:
                    list1 = self._observers[m._username]
                    list1["pending_messages"].append((m._msg_type, m._message))
                else:
                    list1 = [(m._msg_type, m._message)]
                    self._observers[m._username]["pending_messages"] = list1
