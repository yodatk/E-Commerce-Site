from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from src.domain.system.db_config import db



class TypedList(list):
    """List that checks the list have only item of a given type"""

    def __init__(self, type_items, initial_list: list = None):
        super().__init__()
        if initial_list is None:
            initial_list = []
        self._type_items = type_items
        if not (initial_list is None or (isinstance(initial_list, list) and all(
                isinstance(item, type_items) for item in initial_list))):
            raise TypeError("initial list is not matching the type")
        else:
            self.extend(initial_list)

    def append(self, item):
        """
        Add item if it's type is 'type_items'
        :param item: item to add
        :return: None.
        """
        if not isinstance(item, self._type_items):
            raise TypeError('item is not of type {}'.format(self._type_items))
        super(TypedList, self).append(item)  # append the item to itself (the list)

    @property
    def type_items(self):
        return self._type_items

    @type_items.setter
    def type_items(self, key):
        raise Exception("cannot change item type of TypedList")

    def check_types(self, wanted_type):
        return wanted_type == self._type_items

    def filtering_empty_str(self):
        if self._type_items == str:
            lst = [elem for elem in self if elem.strip() != '']
            return TypedList(str, lst)
        else:
            return self

    def copy(self):
        copied = [i for i in self]
        return TypedList(self._type_items, copied)


class TypedDict(dict):
    """
    Dictionary that contains keys from the same type, and values from the same type
    """

    def __init__(self, type_key, type_value, initial_dict: dict = None):
        super().__init__()
        if initial_dict is None:
            initial_dict = dict()
        self._type_key = type_key
        self._type_value = type_value
        if not (len(initial_dict) == 0 or (
                isinstance(initial_dict, dict) and all(isinstance(k, type_key) for k in initial_dict.keys()) and all(
            isinstance(v, type_value) for v in initial_dict.values()))):
            raise TypeError("initial dict is not matching the types")
        elif len(initial_dict) != 0:
            for k in initial_dict.keys():
                self.__setitem__(k, initial_dict.get(k))

    def __setitem__(self, key, value):
        if (type(key) == self._type_key) and isinstance(value, self._type_value):
            super(TypedDict, self).__setitem__(key, value)
        else:
            raise TypeError('item is not of type {} -> {}'.format(self._type_key, type(self._type_value)))

    @property
    def type_key(self):
        return self._type_key

    @type_key.setter
    def type_key(self, key):
        raise Exception("cannot change key type of TypedDict")

    @property
    def type_value(self):
        return self._type_value

    @type_value.setter
    def type_value(self, value):
        raise Exception("cannot change value type of typedDict")

    def check_types(self, wanted_keys, wanted_values):
        return wanted_keys == self._type_key and wanted_values == self._type_value

    def copy(self):
        copied = TypedDict(self._type_key, self._type_value)
        for key in self.keys():
            copied[key] = self.get(key)
        return copied


@dataclass(frozen=True)
class Result:
    """
    Class for explaining result of a process or request from the system
    """
    succeed: bool  # is operation successful
    requesting_id: int  # the id of the requesting user(if didnt have all along, will return a new one)
    msg: str  # detailed message if something went wrong \ success message
    data: any = field(default_factory=None)  # any data that was requested will appear in this field

    def to_dictionary(self):
        return {
            "succeed": self.succeed,
            "requesting_id": self.requesting_id,
            "msg": self.msg,
            "data": self.data
        }

    def __post_init__(self):
        if not isinstance(self.succeed, bool):
            raise TypeError("Not a of type bool: succeed")

        if not isinstance(self.requesting_id, int):
            raise TypeError("Not of type int: requesting_id")

        if not isinstance(self.msg, str):
            raise TypeError("Not of type str: msg")


class TypeChecker:
    @staticmethod
    def check_for_non_empty_strings(strings: list):
        return all(type(item) == str and item.strip() != "" for item in strings)

    @staticmethod
    def check_for_positive_number(numbers: list):
        return all((type(item) == int or type(item) == float) and item >= 0 for item in numbers)

    @staticmethod
    def check_for_positive_ints(numbers: list):
        return all(type(item) == int and item >= 0 for item in numbers)

    @staticmethod
    def check_for_list_of_bool(bools: list):
        return all(type(item) == bool for item in bools)
