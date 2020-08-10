from sqlalchemy import orm
from sqlalchemy.ext.mutable import MutableList

import src.domain.system.permission_classes as pc
from src.communication.notification_handler import Category
from src.domain.system.DAL import DAL
from src.domain.system.cart_purchase_classes import ShoppingCart, Purchase
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.system.data_handler import DataHandler
from src.domain.system.db_config import db
from src.logger.log import Log
from src.protocol_classes.classes_utils import TypedDict, TypedList, Result

import uuid


class DBError(Exception):
    """Base class for db exceptions"""
    pass


id_counter = 0


def generate_id():
    """
    generating new user id (positive integer)
    :return: new user id
    """
    global id_counter
    id_counter += 1
    return id_counter


class LoggedInUser(db.Model):
    __tablename__ = 'loggedInUsers'
    _dal: DAL = DAL.get_instance()
    _user_name = db.Column(db.String(250), primary_key=True)
    _password = db.Column(db.VARCHAR(256))
    # _shopping_cart_fk = db.Column(db.Integer, db.ForeignKey("shopping_cart.id"))
    _email = db.Column(db.VARCHAR(240))  # todo enforce email length somewhere
    _permissions_list = db.Column(MutableList.as_mutable(db.JSON))
    _manager_counter = db.Column(db.Integer)
    _owner_counter = db.Column(db.Integer)
    _admin_counter = db.Column(db.Integer)

    def __init__(self, user_name: str, password: str, email: str):

        if not ((type(user_name) is str) and (type(email) is str) and (type(password) is str)):
            raise TypeError("Wrong types, or list not matching the wanted type")
        self._permissions_list = []
        self.user_name = user_name
        self.password = password
        self.email = email
        self.is_connected = True
        self._permissions = TypedDict(str, pc.Permission)
        self._manager_counter = 0
        self._owner_counter = 0
        self._admin_counter = 0
        # self._shopping_cart_fk = shopping_cart_id

    # this constructor is called each time we load the object from the data base
    @orm.reconstructor
    def _init_on_load(self):
        self._purchases = TypedList(Purchase)
        self._permissions = self._dal.get_permission_with_id_keys_for_user(self._permissions_list, self._user_name)

    def get_shopping_cart_of_user(self):
        res = self._dal.get_baskets_by_user(self._user_name)
        for basket in res.values():
            self._dal.add(basket, add_only=True)
        return res

    @property
    def user_name(self):
        return self._user_name

    @user_name.setter
    def user_name(self, new_user_name: str):
        if isinstance(new_user_name, str):
            self._user_name = new_user_name

    # @property
    # def purchases(self):
    # #     return self._purchases
    #
    # @purchases.setter
    # def purchases(self, new_purchases: TypedDict):
    #     if isinstance(new_purchases, TypedList) and new_purchases.check_types(Purchase):
    #         self._purchases = new_purchases

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password: str):
        if isinstance(new_password, str):
            self._password = new_password

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email: str):
        if isinstance(new_email, str):
            self._email = new_email

    @property
    def is_connected(self):
        return self._is_connected

    @is_connected.setter
    def is_connected(self, new_is_connected: bool):
        if isinstance(new_is_connected, bool):
            self._is_connected = new_is_connected

    @property
    def permissions(self):
        return self._permissions

    def add_permission(self, new_permission: pc.Permission):
        """
        adding a new permission connection between this user to a given store
        :param new_permission: Permission to add to this user
        :return: True if added successfully, False if permission to that store already exists
        """
        if new_permission._role == pc.Role.system_manager.value:
            self.adding_permission(new_permission, '')
            return True
        elif new_permission._store_fk in self._permissions:
            return False  # permission to this store already exists
        else:
            self.adding_permission(new_permission, new_permission._store_fk)
            return True

    def adding_permission(self, new_permission, name):
        self._permissions_list.append(name)
        self._dal.add(self, add_only=True)
        self._permissions[name] = new_permission

    def remove_permission(self, store_name: str):
        """
        remove permission for actions in a given store
        :param store_name: (str) name of the store to remove
        :return: None
        """

        if store_name in self._permissions_list:
            self._permissions_list.remove(store_name)
        perm_to_remove = self._permissions.pop(store_name)
        self._dal.add(perm_to_remove, add_only=True)

    def view_all_purchases(self):
        """
        :return: list of all purchases of this user as dictionaries
        """
        output = self._dal.get_purchases_of_user(self._user_name)

        return [p.to_dictionary() for p in output]

    def is_admin(self):
        # if '' in self.permissions:
        #     perm: pc.Permission = self.permissions['']
        #     self._dal.add(perm, add_only=True)
        #     if perm.role == pc.Role.system_manager.value:
        #         return True
        # return False
        # return '' in self._dal.get_permission_with_id_keys_for_user(self._user_name)
        return self._dal.is_admin(self._user_name)

    def login(self):
        self._is_connected = True
        return True

    def get_category(self):
        if self._admin_counter > 0:
            return Category.system_manager.to_string()
        elif self._owner_counter > 0:
            return Category.store_owner.to_string()
        elif self._manager_counter > 0:
            return Category.store_manager.to_string()
        else:
            return Category.logged_in.to_string()


class User:
    _user_id = None
    _dal: DAL = DAL.get_instance()

    def __init__(self, guest_id):
        shopping_cart = ShoppingCart()
        # self._dal.add(shopping_cart, add_only=True)
        self._user_id = guest_id
        self._shopping_cart: ShoppingCart = shopping_cart
        self._state = None

    # class User:
    #
    #     def __init__(self, user_id: int, shopping_cart: ShoppingCart = None):
    #         if shopping_cart is None:
    #             shopping_cart = ShoppingCart()
    #         self._state: LoggedInUser = None
    #         self._shopping_cart: ShoppingCart = shopping_cart
    #         self._user_id = user_id
    #         # self._purchases = TypedDict(str, TypedList) moved to LIU

    @property
    def user_state(self):
        return self._state

    @user_state.setter
    def user_state(self, new_user_state: LoggedInUser):
        # if isinstance(new_user_state, LoggedInUser):
        self._state = new_user_state

    @property
    def shopping_cart(self):
        # if LIU == null --> return shopping cart
        # else go to dal and get shopping cart
        return self._shopping_cart

    @property
    def user_id(self):
        return self._user_id

    def register(self, username: str, password: str, email: str):
        # self._dal.add(self._shopping_cart)
        self.user_state: LoggedInUser = LoggedInUser(username, password, email)
        for basket in self.shopping_cart.baskets.values():
            self._dal.add(basket)
            basket._user = self.user_state.user_name
        self._shopping_cart = ShoppingCart()
        self._dal.add(self.user_state, add_only=True)
        return self

    def is_registered(self):
        return self.user_state is not None

    def login(self):
        return self.user_state.login()

    def logout(self):
        if self.is_registered():
            # state: LoggedInUser = self.user_state
            self.user_state = None
            return True
        else:
            return False

    def convert_shopping_cart_to_dictionary(self):
        """
        converting the current shopping cart to dictionary
        :return: dict representing the given shopping cart
        """
        # result: dict = {}
        # stores: list = []
        # total_price: float = 0.0
        # for store in self.shopping_cart.keys():
        #     current_list = [
        #         {"product_name": p.product.name, "quantity": p.quantity, "price": p.price.calc_price()} for
        #         p in self.shopping_cart[store].values()]
        #     total_price += reduce(lambda acc, c: acc + c,
        #                           [p.price.calc_price() * p.quantity for p in self.shopping_cart[store].values()])
        #     stores.append(current_list)
        # result["stores_baskets"] = stores
        # result["total_price"] = total_price
        # return result
        return self.shopping_cart.to_dictionary()

    def calculate_shopping_cart_price(self):
        """
        calculate the price of the cart
        :return: final price of the shopping cart
        """
        # total_price: float = 0.0
        # for store in self.shopping_cart.keys():
        #     total_price += reduce(lambda acc, c: acc + c,
        #                           [p.price.calc_price() * p.quantity for p in self.shopping_cart[store].values()])
        # return total_price
        return self.shopping_cart.get_total_value_of_shopping_cart()

    def is_admin(self):
        """
        checking if the current user is admin
        :return: True if admin False otherwise
        """
        if self.user_state is None:
            return False
        return self.user_state.is_admin()

    @staticmethod
    def create_new_user_for_guest(user_id):
        if user_id >= 0:
            return User(user_id)
        _user_id = int((uuid.uuid4().int >> 64) / 100000000000)
        new_user: User = User(_user_id)
        return new_user


class UserSystemHandler:

    def __init__(self, d_handler):
        self._d_handler: DataHandler = d_handler
        self._dal: DAL = DAL.get_instance()

    @property
    def data_handler(self):
        return self._d_handler

    def user_state_is_none(self, user_id: int):
        return self.data_handler.user_state_is_none(user_id)

    def register_user(self, user_id: int, user_name: str, password: str, email: str):
        """
        :param user_id: user id of user, if he has no id, default value is -1
        :param user_name:
        :param password:
        :param email:
        :return: Result object contains True / False if the operation succeeded, user_id and message
        """

        res: Result = self.data_handler.register(user_id, user_name, password, email)
        return res

    def login_user(self, user_id: int, user):
        """
        :param user_id: input user_id

        :return: Result object contains True / False if the operation succeeded, user_id and message
        """
        return self.data_handler.login(user_id, user)

    def logout(self, user_id: int):
        """
        :param user_id: input user_id
        :return: Result object contains True / False if the operation succeeded, user_id and message
        """
        return self.data_handler.logout(user_id)

    def get_user_stored_password(self, user_id: int):
        """
        :param user_id: (int) user id of the wanted user
        :return:  stored password of user, if exists
        """
        user = self.data_handler.get_user_by_id(user_id)
        if user is None:
            return Result(False, user_id, "user doesn't exist", None)
        if user.is_registered():
            state = user.user_state
            return Result(True, user_id, "success", state.password)
        return Result(False, user_id, "user doesn't register to the system", None)

    # def check_username_exist(self, user_id: int, username: str):
    #     """
    #     :param user_id: (int) user id of the wanted user
    #     :param username:  (str) user name of the wanted user
    #     :return: Result object with info on the process
    #     """
    #     user = self.data_handler.get_user_by_id(user_id)
    #     if user is None:
    #         return Result(False, user_id, "user doesn't exist", None)
    #     if user.is_registered():
    #         state = user.user_state
    #         if state.user_name == username:
    #             return Result(True, user_id, "success", None)
    #         else:
    #             return Result(False, user_id, "username is not exist", None)
    #     else:
    #         return Result(False, user_id, "user doesn't register to the system", None)

    def check_username_already_exist(self, username: str):
        """
        :param username:  (str) user name of the wanted user
        :return: Result object with info on the process
        """
        if self._dal.get_user_by_name(username) is not None:
            # if self._d_handler.get_user_by_username_as_result(username) != -1:
            return Result(True, -1, "success", None)
        else:
            return Result(False, -1, "user name was not found", None)

    def get_user_by_username_as_result(self, username):
        return self._d_handler.get_user_by_username_as_result(username)

    def get_store_by_name(self, storename):
        return self._d_handler.get_store_by_name(storename)

    def get_user_by_id(self, user_id):
        return self._d_handler.get_user_by_id_as_result(user_id)

    # def _check_and_handle_new_user(self, user_id):
    #     if user_id <= 0:
    #         # creating user and save it to the database
    #         new_user: User = User.create_new_user_for_guest()
    #         user_id = new_user.user_id
    #         self._d_handler.add_or_update_user(user_id, new_user)
    #     return user_id

    # def get_user_by_id_if_guest_create_one(self, user_id: int):
    #     user: User = self._d_handler.get_user_by_id(user_id)
    #     if user is None:
    #         new_user: User = User.create_new_user_for_guest(user_id)
    #         user_id = new_user.user_id
    #         self._d_handler.add_or_update_user(user_id, new_user)
    #     return Result(True, user_id, "Created user", user_id)

    def get_user_by_id_if_guest_create_one(self, user_id: int):
        user: User = self._d_handler.get_user_by_id(user_id)
        if user is None:
            user: User = User.create_new_user_for_guest(user_id)
            self._d_handler.add_or_update_user(user.user_id, user)
        return Result(True, user.user_id, "user:", user.user_id)

    def update_stats_counter_for_user(self, counter_change: int, username: str, role: int):
        self.data_handler.update_stats_counter_for_user(counter_change, username, role)
