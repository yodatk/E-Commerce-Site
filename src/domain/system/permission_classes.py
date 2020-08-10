from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import orm
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm.attributes import flag_modified

from src.logger.log import Log

if TYPE_CHECKING:
    from src.domain.system.users_classes import User, LoggedInUser
    from src.domain.system.store_classes import Store

import enum
from src.protocol_classes.classes_utils import Result, TypedDict, TypedList
from src.domain.system.db_config import db
from src.domain.system.DAL import DAL
from sqlalchemy.orm.session import make_transient


class Role(enum.Enum):
    system_manager = 1
    store_initial_owner = 2
    store_owner = 3
    store_manager = 4

    def to_string(self):
        if self == Role.system_manager:
            return "System Manager"
        elif self == Role.store_initial_owner:
            return "Initial Owner"
        elif self == Role.store_owner:
            return "Owner"
        else:
            return "Manager"


class Permission(db.Model):
    """
    relation class between Store and User, that defines the actions a certain user can do in a store
    """
    __tablename__ = 'permissions'
    # id = db.Column(db.Integer, primary_key=True)
    _role = db.Column(db.Integer)
    _dal: DAL = DAL.get_instance()
    _store_fk = db.Column(db.String(50), db.ForeignKey("store._name"), primary_key=True)
    _user_fk = db.Column(db.String(50), db.ForeignKey("loggedInUsers._user_name"), primary_key=True)
    _appointed_by_fk = db.Column(db.String(50), db.ForeignKey("loggedInUsers._user_name"), nullable=True)
    _store = db.relationship("Store", lazy="joined")  # TODO1
    _user = db.relationship("LoggedInUser", lazy="joined", foreign_keys=[_user_fk])  # TODO1
    _appointed_by = db.relationship("LoggedInUser", lazy="joined", foreign_keys=[_appointed_by_fk])  # TODO1
    _can_manage_inventory = db.Column(db.Boolean)
    _appoint_new_store_owner = db.Column(db.Boolean)
    _appoint_new_store_manager = db.Column(db.Boolean)
    _watch_purchase_history = db.Column(db.Boolean)
    _open_and_close_store = db.Column(db.Boolean)
    _can_manage_discount = db.Column(db.Boolean)
    _managers_appointed_ls = db.Column(MutableList.as_mutable(db.JSON))
    _owners_appointed_ls = db.Column(MutableList.as_mutable(db.JSON))

    def __init__(self, store: str, user: str, appointed_by: str, role: Role,
                 can_manage_inventory: bool = False,
                 appoint_new_store_owner: bool = False,
                 appoint_new_store_manager: bool = False,
                 open_and_close_store: bool = False,
                 can_manage_discount: bool = False,
                 watch_purchase_history: bool = True, user_obj=None, store_obj=None, appointed_by_obj=None):

        self._role = role.value
        self._store = store_obj
        self._store_fk = store  # if store is not None else ""  # store.name if store is not None else ""
        # self._user = user_obj
        self._user_fk = user  # .user_state.user_name if user is not None else ""
        self._appointed_by = appointed_by_obj
        self._appointed_by_fk = appointed_by  # .user_state.user_name if appointed_by is not None else ""
        self.can_manage_inventory = can_manage_inventory
        self.appoint_new_store_owner = appoint_new_store_owner
        self.appoint_new_store_manager = appoint_new_store_manager
        self.watch_purchase_history = watch_purchase_history
        self.open_and_close_store = open_and_close_store
        self.can_manage_discount = can_manage_discount
        # self._managers_appointed = TypedDict(str, Permission)
        # self._owners_appointed = TypedDict(str, Permission)
        self._managers_appointed_ls = []
        self._owners_appointed_ls = []

    @property
    def managers_appointed(self):
        from src.domain.system.data_handler import DataHandler
        _data_handler: DataHandler = DataHandler.get_instance()
        self._dal.add(self, add_only=True)
        temp = self._dal.get_permission_with_id_keys(self._managers_appointed_ls, self._store_fk)
        for u in _data_handler.users.values():
            if u.user_state is not None:
                p: Permission = u.user_state.permissions.get(self._store_fk)
                if p:
                    res = self._dal.add(p, add_only=True)
                    if res:
                        p = res
                        u.user_state.permissions[self._store_fk] = res
                    if p._appointed_by_fk == self._user_fk and p.role == Role.store_manager.value:
                        temp[p._user_fk] = p
        return temp

    @property
    def owners_appointed(self):
        from src.domain.system.data_handler import DataHandler
        _data_handler: DataHandler = DataHandler.get_instance()
        temp = self._dal.get_permission_with_id_keys(self._owners_appointed_ls, self._store_fk)
        for u in _data_handler.users.values():
            if u.user_state is not None:
                p: Permission = u.user_state.permissions.get(self._store_fk)
                if p:
                    res = self._dal.add(p, add_only=True)
                    if res:
                        p = res
                        u.user_state.permissions[self._store_fk] = res
                    if p._appointed_by_fk == self._user_fk and p.role == Role.store_owner.value:
                        temp[p._user_fk] = p
        return temp

    @property
    def role(self):
        return self._role

    @property
    def store(self):
        return self._store

    # @property
    # def username(self):
    #     return self._user.user_state.user_name

    @property
    def user(self):
        return self._user

    @property
    def appointed_by(self):
        return self._appointed_by

    @property
    def can_manage_inventory(self):
        return self._can_manage_inventory

    @can_manage_inventory.setter
    def can_manage_inventory(self, permission: bool):
        if isinstance(permission, bool):
            self._can_manage_inventory = permission

    @property
    def appoint_new_store_owner(self):
        return self._appoint_new_store_owner

    @appoint_new_store_owner.setter
    def appoint_new_store_owner(self, permission: bool):
        if isinstance(permission, bool):
            self._appoint_new_store_owner = permission

    @property
    def appoint_new_store_manager(self):
        return self._appoint_new_store_manager

    @appoint_new_store_manager.setter
    def appoint_new_store_manager(self, permission: bool):
        if isinstance(permission, bool):
            self._appoint_new_store_manager = permission

    @property
    def watch_purchase_history(self):
        return self._watch_purchase_history

    @watch_purchase_history.setter
    def watch_purchase_history(self, permission: bool):
        if isinstance(permission, bool):
            self._watch_purchase_history = permission

    @property
    def open_and_close_store(self):
        return self._open_and_close_store

    @open_and_close_store.setter
    def open_and_close_store(self, permission: bool):
        if isinstance(permission, bool):
            self._open_and_close_store = permission

    @property
    def can_manage_discount(self):
        return self._can_manage_discount

    @can_manage_discount.setter
    def can_manage_discount(self, permission: bool):
        if isinstance(permission, bool):
            self._can_manage_discount = permission

    def _convert_value_to_role_string(self):
        if self._role == 1:
            return "System Manager"
        elif self._role == 2:
            return "Initial Owner"
        elif self._role == 3:
            return "Owner"
        elif self._role == 4:
            return "Manager"
        else:
            return ""

    def to_dictionary(self) -> dict:
        """
        :return: dictionary representation of the Permission object
        """
        sub_managers_list = {}
        sub_owners_list = {}
        for name, perm in self.managers_appointed.items():
            sub_managers_list[name] = perm.to_dictionary()
        for name, perm in self.owners_appointed.items():
            sub_owners_list[name] = perm.to_dictionary()
        return {
            'role': self._convert_value_to_role_string(),
            'store_name': self._store_fk,
            'user': self.user.user_name,
            'appointed_by': self.appointed_by.user_name,
            'can_manage_inventory': self.can_manage_inventory,
            'can_manage_discount': self.can_manage_discount,
            'open_and_close_store': self.open_and_close_store,
            'watch_purchase_history': self.watch_purchase_history,
            'appoint_new_store_manager': self.appoint_new_store_manager,
            "appoint_new_store_owner": self.appoint_new_store_owner,
            'managers_appointed': sub_managers_list,
            'owners_appointed': sub_owners_list
        }

    @staticmethod
    def define_permissions_for_init(role: Role, user: str, store: str, appointed_by: str = None, user_obj=None,
                                    store_obj=None, appointed_by_obj=None):

        """
        return default permission according to role
        :return: permission - contains all the permissions active.
        """
        if role == Role.system_manager:
            perm: Permission = Permission(None, user, None, role, True, True, True, True, True, True,
                                          user_obj, store_obj)
        elif role != Role.store_manager:
            perm: Permission = Permission(store, user, appointed_by, role, True, True, True, True, True,
                                          watch_purchase_history=True, user_obj=user_obj, store_obj=store_obj,
                                          appointed_by_obj=appointed_by_obj)
        else:
            # todo: set the True to False again.
            perm: Permission = Permission(store, user, appointed_by, role, False, False, True, False, False,
                                          watch_purchase_history=True, user_obj=user_obj, store_obj=store_obj,
                                          appointed_by_obj=appointed_by_obj)
        return perm

    def add_simple_product_discount(self, end_time: datetime, discount_percent: float, discounted_product: str,
                                    size_of_basket_cond: int = None,
                                    over_all_price_category_cond: list = None,
                                    over_all_price_product_cond: list = None, product_list_cond: list = None,
                                    overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding simple product discount, according to given conditions, if possible
        :param end_time: the expiration date of the discount
        :param discount_percent: the discount percent to deduce from the price of the product
        :param discounted_product: name of the product to give discount to
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on
        :param discount_id: (int) discount id to edit. if negative -> adding a new discount
        :return: Result with info on process
        """
        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.add_simple_product_discount(end_time, discount_percent, discounted_product,
                                                                 size_of_basket_cond,
                                                                 over_all_price_category_cond,
                                                                 over_all_price_product_cond, product_list_cond,
                                                                 overall_category_quantity, discount_id)
            if res.succeed:
                return Result(True, -1, res.msg, res.data)
            else:
                return Result(False, -1, res.msg, res.data)

    def add_free_per_x_product_discount_discount(self, end_time: datetime, product_name: str, free_amount: int,
                                                 per_x_amount: int, is_duplicate: bool = True,
                                                 size_of_basket_cond: int = None,
                                                 over_all_price_category_cond: list = None,
                                                 over_all_price_product_cond: list = None,
                                                 product_list_cond: list = None,
                                                 overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding Free Per X kind of discount on a given product, if possible
        :param end_time: (datetime) the expiration date of the discount
        :param product_name: name of the product to do discount on
        :param free_amount: (int)number of items to get free on each x items you bought
        :param per_x_amount:(int) number of items to buy to get the free ones
        :param is_duplicate:(bool) is to perform this discount until there are no more of the given product, or just 1 time (default True)
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :param discount_id: (int) discount id to edit. if negative -> adding a new discount
        :return: Result with info on process
        """
        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.add_free_per_x_product_discount_discount(end_time, product_name, free_amount,
                                                                              per_x_amount,
                                                                              is_duplicate,
                                                                              size_of_basket_cond,
                                                                              over_all_price_category_cond,
                                                                              over_all_price_product_cond,
                                                                              product_list_cond,
                                                                              overall_category_quantity, discount_id)
            if res.succeed:
                return Result(True, -1, res.msg, res.data)
            else:
                return Result(False, -1, res.msg, res.data)

    def add_simple_category_discount(self, end_time: datetime, discount_percent: float, discounted_category: str,
                                     size_of_basket_cond: int = None,
                                     over_all_price_category_cond: list = None,
                                     over_all_price_product_cond: list = None, product_list_cond: list = None,
                                     overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding simple category discount, according to given conditions, if possible
        :param end_time: the expiration date of the discount
        :param discount_percent: the discount percent to deduce from the price of the product
        :param discounted_category: name of the product to give discount to
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on
        :param discount_id: (int) discount id to edit. if negative -> adding a new discount
        :return: Result with info on process
        """
        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.add_simple_category_discount(end_time, discount_percent, discounted_category,
                                                                  size_of_basket_cond,
                                                                  over_all_price_category_cond,
                                                                  over_all_price_product_cond, product_list_cond,
                                                                  overall_category_quantity, discount_id)
            if res.succeed:
                return Result(True, -1, res.msg, res.data)
            else:
                return Result(False, -1, res.msg, res.data)

    def add_free_per_x_category_discount(self, end_time: datetime, category_name: str, free_amount: int,
                                         per_x_amount: int, is_duplicate: bool = True,
                                         size_of_basket_cond: int = None,
                                         over_all_price_category_cond: list = None,
                                         over_all_price_product_cond: list = None,
                                         product_list_cond: list = None,
                                         overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding Free Per X kind of discount on a given category, if possible
        :param end_time: (datetime) the expiration date of the discount
        :param category_name: name of the product to do discount on
        :param free_amount: (int)number of items to get free on each x items you bought
        :param per_x_amount:(int) number of items to buy to get the free ones
        :param is_duplicate:(bool) is to perform this discount until there are no more of the given product, or just 1 time (default True)
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :param discount_id: (int) discount id to edit. if negative -> adding a new discount
        :return: Result with info on process
        """
        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.add_free_per_x_category_discount_discount(end_time, category_name, free_amount,
                                                                               per_x_amount,
                                                                               is_duplicate,
                                                                               size_of_basket_cond,
                                                                               over_all_price_category_cond,
                                                                               over_all_price_product_cond,
                                                                               product_list_cond,
                                                                               overall_category_quantity,
                                                                               discount_id)
            if res.succeed:
                return Result(True, -1, res.msg, res.data)
            else:
                return Result(False, -1, res.msg, res.data)

    def add_basket_discount(self, end_time: datetime, discount_percent: float,
                            size_of_basket_cond: int = None,
                            over_all_price_category_cond: list = None,
                            over_all_price_product_cond: list = None, product_list_cond: list = None,
                            overall_category_quantity: list = None, discount_id: int = -1):
        """
        add a discount percent on the entire basket
        :param end_time: expiration date of the discount
        :param discount_percent: the amount of percent disocount
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :param discount_id: (int) discount id to edit. if negative -> adding a new discount
        :return: Result with info on process
        """

        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.add_discount_on_entire_store(end_time, discount_percent,
                                                                  size_of_basket_cond,
                                                                  over_all_price_category_cond,
                                                                  over_all_price_product_cond,
                                                                  product_list_cond,
                                                                  overall_category_quantity, discount_id)
            if res.succeed:
                return Result(True, -1, res.msg, res.data)
            else:
                return Result(False, -1, res.msg, res.data)

    def remove_discount(self, discount_id: id):
        """
        removing discount
        :param discount_id: id of the discount
        :return: Result with info on process
        """
        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.remove_discount_from_store(discount_id)
            if res.succeed:
                return Result(True, -1, res.msg, res.data)
            else:
                return Result(False, -1, res.msg, res.data)

    def get_all_discount(self):
        """
        getting all discount in store
        :return:
        """
        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            output: Result = self.store.fetch_all_discounts()
            return Result(output.succeed, -1, output.msg, output.data)

    def combine_discounts(self, discounts_id_list: list, operator: str):
        """
        combine given discounts with operator
        :param discounts_id_list: list of discounts id to combine
        :param operator: logic operator to combine
        :return: discount id of the new combine discount
        """
        if not self.can_manage_discount:
            return Result(False, -1, "Permission denied", None)
        else:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.combine_discounts(discounts_id_list, operator)
            if res.succeed:
                return Result(True, -1, res.msg, res.data)
            else:
                return Result(False, -1, res.msg, res.data)

    def _add_staff_member(self, new_member: LoggedInUser, is_owner_to_add: bool):
        permission_to_check: bool = self.appoint_new_store_owner if is_owner_to_add else self.appoint_new_store_manager
        if not permission_to_check:
            return Result(False, -1, "Permission denied", None)
        if new_member is None:
            return Result(False, -1,
                          f"the new {'owner' if is_owner_to_add else 'manager'} must be a registered user",
                          None)
        self._dal.add(self.store, add_only=True)
        if self.store.name in new_member.permissions:
            return Result(False, -1, "the given user is already defined in this store staff", None)
        else:
            perm: Permission = Permission.define_permissions_for_init(
                Role.store_owner if is_owner_to_add else Role.store_manager, new_member.user_name,
                self.store.name,
                self._user_fk, user_obj=new_member, store_obj=self.store, appointed_by_obj=self.user)
            self._dal.add(perm, add_only=True)
            # perm._user = new_member.user_state
            # perm._store = self.store
            # perm._appointed_by = self.user

            res: Result = self.store.add_store_member(perm)
            if not res.succeed:
                return res
            else:
                new_member.add_permission(perm)
                # self._dal.add(perm, add_only=True)
                # self._dal.flush()  # So we ill able to call .id

                if is_owner_to_add:
                    self._owners_appointed_ls.append(perm._user_fk)
                    # self._owners_appointed[new_member.user_name] = perm
                else:
                    # self.managers_appointed[new_member.user_name] = perm
                    self._managers_appointed_ls.append(perm._user_fk)

                try:
                    self._dal.add(self, add_only=True)
                except:
                    pass

                return Result(True, -1,
                              f"new {'owner' if is_owner_to_add else 'manager'} was added to store",
                              new_member.user_name)

    def add_store_owner(self, new_owner: LoggedInUser):
        """
        The function adds new store owner to the appropriate table.
        :param new_owner: User to appoint as new Owner
        :return Result with info on process
        """
        if self.role == Role.store_manager:
            return Result(False, -1, "only owners can appoint new owners", None)
        return self._add_staff_member(new_owner, is_owner_to_add=True)

    def add_store_manager(self, new_manager: LoggedInUser):
        """
        The function adds new store owner to the appropriate table.
        :param new_manager: User to appoint as new Owner
        :return Result with info on process
        """
        return self._add_staff_member(new_manager, is_owner_to_add=False)

    def _remove_member(self, member_to_remove: str, is_owner: bool, to_delete: list = None,
                       to_delete_from_store: list = None):
        """
        remove a staff member from store management
        :param member_to_remove: name of the user to remove from management
        :param is_owner: bool- True if the user to remove is owner, False otherwise
        :return: Result with info on process
        """
        if to_delete is None:
            to_delete = []
        if to_delete_from_store is None:
            to_delete_from_store = []
        self._dal.add(self, add_only=True)
        collection_to_check = self.owners_appointed if is_owner else self.managers_appointed
        if member_to_remove not in collection_to_check:
            return Result(False, -1,
                          f"cannot remove a {'owner' if is_owner else 'manager'} that you did'nt appoint", None)
        else:
            # removing from this permission object
            self._dal.add(self.store, add_only=True)
            perm: Permission = collection_to_check.pop(member_to_remove)
            self._dal.add(perm, add_only=True)
            store_name = perm._store_fk
            if is_owner:
                if perm._user_fk in self._owners_appointed_ls:
                    self._owners_appointed_ls.remove(perm._user_fk)
            else:
                if perm._user_fk in self._managers_appointed_ls:
                    self._managers_appointed_ls.remove(perm._user_fk)
            if perm.role == Role.store_initial_owner or perm.role == Role.system_manager:
                log: Log = Log.get_instance()
                log.get_logger().error(
                    f"ERROR IN '_remove_member' in Permission class: User {self._user_fk} was trying to remove the System Manager\ the initial owner '{member_to_remove}' of store {self.store.name}")
                return Result(False, -1, f'cannot remove a system Manager or a Store initial owner',
                              None)

            # removing sub owners
            for sub_perm in list(perm.owners_appointed.keys()).copy():
                res: Result = perm.remove_owner(sub_perm)
                if res.succeed:
                    perm_delete, store_delete = res.data
                    to_delete.extend(perm_delete)
                    to_delete_from_store.extend(store_delete)
                else:
                    return res
            # removing sub managers
            for sub_perm in list(perm.managers_appointed.keys()).copy():
                res: Result = perm.remove_manager(sub_perm)
                if res.succeed:
                    perm_delete, store_delete = res.data
                    to_delete.extend(perm_delete)
                    to_delete_from_store.extend(store_delete)
                else:
                    return res
            # removing permission from the user itself - no connection remains
            # self._store.remove_member(member_to_remove)
            # self._dal.add(self._store, add_only=True)
            perm.user.remove_permission(store_name)
            from src.domain.system.data_handler import DataHandler
            _data_handler: DataHandler = DataHandler.get_instance()
            _data_handler.remove_permission_of_user_from_store(member_to_remove, self._store_fk)
            to_delete.append(perm)
            to_delete_from_store.append(member_to_remove)
            return Result(True, -1, f"{'owner' if is_owner else 'manager'} was removed successfully",
                          (to_delete, to_delete_from_store))

    def remove_owner(self, owner_to_remove: str):
        """
        removing an owner that this staff member appointed if possible
        :param owner_to_remove: User to remove from Store as owner
        :return: Result with process info
        """
        if self.role == Role.store_manager.value:
            return Result(False, -1, "only owners can remove owners", None)
        else:
            return self._remove_member(owner_to_remove, is_owner=True)

    def remove_manager(self, manager_to_remove: str):
        """
        removing a manager this staff member appointed if possible
        :param manager_to_remove:
        :return:
        """
        return self._remove_member(manager_to_remove, is_owner=False)

    def edit_permission(self, to_edit: str, can_manage_inventory: bool = False, appoint_new_store_owner: bool = False,
                        appoint_new_store_manager: bool = False,
                        watch_purchase_history: bool = False,
                        open_and_close_store: bool = False,
                        can_manage_discount: bool = False):
        """
        edit permission to a sub staff member if possible
        :param to_edit:username of the User to edit
        :param can_manage_inventory: True if user can manage the inventory of the store, False otherwise
        :param appoint_new_store_owner:  True if user can appoint new owner, False otherwise
        :param appoint_new_store_manager:  True if user can appoint new manager, False otherwise
        :param watch_purchase_history:  True if user can watch store purchase history, False otherwise
        :param open_and_close_store:  True if user can open and close the store, False otherwise
        :param can_manage_discount:  True if user can manage discount of the store, False otherwise
        :return: Result with info
        """
        managers = self.managers_appointed
        # y = self.owners_appointed
        if to_edit not in managers:  # and to_edit not in y:
            return Result(False, -1, "cannot edit permission for manager you didnt appoint", None)
        else:
            perm_to_edit: Permission = managers[to_edit]
            res = self._dal.add(perm_to_edit, add_only=True)
            if res:
                perm_to_edit = res

            if perm_to_edit.role != Role.store_manager.value:
                return Result(False, 0, "cannot edit permissions for somone who isn't a manager",
                              None)
            # self._dal.add(self.store, add_only=True)
            if perm_to_edit.role == Role.store_initial_owner or perm_to_edit.role == Role.system_manager:
                log: Log = Log.get_instance()
                log.get_logger().error(
                    f"ERROR IN 'edit_permission' in Permission class: User {self._user_fk} was trying to edit permossions of the System Manager\ the initial owner '{to_edit}' of store '{self.store.name}'")
                return Result(False, 0, "cannot edit permission of an initial owner or system manager",
                              None)
            # if appoint_new_store_owner:
            #     return Result(False, 0, "manager cannot appoint new owners", None)
            else:
                perm_to_edit.appoint_new_store_owner = False
            # else:
            #     perm_to_edit: Permission = self.owners_appointed[to_edit]
            #     self._dal.add(perm_to_edit, add_only=True)

            perm_to_edit.can_manage_inventory = can_manage_inventory
            perm_to_edit.appoint_new_store_manager = appoint_new_store_manager
            perm_to_edit.watch_purchase_history = watch_purchase_history
            perm_to_edit.open_and_close_store = open_and_close_store
            perm_to_edit.can_manage_discount = can_manage_discount
            res = self._dal.add(perm_to_edit, add_only=True)
            if res:
                perm_to_edit = res
            res = self._dal.add(perm_to_edit.user, add_only=True)
            if res:
                perm_to_edit._user = res
            return Result(True, 0, "permissions edited successfully", perm_to_edit.user)

    def add_product_to_store(self, product_name: str, base_price: float, quantity: int, brand: str,
                             categories: TypedList = None, description: str = ""):
        """
        adding new product to the store inventory if possible
        :param product_name: (str) name of the product to add
        :param base_price:(float) base price of that product for a single unit
        :param quantity: (int) quantity of that product to add to inventory
        :param brand:(str) name of the brand of that product
        :param categories:(TypedList of str) all categories that product belong to
        :param description(str) description of the product
        :return: Result with info o process
        """
        if self.can_manage_inventory:
            self._dal.add(self.store)
            if self.store.add_product(product_name, base_price, quantity, brand,
                                      categories, description):
                return Result(True, -1, "Product added successfully", None)
            else:
                return Result(False, -1, "somthing went wrong", None)
        else:
            return Result(False, -1, "don't have permission for such action", None)

    def remove_product(self, product_name: str):
        """
        remove product from store inventory if possible
        :param product_name: (str) name of the product to remove
        :return: Result with info on the process
        """
        if self.can_manage_inventory:
            if self.store.remove_product_from_store(product_name):
                return Result(True, -1, "product was removed successfully", None)
            else:
                return Result(False, -1, "product does not exists in the store", None)
        else:
            return Result(False, -1, "don't have permission for such action", None)

    def edit_existing_product(self, product_name: str, brand: str, new_price: float, quantity: int,
                              categories: TypedList = None,
                              description: str = ""):
        """
        edit details of product that is in store
        :param product_name:(str) name of the product to edit
        :param brand:(str) name of the new brand to edit
        :param new_price:(float) new base price for the product
        :param categories:(list of str) list of new categories to edit by
        :param description: (str) new description of the product
        :return: Result with success, or with fail info
        """
        if quantity < 0:
            return Result(False, -1, "quantity must be positive", None)
        if new_price < 0:
            return Result(False, -1, "price must be positive", None)
        if self.can_manage_inventory:
            self._dal.add(self.store, add_only=True)
            if quantity == 0:
                return self.remove_product(product_name)
            elif self.store.edit_product_in_store(product_name, brand, new_price, quantity,
                                                  categories, description):
                return Result(True, -1, "edited product successfully", None)
            else:
                return Result(False, -1, "product was not found in store", None)
        else:
            return Result(False, -1, "don't have permission for such action", None)

    def _to_open_or_close_store(self, to_open: bool):
        """
        opening or closing store if possible
        :param to_open: True if need to open store, False otherwise
        :return: Result with process info
        """
        if self.open_and_close_store:
            self._dal.add(self.store, add_only=True)
            res: bool = self.store.open_store() if to_open else self.store.close_store()
            if res:
                self._dal.add(self._store)
                return Result(True, -1, f"Store {'opened' if to_open else 'closed'} successfully", None)
            else:
                log: Log = Log.get_instance()
                log.get_logger().error(
                    f"ERROR IN '_to_open_or_close_store' in Permission class: User was trying to {'open' if to_open else 'close'} the store '{self.store.name}' and didn't manage to do so, even though he had the permission ")

                return Result(False, -1, "Something went wrong", None)
        else:
            return Result(False, -1, "Permission denied", None)

    def add_policy(self, min_basket_quantity: int, max_basket_quantity: int, product_name: str,
                   min_product_quantity: int,
                   max_product_quantity: int, category: str, min_category_quantity: int,
                   max_category_quantity: int, day: str, policy_id: int = -1):
        if self.can_manage_discount:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.add_policy(min_basket_quantity, max_basket_quantity, product_name,
                                                min_product_quantity, max_product_quantity, category,
                                                min_category_quantity, max_category_quantity, day, policy_id)
            if res.succeed:
                return Result(True, -1, "add policy successfully", res.data)
            else:
                log: Log = Log.get_instance()
                log.get_logger().error(
                    f"ERROR IN 'add_policy' in Permission class: User {-1} was trying to "
                    f"add policy to the store '{self.store.name}' and didn't manage to do so, even though he had the "
                    "permission ")
                return Result(False, -1, "Something went wrong", None)
        else:
            return Result(False, -1, "Permission denied", None)

    def remove_policy(self, to_remove: int):
        if self.can_manage_discount:
            self._dal.add(self.store, add_only=True)
            return self.store.remove_policy_from_store(to_remove)
            # if policy is not None:
            #     return Result(True, -1, "remove policy successfully", None)
            # else:
            #     log: Log = Log.get_instance()
            #     log.get_logger().error(
            #         f"ERROR IN 'remove_policy' in Permission class: User {-1} was trying to "
            #         f"remove policy from the store '{self.store.name}' and didn't manage to do so, even though he had "
            #         f"the permission ")
            #     return Result(False, -1, "Something went wrong", None)
        else:
            return Result(False, -1, "Permission denied", None)

    def combine_policies(self, policies_id_list: list, operator: str):
        if self.can_manage_discount:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.combine_policies(policies_id_list, operator)
            if res.succeed:
                return Result(True, -1, "combine policies successfully", None)
            else:
                log: Log = Log.get_instance()
                log.get_logger().error(
                    f"ERROR IN 'combine_policies' in Permission class: User {-1} was trying to "
                    f"combine policies to the store '{self.store.name}' and didn't manage to do so, even though "
                    f"he had the permission ")
                return Result(False, -1, "Something went wrong", None)
        else:
            return Result(False, -1, "Permission denied", None)

    def fetch_policies(self):
        if self.can_manage_discount:
            self._dal.add(self.store, add_only=True)
            res: Result = self.store.fetch_shopping_policies()
            if res.succeed:
                return Result(True, -1, "fetch policies successfully", res.data)
            else:
                log: Log = Log.get_instance()
                log.get_logger().error(
                    f"ERROR IN 'fetch_policies' in Permission class: User {-1} was trying to "
                    f"fetch policies to the store '{self.store.name}' and didn't manage to do so, even though "
                    f"he had the permission ")
                return Result(False, -1, "Something went wrong", None)
        else:
            return Result(False, -1, "Permission denied", None)

    def open_store(self):
        """
        open this store if have permission
        :return: Result with process info
        """
        return self._to_open_or_close_store(to_open=True)

    def close_store(self):
        """
        close this store if have permission
        :return: Result with process info
        """
        return self._to_open_or_close_store(to_open=False)

    def remove_all_sub_members(self, admin: User):
        """
        removing all permissions of this user to the store it managing
        :param admin: User who is also admin
        :return: True if successful, False otherwise
        """
        if admin.is_admin():
            for manager in self.managers_appointed:
                self.remove_manager(manager)
            for owner in self.owners_appointed:
                self.remove_owner(owner)
            return True
        else:
            return False

    def get_all_sub_permissions(self, direct_staff_only=True):
        """
        returns all the sub staff the user with the store
        :param direct_staff_only: (bool) flag represents whether to get also sub-sub managers and owners or not
        :return:
        """
        if self.role == Role.system_manager or self.role == Role.store_initial_owner:
            # those roles can edit anyone in the store
            self._dal.add(self.store, add_only=True)
            return self.store.get_permissions()
        elif direct_staff_only:
            all_sub_staff: TypedDict = TypedDict(str, Permission)
            for name, perm in self.managers_appointed.items():
                self._dal.add(perm, add_only=True)
                all_sub_staff[name] = perm
            for name, perm in self.owners_appointed.items():
                self._dal.add(perm, add_only=True)
                all_sub_staff[name] = perm
            return all_sub_staff
        else:
            # todo -> add recursive requirement here
            return self.get_all_sub_permissions(True)
