from __future__ import annotations

from typing import TYPE_CHECKING

from src.communication.notification_handler import Category, StatManager
from src.domain.system.DAL import DAL
from src.domain.system.cart_purchase_classes import Purchase
from src.domain.system.store_classes import Store

if TYPE_CHECKING:
    from src.domain.system.permission_classes import Permission, Role
    from src.domain.system.users_classes import User, LoggedInUser

import threading
# Exceptions
from src.protocol_classes.classes_utils import Result, TypedList, TypedDict

from src.domain.system.db_config import db


class UserNotExists(Exception):
    """When user trying to perform actions while he is not logged in"""


class DataHandler:
    __instance = None

    @staticmethod
    def get_instance():
        """ Static access method. """
        if DataHandler.__instance is None:
            DataHandler()
        return DataHandler.__instance

    def __init__(self):
        from src.domain.system.users_classes import User
        """ Virtually private constructor. """
        self._dal: DAL = DAL.get_instance()
        self._db = None
        self._admins = TypedList(User)
        self._users = TypedDict(int, User)
        self._users_lock = threading.Lock()
        self._stores = dict()
        self._stores_lock = threading.Lock()
        self._purchases = TypedList(Purchase)
        self._guest_id = 1
        self._initialize = False
        DataHandler.__instance = self

    def num_of_users(self) -> int:
        return self._dal.get_num_of_registered_users()

    def create_all(self, init_app):
        # Do not remove
        if self._db is None:
            self._db = db
            init_app(self._db)  # Bind the server
            self._dal.update_session(db)
            self._db.create_all()
            # receive_after_create()

    def insert_some_fun(self):
        self._dal.insert_some_fun()

    @property
    def admins(self):
        return self._admins

    @property
    def users(self):
        return self._users

    @property
    def stores(self):
        return self._stores

    @property
    def purchases(self):
        return self._purchases

    def add_or_update_user(self, user_id, new_user: User):
        """
        adding new user to data_handler or updating existing one
        :param user_id: (int) id of the user
        :param new_user: (User) user to add
        :return: None
        """
        self._users[user_id] = new_user

    def add_admin(self, admin: User, user_name: str):
        from src.domain.system.permission_classes import Permission, Role
        """
        adding new admin to the system
        :param admin: User obj of a new admin user
        :return: None
        """
        # perm: Permission = Permission.define_permissions_for_init(Role.system_manager, user_name, None,
        #                                                          None)
        # self._dal.add(admin.user_state)
        # self._dal.add(perm)
        state: LoggedInUser = admin.user_state
        state._admin_counter = 1
        self.update_stats_counter_for_user(1, state.user_name, Role.system_manager.value)
        self._admins.append(admin)
        self._dal.add(state, add_only=True)

    def admins_user_ids(self):
        """
        get all the id's of all admins
        :return: lists of al admins users
        """
        return [user.user_id for user in self._admins]

    def check_user_id_exists(self, user_id: int):
        """
        checks if a given code is in the system
        :param user_code: id to look for
        :return: True if found false otherwise
        """
        return user_id in self._users

    def get_user_by_id_as_result(self, user_id):
        if self.check_user_id_exists(user_id):
            return Result(True, user_id, "User found", self._users[user_id])
        return Result(False, user_id, "User not found", None)

    def get_id_by_name(self, name: str):
        """
        get user id by name
        :param name: (str) id of a user
        :return: SavedUser object if exists, None otherwise
        """
        user: User = self.get_user_by_username(name)
        return -1 if user is None else user.user_id

    def get_user_by_username(self, name: str) -> LoggedInUser:
        """
        get user id by name
        :param name: (str) id of a user
        :return: SavedUser object if exists, None otherwise
        """
        for user_id in self._users:
            current: User = self._users[user_id]
            if current.user_state is not None:
                temp = self._dal.add(current.user_state, add_only=True)
                if temp:
                    current.user_state = temp
                if current.user_state.user_name == name:
                    return current.user_state
        loaded_user: LoggedInUser = self._dal.get_user_by_name(name)
        temp = self._dal.add(loaded_user, add_only=True)
        if temp:
            loaded_user = temp
        # if loaded_user is not None:
        #     # self._users[user.user_id] = user
        return loaded_user

    def user_state_is_none(self, user_id: int):
        ret = self._users.get(user_id, None)
        if ret is not None:
            ret = ret.user_state
        return Result(True, user_id, "", ret)

    def get_user_by_username_login(self, name: str):
        """
        get user id by name
        :param name: (str) id of a user
        :return: SavedUser object if exists, None otherwise
        """
        for user_id in self._users:
            current: User = self._users[user_id]
            if current.user_state is not None:
                temp = self._dal.add(current.user_state, add_only=True)
                if temp:
                    current.user_state = temp
                if current.user_state.user_name == name:
                    return current.user_state, user_id
        loaded_user: LoggedInUser = self._dal.get_user_by_name(name)

        if loaded_user is not None:
            temp = self._dal.add(loaded_user, add_only=True)
            if temp:
                loaded_user = temp
        # if loaded_user is not None:
        #     # self._users[user.user_id] = user
        return loaded_user, -1

    def add_or_update_user_state(self, state: LoggedInUser, user_id: int):
        user: User = self._users[user_id]
        user.user_state = state

    def get_user_by_username_as_result(self, username: str) -> Result:
        u, user_id = self.get_user_by_username_login(username)
        if u:
            return Result(True, user_id, "User found", u)
        return Result(False, user_id, "User not found", None)

    def get_user_by_id(self, user_id: int):
        """
        get user by id.
        :param user_id: (int) id of a user
        :return: SavedUser object if exists, None otherwise
        """

        if user_id in self._users:
            return self._users[user_id]
        # else:
        #     user: User = self._dal.get_user_by_id(user_id)
        #     if user is not None:
        #         self._users[user_id] = user
        return None

    def get_store_by_name_as_dictionary(self, username: str, store_name: str):
        """
        give info on store
        :param user_id: id of the user requesting the info
        :param store_name: (str) store name
        :return: Result with info of store if found
        """
        store: Store = self._get_store_by_name(store_name)
        if store is not None:
            return Result(True, -1, "store was found", store.to_dictionary(with_permissions=True))
        else:
            return Result(False, -1, "store was not found", None)

    def _get_store_by_name(self, store_name: str):
        """
        get store from map or database if neccessary by name
        :param store_name: name of the store
        :return: Store if exists
        """
        # if store_name in self._stores:
        #     return self._stores[store_name]
        # else:
        store: Store = self._dal.get_store_by_name(store_name)
        return store

    def get_store_by_name(self, store_name: str):
        from src.domain.system.store_classes import Store
        """
        give info on store
        :param store_name: (str) store name
        :return: Result with info of store if found
        """
        store: Store = self._get_store_by_name(store_name)
        if store is not None:
            return Result(True, -1, "store was found", store)
        else:
            return Result(False, -1, "store was not found", None)

    def get_store_that_contains_name(self, store_name: str):
        """
        give all stores which have the given name in their store name
        :param store_name: name to search
        :return: list of store with relevant names
        """
        # with self._stores_lock:
        #     output = []
        #     for key, store in self.stores.items():
        #         if (store_name == "" or store_name in key) and store.open:
        #             output.append(store.copy())
        #     return output
        return self._dal.get_store_that_contains_name(store_name)

    def get_stores_by_names(self, store_names: TypedList):
        """
        get all the available Stores of the available List
        :param store_names: TypedList of Str filled with wanted store Names
        :return: TypedList of Store object according to the given names. if given list is empty, Return all available stores
        """
        if len(store_names) == 0:
            return Result(True, -1, "all stores", self._stores.values())
        else:
            output = []
            with self._stores_lock:
                for store_name in store_names:
                    if store_name in self._stores:
                        output.append(self._stores[store_name])
            return Result(True, -1, "stores were found", output)

    def get_stores_according_to_list(self, stores_name: TypedList):
        initial_list = self._dal.get_all_stores_according_to_list(stores_name)
        if initial_list is None or len(initial_list) == 0:
            return []
        return [s for s in initial_list if s.open]

    def add_purchase(self, purchase: Purchase):
        """
        add new purchase to purchase collection
        :param purchase: Purchase object to add
        :return: None
        """
        self._purchases.append(purchase)

    def is_admin(self, to_check: any):
        """
        check if given user is admin
        :param to_check: User to check
        :return: True if admin, False otherwise
        """
        from src.domain.system.users_classes import User
        if type(to_check) == User:
            return to_check in self._admins
        elif type(to_check) == str:
            return to_check in [u.user_state.user_name for u in self._admins]
        else:
            raise TypeError

    def add_store(self, store: Store):
        """
        Adds new store to data Handler
        :param store: Store object to add
        :return: None
        """
        self._stores[store.name] = store

    def register(self, new_user_id: int, username: str, password: str, email: str):
        """
        registering a given user to the system
        :param guest: User object to register
        :param username: username of the user
        :param password: hashed password of the user
        :param email: email of the user
        :return:
        """
        from src.domain.system.users_classes import User
        if not self._initialize:
            self._initialize = self.num_of_users() > 0
        if new_user_id in self._users:
            new_user: User = self._users[new_user_id]
            if new_user.is_registered():
                return Result(False, new_user_id, "The given id is belonged to a registered user", None)
            new_user = new_user.register(username, password, email)
            if not self._initialize:
                self.add_admin(new_user, username)
                self._initialize = True
            new_user.user_state = None
            # self._dal.add(new_user)
        else:
            if new_user_id == -1:
                new_user: User = User.create_new_user_for_guest(-1)
                new_user_id = new_user.user_id
            else:
                new_user: User = User(new_user_id)
            new_user = new_user.register(username, password, email)
            if not self._initialize:
                self.add_admin(new_user, username)
                self._initialize = True
            new_user.user_state = None
            # self._dal.add(new_user)
            user_id = new_user.user_id
            self.users[user_id] = new_user

        return Result(True, new_user_id, "success", None)

    def login(self, user_id: int, registered_user: LoggedInUser):
        """
        logging in a registered user to the system
        :param user_id: id of the requesting user
        :param user_name: username of the user to log in
        :param password: password of the user who wants to log in
        :return: Result with the result process
        """
        user: User = self.get_user_by_id(user_id)
        if user is None:
            return Result(False, user_id, "Something went wrong in login", None)
        user.user_state = registered_user
        user.shopping_cart.baskets = registered_user.get_shopping_cart_of_user()
        user.login()
        return Result(True, user_id, "success login", None)

    def logout(self, user_id: int):
        """
        logging out a user from the system
        :param user_id: id of the user who wants to log out
        :return: Result with Info on the process
        """
        if user_id in self.users:
            user: User = self.users[user_id]
            # todo if none check if exists exists in db
            if user.logout():
                # del self._users[user_id]
                return Result(True, user_id, "success", None)
            else:
                return Result(False, user_id, "user is not registered or user already not connected to the system",
                              None)
        return Result(False, user_id, "user id is not exist", None)

    def remove_permission_of_user_from_store(self, username, storename):
        try:
            user: User = self.get_user_by_username_wrapper(username)
            if user:
                user: LoggedInUser = user.user_state
                if user:
                    if storename in user.permissions:
                        user.remove_permission(storename)
        except Exception as e:
            pass

    def update_users_after_remove(self):
        for user in self._users.values():
            if user.user_state:
                user: LoggedInUser = user.user_state
                self._dal.add(user, add_only=True)
                to_delete = []
                for p in user.permissions.keys():
                    if p not in user._permissions_list:
                        to_delete.append(p)
                for p in to_delete:
                    del user.permissions[p]

                # ret = self._dal.get_permission_by_username_from_loggedInUsers(user.user_name)
                # for s in ret._permissions_list:
                #     if s not in user.permissions:
                #         res = self._dal.get_permission_by_user_fk_store_fk(user.user_name, s)
                #         if res:
                #             user._permissions[s] = res

    def get_user_by_username_wrapper(self, name: str) -> User:
        for user_id in self._users:
            current: User = self._users[user_id]
            if current.user_state is not None:
                if current.user_state.user_name == name:
                    return current
        return None

    def save_purchases(self, purchases: TypedList):
        """saving given purchases"""
        self.purchases.extend(purchases)

    def commit_session(self):
        self._dal.commit()

    # def get_user_by_userId_as_loggedInUser(self, username):
    #     try:
    #         u: User = self._users.get(username)
    #         return Result(True, -1, "Found", u.user_state)
    #     except:
    #         return Result(False, -1, "Could not found user", None)

    def update_stats_counter_for_user(self, counter_change: int, username: str, role: int):
        user: LoggedInUser = self.get_user_by_username(username)
        old_categ = user.get_category()
        if role == 1:  # sys manager
            user._admin_counter += counter_change
        elif role == 3:
            user._owner_counter += counter_change
        elif role == 4:
            user._manager_counter += counter_change
        new_categ = user.get_category()
        _, user_id = self.get_user_by_username_login(user.user_name)
        if user_id != -1:
            StatManager.get_instance().transition(new_categ, old_categ)
