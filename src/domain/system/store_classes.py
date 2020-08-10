from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from sqlalchemy import orm

from src.communication.notification_handler import StatManager, Category
from src.domain.system.discounts import CompositeOrDiscount, _IDiscount, _IDiscountCondition, _IDiscountStrategy, \
    ComplexDiscount, DiscountConditionCombo, ProductDiscountStrategy, CategoryDiscountStrategy, \
    FreePerXProductDiscountStrategy, FreePerXCategoryDiscountStrategy, BasketDiscountStrategy
from src.domain.system.shopping_policies import CompositeAndShoppingPolicy, IShoppingPolicies, ICompositePolicy
from src.domain.system.shopping_policies import LeafProductPolicy, LeafBasketQuantity
from src.domain.system.store_managers_classes import AppointmentAgreement
from src.external.publisher import Publisher
from src.logger.log import Log

if TYPE_CHECKING:
    from src.domain.system.users_classes import User
    from src.domain.system.permission_classes import Permission, get_category, Role
    from src.domain.system.cart_purchase_classes import Basket, ProductInShoppingCart

from src.domain.system.cart_purchase_classes import Purchase
from src.domain.system.products_classes import Product, ProductInInventory, PermissionDenied

from src.protocol_classes.classes_utils import TypedList, Result

import src.domain.system.products_classes as pc
from datetime import datetime

from src.domain.system.DAL import DAL
from src.protocol_classes.classes_utils import TypeChecker, TypedDict

from src.domain.system.db_config import db
import json


class Store(db.Model):
    __tablename__ = 'store'
    _dal: DAL = DAL.get_instance()
    _name = db.Column(db.String(50), primary_key=True)
    _initial_owner_fk = db.Column(db.String(50), db.ForeignKey('loggedInUsers._user_name'))
    _initial_owner = db.relationship("LoggedInUser", lazy="select")  # TODO1
    _opened = db.Column(db.Boolean)
    _creation_date = db.Column(db.DateTime)

    _inventory_ls = db.relationship("ProductInInventory", lazy="select",
                                    foreign_keys=[pc.ProductInInventory._store_fk])
    _purchases_ls = db.Column(db.JSON)  # db.relationship("Purchase", lazy="select")
    _permissions_ls = db.Column(db.JSON)  # db.relationship("Permission", lazy="select")
    _pending_ownership_proposes_ls = db.relationship("AppointmentAgreement", lazy="subquery")  # WAS subquery,#TODO1
    _discount_fk = db.Column(db.Integer, db.ForeignKey("complex_discount.id"))
    _discount = db.relationship("ComplexDiscount", lazy="joined")
    _shopping_policies_fk = db.Column(db.Integer, db.ForeignKey("i_composite_policy.id"))
    _shopping_policies = db.relationship("ICompositePolicy", lazy="joined")

    def __init__(self, name: str, initial_owner: str, opened: bool = True,
                 creation_date: datetime = datetime.now(),
                 inventory: TypedDict = None, purchases: TypedList = None, initial_owner_obj=None):
        from src.domain.system.permission_classes import Permission
        if inventory is None:
            inventory = TypedDict(str, ProductInInventory)
        if purchases is None:
            purchases = TypedList(Purchase)
        self._inventory_ls = []
        self._permissions_ls = json.dumps([])
        self._purchases_ls = json.dumps([])
        self._pending_ownership_proposes_ls = []
        self.name: str = name
        self._owner_init = False
        self._initial_owner_fk = initial_owner
        self._initial_owner = initial_owner_obj
        self._owner_init = True
        self.open = opened
        self.creation_date: datetime = creation_date
        self.inventory = inventory
        self._inventory_lock = threading.Lock()
        self.purchases = purchases
        self._permissions = TypedDict(str, Permission)
        self._discount = CompositeOrDiscount(_IDiscountCondition(datetime.now()), _IDiscountStrategy())
        self._shopping_policies = CompositeAndShoppingPolicy()
        self._pending_ownership_proposes = TypedDict(str, AppointmentAgreement)

    @orm.reconstructor
    def loaded(self):
        from src.domain.system.permission_classes import Permission
        self._inventory = TypedDict(str, ProductInInventory)
        self._inventory_lock = threading.Lock()

        for p in self._inventory_ls:
            self._inventory[p.product_name] = p

        self._permissions = self._dal.get_permission_with_id_keys_for_store(json.loads(self._permissions_ls),
                                                                            self._name)
        self._dal.add_all(list(self._permissions.values()), add_only=True)
        # self._dal.add_all(self._permissions_ls, add_only=True)
        # for perm in self._permissions_ls:
        #     self._permissions[perm.user.user_name] = perm

        self._purchases = self._dal.get_purchases_with_id_keys_for_store(json.loads(self._purchases_ls))

        self._pending_ownership_proposes = TypedDict(str, AppointmentAgreement)
        for prop in self._pending_ownership_proposes_ls:
            self._dal.add(prop, add_only=True)
            self._pending_ownership_proposes[prop._candidate_fk] = prop
        # self._dal.add(self._initial_owner, add_only=True)

    def add_appointement_agreement(self, ag: AppointmentAgreement):
        self._pending_ownership_proposes_ls.append(ag)
        self._pending_ownership_proposes[ag._candidate_fk] = ag

    @property
    def purchases(self):
        return self._purchases

    @purchases.setter
    def purchases(self, new_purchases: TypedList):
        if isinstance(new_purchases, TypedList) and new_purchases.check_types(Purchase):
            self._purchases = new_purchases

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        if type(new_name) == str and new_name.strip() != "":
            self._name = new_name
        else:
            raise TypeError("not a valid name(suppose to be str)")

    @property
    def initial_owner_name(self):
        return self._initial_owner_fk

    @property
    def initial_owner(self):
        return self._initial_owner

    @initial_owner.setter
    def initial_owner(self, owner: str):
        if not self._owner_init:
            if isinstance(owner, str):
                self._initial_owner = owner
            else:
                raise TypeError("owner should be of type User")
        else:
            raise PermissionDenied("not should not be able to change initial Owner")

    @property
    def discount_root(self):
        return self._discount

    @property
    def shopping_policies(self):
        return self._shopping_policies

    @property
    def open(self):
        return self._opened

    @open.setter
    def open(self, is_open: bool):
        if type(is_open) == bool:
            self._opened = is_open
        else:
            raise TypeError("not a valid is_open (supposed to be bool)")

    @property
    def inventory(self):
        return self._inventory

    @inventory.setter
    def inventory(self, inv: TypedDict):
        if isinstance(inv, TypedDict) and inv.check_types(str, ProductInInventory):
            self._inventory = inv
        else:
            raise TypeError("not a valid inventory")

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self, new_date: datetime):
        if type(new_date) == datetime:
            self._creation_date = new_date
        else:
            raise TypeError("not a valid date")

    def __eq__(self, other):
        if isinstance(other, Store):
            return self._name == other._name
        else:
            return False

    def copy(self):
        """
        create a new Store Object with the same properties as this one
        :return: Store Object copy
        """
        return Store(self.name, self.initial_owner, self.open, self.creation_date,
                     self.inventory, self.purchases)

    def get_permissions(self):
        return self._permissions

    def to_dictionary(self, with_permissions=False):
        self.loaded()
        temp = []
        for key, product in self.inventory.items():
            temp.append(product.to_dictionary())
        return {
            "name": self.name,
            "initial_owner": self._initial_owner_fk,
            "open": self.open,
            "creation_date": str(self.creation_date),
            "inventory": temp,
            "permissions": self.get_permissions() if with_permissions else dict()
        }

    def add_purchases(self, purchases: TypedList):
        """
        adding new purchase to the store purchase history
        :param purchases: (TypedList of Purchase) list of purchases that was made in the store.
        :return: None
        """
        if not isinstance(purchases, TypedList) or not purchases.check_types(Purchase):
            raise TypeError(f"expected Purchase got {type(purchases)}")
        else:
            for purchase in purchases:
                num_items: int = len(purchase.basket.products)
                for perm in self._permissions.values():
                    self._dal.add(perm, add_only=True)
                    if num_items == 1:
                        msg = f"One item was purchased from store {self.name}. Purchase ID: {purchase.purchase_id}"
                    else:
                        msg = f"{str(num_items)} items were purchased from store {self.name}. Purchase ID: {purchase.purchase_id}"
                    Publisher.get_instance().publish('store_update', f"Date: {datetime.today()}: {msg}", perm._user_fk)
            # self._purchases_ls.append(purchases)
            temp = json.loads(self._purchases_ls)
            for purchase in purchases:
                self._dal.add(purchase, add_only=True)
                temp.append(purchase.purchase_id)
            self._purchases_ls = json.dumps(temp)
            self.purchases.extend(purchases)

    def watch_purchase_history(self, requesting_user: User):
        """
        view all purchases that was done in this store, if possible
        :param requesting_user: (User) the user who request to see the purchases
        :return: List of all purchases done in the store. None if don't have the right permission
        """
        if requesting_user.user_state is None:
            return Result(False, requesting_user.user_id, "Must be Registered User for this kind of action", None)
        elif not requesting_user.user_state.is_connected:
            return Result(False, requesting_user.user_id, "Must be logged in for such action", None)
        if requesting_user.is_admin():
            return Result(True, requesting_user.user_id, "Purchases result in data field",
                          [p.to_dictionary() for p in self.purchases])

        if self._is_permitted_to_watch_history(requesting_user):
            return Result(True, requesting_user.user_id, "Purchases result in data field",
                          [p.to_dictionary() for p in self.purchases])
        else:
            return Result(False, requesting_user.user_id, "Don't have permission for such action", None)

    def open_store(self):
        self._opened = True
        return True

    def close_store(self):
        self._opened = False
        return True

    def add_store_member(self, perm: Permission):
        from src.domain.system.users_classes import User
        if perm._user_fk in self._permissions:
            return Result(False, -1, "User is Already in store management", None)
        else:
            self._permissions[perm._user_fk] = perm
            temp = json.loads(self._permissions_ls)
            temp.append(perm._user_fk)
            self._permissions_ls = json.dumps(temp)
            return Result(True, -1, "User added successfully to management of the store", None)

    def fetch_all_discounts(self):
        all_discounts = self.get_all_discounts()
        data = [{"discount_id": dis.id, "description": dis.get_description()} for dis in all_discounts]
        return Result(True, -1, "all discounts:", data)

    def get_all_discounts(self):
        """
        :return: list of all discounts in the store. build from id an description
        """
        # return self._dal.get_discounts_by_store_name(self.name)
        return self.discount_root.get_all_discounts()

    def remove_member(self, to_remove: list):
        """
        The function remove a store management member from the store
        :param to_remove:(str) name of the user to remove
        :return : None
        """
        # removed_permission: Permission = self._permissions[to_remove]
        # self._dal.add(removed_permission, add_only=True)
        for name in to_remove:
            if name in self._permissions:
                del self._permissions[name]
                msg: str = f"{name} was removed from staff of store: {self.name}"
                Publisher.get_instance().publish('store_update', f"Date: {datetime.today()}: {msg}", name)
        return True

    def get_copy_of_product(self, product_name: str, quantity: int = None):
        """
        return copy of a wanted product with a given quantity
        :param product_name: (str) name of the wanted product
        :param quantity: (int) wanted quantity of the product
        :return: ProductInInventory duplicate of what's in the inventory, with the given quantity. if product does not exists, return None
        """
        if type(product_name) != str and quantity is not None and TypeChecker.check_for_positive_ints([quantity]):
            raise TypeError(f'expected a string and positive int, got {type(product_name)}, {type(quantity)}')
        if product_name not in self.inventory:
            return None  # product does not exists
        else:
            current: ProductInInventory = self.inventory[product_name]
            if quantity is None:
                quantity = current.quantity
            if current.quantity >= quantity:
                output: ProductInInventory = current
                # output.quantity = quantity
                return output
            else:
                return False  # not enough in inventory

    def add_simple_product_discount(self, end_time: datetime, discount_percent: float, discounted_product: str,
                                    size_of_basket_cond: int = None,
                                    over_all_price_category_cond: list = None,
                                    over_all_price_product_cond: list = None, product_list_cond: list = None,
                                    overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding simple product discount, according to given conditions
        :param end_time: the expiration date of the discount
        :param discount_percent: the discount percent to deduce from the price of the product
        :param discounted_product: name of the product to give discount to
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :param discount_id: (int) id of discount to edit. if negative -> adding a new discount
        :return: Result with info on process
        """
        self._dal.begin_nested()
        try:
            discount_condition: _IDiscountCondition = DiscountConditionCombo.create_combo_condition(end_time,
                                                                                                    size_of_basket_cond,
                                                                                                    over_all_price_category_cond,
                                                                                                    over_all_price_product_cond,
                                                                                                    product_list_cond,
                                                                                                    overall_category_quantity)
            discount_strategy: _IDiscountStrategy = ProductDiscountStrategy.create_product_discount_strategy(
                discount_percent, discounted_product)
            new_discount: _IDiscount = _IDiscount(discount_condition, discount_strategy)

            if discount_id < 0:
                r = self.add_simple_discount_to_store(new_discount)
                self._dal.commit()
                return r
            else:
                r = self._replace_discount(discount_id, new_discount)
                self._dal.commit()
                return r
        except Exception as e:
            self._dal.rollback()
            return Result(False, -1, f"Add simple discount failed, Rollback performed({str(e)})", None)

    def add_free_per_x_product_discount_discount(self, end_time: datetime, product_name: str, free_amount: int,
                                                 per_x_amount: int, is_duplicate: bool = True,
                                                 size_of_basket_cond: int = None,
                                                 over_all_price_category_cond: list = None,
                                                 over_all_price_product_cond: list = None,
                                                 product_list_cond: list = None,
                                                 overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding Free Per X kind of discount on a given product
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
        :param discount_id: (int) id of discount to edit. if negative -> adding a new discount
        :return: Result with info on process
        """
        self._dal.begin_nested()
        try:
            discount_condition: _IDiscountCondition = DiscountConditionCombo.create_combo_condition(end_time,
                                                                                                    size_of_basket_cond,
                                                                                                    over_all_price_category_cond,
                                                                                                    over_all_price_product_cond,
                                                                                                    product_list_cond,
                                                                                                    overall_category_quantity)
            discount_strategy: _IDiscountStrategy = FreePerXProductDiscountStrategy.create_free_per_x_product_discount_strategy(
                product_name, free_amount, per_x_amount, is_duplicate)
            new_discount: _IDiscount = _IDiscount(discount_condition, discount_strategy)

            if discount_id < 0:
                r = self.add_simple_discount_to_store(new_discount)
                self._dal.commit()
                return r
            else:
                r = self._replace_discount(discount_id, new_discount)
                self._dal.commit()
                return r
        except Exception as e:
            self._dal.rollback()
            return Result(False, -1, f"Add free per x product discount failed, Rollback performed({str(e)})", None)

    def add_simple_category_discount(self, end_time: datetime, discount_percent: float, discounted_category: str,
                                     size_of_basket_cond: int = None,
                                     over_all_price_category_cond: list = None,
                                     over_all_price_product_cond: list = None, product_list_cond: list = None,
                                     overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding simple category discount, according to given conditions
        :param end_time: the expiration date of the discount
        :param discount_percent: the discount percent to deduce from the price of the product
        :param discounted_category: name of the category to give discount to
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond:
        :param overall_category_quantity:
        :return: Result with info on process
        """
        self._dal.begin_nested()
        try:
            discount_condition: _IDiscountCondition = DiscountConditionCombo.create_combo_condition(end_time,
                                                                                                    size_of_basket_cond,
                                                                                                    over_all_price_category_cond,
                                                                                                    over_all_price_product_cond,
                                                                                                    product_list_cond,
                                                                                                    overall_category_quantity)
            discount_strategy: _IDiscountStrategy = CategoryDiscountStrategy.create_category_discount_strategy(
                discount_percent, discounted_category)
            new_discount: _IDiscount = _IDiscount(discount_condition, discount_strategy)

            if discount_id < 0:
                r = self.add_simple_discount_to_store(new_discount)
                self._dal.commit()
                return r
            else:
                r = self._replace_discount(discount_id, new_discount)
                self._dal.commit()
                return r
        except Exception as e:
            self._dal.rollback()
            return Result(False, -1, f"Add simple category discount failed, Rollback performed({str(e)})", None)

    def add_free_per_x_category_discount_discount(self, end_time: datetime, category_name: str, free_amount: int,
                                                  per_x_amount: int, is_duplicate: bool = True,
                                                  size_of_basket_cond: int = None,
                                                  over_all_price_category_cond: list = None,
                                                  over_all_price_product_cond: list = None,
                                                  product_list_cond: list = None,
                                                  overall_category_quantity: list = None, discount_id: int = -1):
        """
        adding Free Per X kind of discount on a given category
        :param end_time: (datetime) the expiration date of the discount
        :param category_name: name of the category to do discount on
        :param free_amount: (int)number of items to get free on each x items you bought
        :param per_x_amount:(int) number of items to buy to get the free ones
        :param is_duplicate:(bool) is to perform this discount until there are no more of the given product, or just 1 time (default True)
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :return: Result with info on process
        """
        self._dal.begin_nested()
        try:
            discount_condition: _IDiscountCondition = DiscountConditionCombo.create_combo_condition(end_time,
                                                                                                    size_of_basket_cond,
                                                                                                    over_all_price_category_cond,
                                                                                                    over_all_price_product_cond,
                                                                                                    product_list_cond,
                                                                                                    overall_category_quantity)
            discount_strategy: _IDiscountStrategy = FreePerXCategoryDiscountStrategy.create_free_per_x_product_discount_strategy(
                category_name, free_amount, per_x_amount, is_duplicate)
            new_discount: _IDiscount = _IDiscount(discount_condition, discount_strategy)
            if discount_id < 0:
                r = self.add_simple_discount_to_store(new_discount)
                self._dal.commit()
                return r
            else:
                r = self._replace_discount(discount_id, new_discount)
                self._dal.commit()
                return r
        except Exception as e:
            self._dal.rollback()
            return Result(False, -1, f"Add free per x category discount failed, Rollback performed({str(e)})", None)

    def add_discount_on_entire_store(self, end_time: datetime, discount_percent: float, size_of_basket_cond: int = None,
                                     over_all_price_category_cond: list = None,
                                     over_all_price_product_cond: list = None, product_list_cond: list = None,
                                     overall_category_quantity: list = None, discount_id: int = -1):

        """
        add store discount to store
        :param end_time: (datetime) the expiration date of the discount
        :param discount_percent: percent to add to the entire store
        :param size_of_basket_cond: optional condition on the minimum size of the baskets
        :param over_all_price_category_cond: optional condition on the price payed on certain categories
        :param over_all_price_product_cond: optional condition on the price
        :param product_list_cond: optional condition on minimum quantity of each given product in the list
        :param overall_category_quantity: optional condition on amount of products in each category
        :return: Result with info on process
        """

        try:

            discount_condition: _IDiscountCondition = DiscountConditionCombo.create_combo_condition(end_time,
                                                                                                    size_of_basket_cond,
                                                                                                    over_all_price_category_cond,
                                                                                                    over_all_price_product_cond,
                                                                                                    product_list_cond,
                                                                                                    overall_category_quantity)
            discount_strategy: _IDiscountStrategy = BasketDiscountStrategy.create_basket_discount_strategy(
                discount_percent)
            new_discount: _IDiscount = _IDiscount(discount_condition, discount_strategy)
            if discount_id < 0:
                res: Result = self.add_complex_discount_to_store(new_discount)
                if res.succeed:
                    for k, product in self.inventory.items():
                        product.discounts[new_discount.id] = new_discount
                return res
            else:
                return self._replace_discount(discount_id, new_discount)

        except Exception as e:
            return Result(False, -1, f"Add discount on entire store failed, Rollback performed({str(e)})", None)

    def add_simple_discount_to_store(self, new_discount: _IDiscount):
        """
        :param new_discount: (_IDiscount) new discount to add
        :return: id of new Discount
        """
        self._dal.add(new_discount, add_only=True)
        self._dal.flush()  # So we ill able to call .id
        self.discount_root.add_discount(new_discount)

        relevant_products, relevant_categories = new_discount.relevant_products_and_categories()
        all_relevant_products_by_name = [k for k, p in self.inventory.items() if k in relevant_products]
        for category in relevant_categories:
            relevant_products_by_category = [k for k, p in self.inventory.items() if
                                             category in p.product.categories]
            all_relevant_products_by_name = all_relevant_products_by_name + relevant_products_by_category
        all_relevant_products_by_name = list(dict.fromkeys(all_relevant_products_by_name))  # removing duplicates
        to_update = []
        for product_name in all_relevant_products_by_name:
            if product_name in self.inventory:
                p: ProductInInventory = self.inventory[product_name]
                p.add_discount(new_discount)
                to_update.append(p)
        self._dal.add_all(to_update, add_only=True)

        return Result(True, -1, "given discount was added successfully", new_discount.id)

    def add_complex_discount_to_store(self, new_discount: _IDiscount):
        """
        :param new_discount: (_IDiscount) new discount to add
        :return: id of new Discount
        """
        self._dal.add(new_discount, add_only=True)
        self._dal.flush()  # So we ill able to call .id
        self.discount_root.add_discount(new_discount)

        return Result(True, -1, "given discount was added successfully", new_discount.id)

    def _removing_discount_from_products(self, to_remove: _IDiscount):
        """
        removing the given discounts from all the relavent products
        :param to_remove: discounts to remove
        :return: None
        """

        all_relevant_products = [p for k, p in self.inventory.items() if to_remove.id in p.discounts]
        for p in all_relevant_products:
            p: ProductInInventory = p
            del p.discounts[to_remove.id]
        self._dal.add_all(all_relevant_products)

    def remove_discount_from_store(self, to_remove: int):
        """
        removing discount if possible
        :param to_remove:(id) id of discount to remove
        :return: Result with info on process
        """
        # Begin transaction here
        self._dal.begin_nested()  # Init transaction
        try:
            output = self.discount_root.remove_discount(to_remove)
            if output is None:
                self._dal.rollback()
                return Result(False, -1, "Discount was not found", None)
            else:
                self.remove_discount_from_product(to_remove, output)
                self._dal.commit()  # Commit transaction
                return Result(True, -1, "Removed successfully", output)
        except Exception as e:
            self._dal.rollback()  # Rollback transaction
            return Result(False, -1,
                          f"Failed to remove discount from Store({self._name}), Rollback performed({str(e)})", None)

    def combine_discounts(self, discounts_id_list: list, operator: str, basic_condition: _IDiscountCondition = None,
                          basic_strategy: _IDiscountStrategy = None):
        # Begin transaction here
        self._dal.begin_nested()  # Init transaction
        try:
            children_discounts = []
            for id in discounts_id_list:
                current_discount: _IDiscount = self.discount_root.remove_discount(id)
                if current_discount is None:
                    self._dal.rollback()
                    return Result(False, -1, f"given discount id {id} was not found in store", None)
                children_discounts.append(current_discount)
            combined_discount: _IDiscount = ComplexDiscount.combine_discounts(children_discounts, operator,
                                                                              basic_condition,
                                                                              basic_strategy)
            ret = self.add_complex_discount_to_store(combined_discount)
            self._dal.commit()
            return ret
        except Exception as e:
            self._dal.rollback()  # Rollback transaction
            return Result(False, -1,
                          f"Failed to combine discounts for Store({self._name}), Rollback performed({str(e)})", None)

    def _replace_discount(self, discount_id: int, edited_discount: _IDiscount):
        """
         replacing the discount with the given id with this one
        :param discount_id: (int) id of the discount
        :param edited_discount: new discount to replace
        :return: The edited discount. if was not found -> return None
        """
        self._dal.add(edited_discount, add_only=True)
        self._dal.flush()  # So we ill able to call .id
        dis_tuple = self.discount_root.edit_discount(discount_id, edited_discount)
        if dis_tuple is None:
            self._dal.delete(edited_discount, del_only=True)
            return Result(False, -1, "Didn't found discount to edit", None)
        else:
            edited, removed = dis_tuple
            self._dal.add(edited, add_only=True)
            self._dal.flush()  # So we ill able to call .id
            self.remove_discount_from_product(discount_id, removed)
            return Result(True, -1, "discount was edited", edited.id)

    def remove_discount_from_product(self, discount_id, removed):
        all_ids = [dis.id for dis in removed.get_all_discounts()]
        all_ids.append(discount_id)
        to_update = []
        for i in all_ids:
            all_relevant_products = [p for k, p in self.inventory.items() if i in p._discounts]
            for p in all_relevant_products:
                p: ProductInInventory = p
                p.clear_discounts()
                self._checking_for_discount_for_product(p)
                to_update.append(p)
        removed.delete_from_db()
        self._dal.add_all(to_update, add_only=True)

    def _edit_existing_policy(self, children, policy_id):
        self._dal.add(children)
        pol_tuple = self.shopping_policies.edit_policy(policy_id, children)
        if pol_tuple is None:
            self._dal.delete(children)
            return Result(False, -1, "Didn't found discount to edit", None)
        else:
            edited, removed = pol_tuple
            self._dal.add(edited)
            self.remove_policy_from_productsss(policy_id, removed)

        return Result(True, -1, "policy was edited", edited.id)

    def remove_policy_from_productsss(self, policy_id, removed):
        all_ids = [pol.id for pol in removed.fetch_policies()]
        all_ids.append(policy_id)
        to_update = []
        for i in all_ids:
            all_relevant_products = [p for k, p in self.inventory.items() if i in p._policies]
            for p in all_relevant_products:
                p: ProductInInventory = p
                p.clear_policies()
                self._checking_for_policies_for_product(p)
                if p not in to_update:
                    to_update.append(p)
        removed.delete_yourself()
        self._dal.add_all(to_update, add_only=True)

    def add_policy(self, min_basket_quantity: int, max_basket_quantity: int, product_name: str,
                   min_product_quantity: int,
                   max_product_quantity: int, category: str, min_category_quantity: int,
                   max_category_quantity: int, day: str, policy_id: int = -1):

        # Begin transaction here
        self._dal.begin_nested()  # Init transaction
        try:
            children = IShoppingPolicies.create_specific_leaf(min_basket_quantity, max_basket_quantity, product_name,
                                                              min_product_quantity, max_product_quantity, category,
                                                              min_category_quantity, max_category_quantity, day)
            if policy_id > 0:
                r = self._edit_existing_policy(children, policy_id)
                self._dal.commit()  # Commit transaction
                return r
            else:
                self._dal.add(children, add_only=True)
                self._dal.flush()  # So we ill able to call .id
                res: Result = self._add_new_policy(children)
                self._dal.commit()  # Commit transaction
                return Result(res.succeed, res.requesting_id, res.msg, children.id)
        except Exception as e:
            self._dal.rollback()  # Rollback transaction
            return Result(False, -1,
                          f"Failed to remove policy from Store({self._name}), Rollback performed({str(e)})", None)

    def _add_new_policy(self, children):
        self.shopping_policies.add_policy(children)
        to_update = []
        policy: LeafProductPolicy = children
        # this specific policy is relevant for all products
        if isinstance(policy, LeafBasketQuantity):
            for k, p in self.inventory.items():
                product: ProductInInventory = self.inventory[k]
                product.add_policy(policy)
                to_update.append(p)
        else:
            rel_categories, rel_products = policy.relevant_categories_and_products()
            all_relevant_products_by_name = [k for k, p in self.inventory.items() if k in rel_products]
            for category in rel_categories:
                relevant_products_by_category = [k for k, p in self.inventory.items() if
                                                 category in p.product.categories]
                all_relevant_products_by_name = all_relevant_products_by_name + relevant_products_by_category
            all_relevant_products_by_name = list(
                dict.fromkeys(all_relevant_products_by_name))  # removing duplicates
            for product_name in all_relevant_products_by_name:
                if product_name in self.inventory:
                    p: ProductInInventory = self.inventory[product_name]
                    p.add_policy(policy)
                    to_update.append(p)
        self._dal.add_all(to_update, add_only=True)
        return Result(True, -1, "given shopping policy was added successfully", children.id)

    def remove_policies_from_products(self, to_remove: IShoppingPolicies):
        rel_products = [p for k, p in self.inventory.items() if to_remove.id in p.policies]
        for p in rel_products:
            p: ProductInInventory = p
            p.remove_policy(p)
        self._dal.add_all(rel_products)

    def remove_policy_from_store(self, to_remove: int):
        # Begin transaction here
        self._dal.begin_nested()  # Init transaction
        try:
            ret_val: IShoppingPolicies = self._shopping_policies.remove_policy(to_remove)
            if ret_val is None:
                self._dal.rollback()
                return Result(False, -1, "Policy was not found", None)
            else:
                self.remove_policy_from_productsss(to_remove, ret_val)
                self._dal.commit()  # Commit transaction
                return Result(True, -1, "Removed successfully", ret_val)
        except Exception as e:
            self._dal.rollback()  # Rollback transaction
            return Result(False, -1,
                          f"Failed to remove policy from Store({self._name}), Rollback performed({str(e)})", None)

    def combine_policies(self, policies_id_list: list, operator: str):
        # Begin transaction here
        self._dal.begin_nested()  # Init transaction
        try:
            children_policies = []
            for policy_id in policies_id_list:
                current_policy = self._shopping_policies.remove_policy(policy_id)
                if current_policy is None:
                    self._dal.rollback()
                    return Result(False, -1, f"given policy id {policy_id} was not found in store", None)
                children_policies.append(current_policy)
            combined_policies: ICompositePolicy = ICompositePolicy.create_composite_policies(children_policies,
                                                                                             operator)
            self._dal.add(combined_policies)
            self._shopping_policies.add_policy(combined_policies)
            ret = Result(True, -1, "Composed", None)
            self._dal.commit()
            return ret
        except Exception as e:
            self._dal.rollback()  # Rollback transaction
            return Result(False, -1,
                          f"Failed to remove policy from Store({self._name}), Rollback performed({str(e)})", None)

    def fetch_shopping_policies(self):
        policies = self.shopping_policies.fetch_policies()
        data = [{"policy_id": p.id, "description": p.description()} for p in policies]
        return Result(True, -1, "fetch policies succeeded", data)

    def add_product(self, product_name: str, base_price: float,
                    quantity: int, brand: str = "", categories: TypedList = None, description: str = ""):
        """
        adding a new product if possible to the store
        :param username:(str) name of the user who is adding product to the inventory
        :param product_name:(str) name of the product
        :param base_price: (float) base price of the product
        :param quantity:(int) amount of items from the product
        :param brand:(str) brand of the product
        :param categories:(TypedList of str) categories of the product
        :param description(str) description of the product
        :return: True if successful, Raise Exceptions otherwise
        """
        # if username in self._permissions:
        #     perm: Permission = self._permissions[username]
        #     if perm.can_manage_inventory:
        base_product: Product = Product(product_name, brand=brand, categories=categories, description=description)
        new_product: ProductInInventory = ProductInInventory(base_product, price=base_price, quantity=quantity,
                                                             store_name=self.name, store_obj=self)
        new_product._store = self

        return self._adding_product(new_product)

    def _checking_for_discount_for_product(self, product: ProductInInventory):
        """
        adding all the relevant discount to the product
        :param product: product to check discounts for
        :return: None
        """
        all_relevant_discounts = self.discount_root.is_product_affected_by_discount(product.product.name,
                                                                                    product.product.categories)
        if all_relevant_discounts is not None:
            for discount in all_relevant_discounts:
                discount: _IDiscount = discount
                product.add_discount(discount)

    def _checking_for_policies_for_product(self, product: ProductInInventory):
        """
        adding all the relevant policies to the product
        :param product: product to check policies for
        :return:
        """
        if len(self.shopping_policies.shop_policies_dict) > 0:
            related_policies = self.shopping_policies.is_product_has_shopping_policies(product.product.name,
                                                                                       product.product.categories)
            if related_policies is not None:
                for policy in related_policies:
                    policy: IShoppingPolicies = policy
                    product.add_policy(policy)

    def _adding_product(self, new_product: ProductInInventory):
        if new_product.product.name in self.inventory:
            # if exists -> adding quantity
            existing_product: ProductInInventory = self.inventory[new_product.product.name]
            existing_product.quantity = existing_product.quantity + new_product.quantity
            self.inventory[new_product.product.name] = existing_product

            self._dal.add_all([existing_product, self])
            return True
        elif new_product.quantity == 0:
            # dont add to inventory item with 0 quantity
            return True
        else:
            # adding discounts to product
            self._dal.add(new_product)
            self._checking_for_discount_for_product(new_product)
            self._checking_for_policies_for_product(new_product)
            self._inventory_ls.append(new_product)
            self.inventory[new_product.product.name] = new_product

            self._dal.add_all([self, new_product])
            return True

    def apply_discount_on_basket(self, basket: Basket):
        """
        applying discount policy of the store on the given basket
        :param basket: (Basket) basket of user to check if there are some valid discount the store can deduce from it
        :return: deduced basket price, according to the
        """
        self.discount_root.reset_flags()
        return self.discount_root.apply(basket)

    def apply_policies_on_basket(self, basket: Basket):
        """
                applying discount policy of the store on the given basket
                :param basket: (Basket) basket of user to check if there are some valid discount the store can deduce from it
                :return: deduced basket price, according to the
                """
        return self.shopping_policies.apply(basket)

    def add_product_after_product_cancellation(self, product: ProductInShoppingCart):
        """
        adding a new product if possible to the store
        :param product: ProductInInventory to add back to store
        :return: True if successful, Raise Exceptions otherwise
        """
        item: ProductInInventory = product._item
        if item.product_name in self.inventory:
            # if exists -> adding quantity
            existing_product: ProductInInventory = self.inventory[item.product_name]
            existing_product.quantity = existing_product.quantity + product._product_quantity
            self.inventory[item.product_name] = existing_product
            # self._dal.add_all([existing_product, self])
            self._dal.update_quantity_of_item(existing_product.id, self._name, existing_product.quantity)
            self._dal.add(existing_product, add_only=True)
            self._dal.add(self, add_only=True)
            return True

        elif product._product_quantity == 0:
            # dont add to inventory item with 0 quantity
            return True
        else:
            # adding discounts to product
            self._dal.add(item)
            self._checking_for_discount_for_product(item)
            self._checking_for_policies_for_product(item)
            self._inventory_ls.append(item)
            self.inventory[item.product_name] = item

            self._dal.add_all([self, item])
            return True

    def pre_purchase_from_store(self, product_name: str, quantity_to_purchase: int):
        """
        removing items from inventory before purchasing
        :param product_name: (str) name of the product to buy
        :param quantity_to_purchase: (int) quantity to buy
        :return: int represent amount bought from store
        """
        if not (isinstance(product_name, str) and isinstance(quantity_to_purchase, int)) or quantity_to_purchase < 0:
            raise TypeError(" invalid arguments: expected str and positive int")
        elif quantity_to_purchase == 0:
            return 0
        if product_name not in self.inventory:
            return 0
        else:
            product: ProductInInventory = self.inventory[product_name]
            if product.quantity <= quantity_to_purchase:
                quantity_to_purchase = product.quantity
                product.quantity = 0
            else:
                product.quantity -= quantity_to_purchase
            # self._dal.add(product, add_only=True)
            self._dal.update_quantity_of_item(product.id, self._name, product.quantity)
            return quantity_to_purchase

    def clear_empty_products_from_inventory(self):
        to_delete_in_inventory = []
        to_delete_products = []
        for p_name in list(self.inventory.keys()):
            p: ProductInInventory = self.inventory[p_name]
            if p.quantity == 0:
                self.inventory.pop(p_name)
                self._inventory_ls.remove(p)
                to_delete_in_inventory.append(p.id)
                to_delete_products.append(p.id)

        self._dal.delete_all_products(to_delete_in_inventory, to_delete_in_inventory)

    def remove_product_from_store(self, product_name: str):
        """
        removing a product from store inventory
        :param requesting_user: (str) name of the requesting_user
        :param product_name: (str) name of the product
        :return: True if succeeded. raise exception otherwise
        """
        if type(product_name) != str or product_name.strip() == "":
            raise TypeError("expected non empty string")
            # if requesting_user in self._permissions:
            #     perm: Permission = self._permissions[requesting_user]
            #     if perm.can_manage_inventory:
        if product_name in self.inventory:
            with self._inventory_lock:
                popped: ProductInInventory = self.inventory.pop(product_name)
                self._dal.delete_all([popped, popped.product])
                self._dal.commit()
                return True
        else:
            return False  # product does'nt exists

    def edit_product_in_store(self, product_name: str, brand: str, new_price: float, quantity: int,
                              categories: list = None, description: str = ""):
        """
        edit details of product in store
        :param product_name: (str) product to edit
        :param brand: (str) new brand of the product
        :param new_price: (float) new base price for product
        :param categories: (TypedList of str) new categories
        :param description: (str) new description of the product
        :return: True if Succeeded, raise Exception otherwise
        """
        if categories is None:
            categories = []
            # if requesting_user in self._permissions:
            #     perm: Permission = self._permissions[requesting_user]
            #     if perm.can_manage_inventory:
        if product_name in self.inventory:
            product_to_edit: ProductInInventory = self.inventory[product_name]
            edited_product: Product = product_to_edit.product
            edited_product.name = product_name
            edited_product.brand = brand
            edited_product.categories = categories
            edited_product.description = description

            product_to_edit.product = edited_product
            product_to_edit.price = new_price
            product_to_edit.quantity = quantity
            # editing discounts again
            product_to_edit.clear_discounts()
            self._checking_for_discount_for_product(product_to_edit)
            self._dal.add_all([edited_product, product_to_edit])
            return True
        else:
            return False

    def _search_products(self, product_name: str = None, categories: list = None,
                         brands: list = None,
                         min_price: float = None,
                         max_price: float = None):
        """
        search all products that answer the conditions
        :param product_name: (str) name of the products
        :param categories: (list of str) names of categories the products need to belong to (at least on of them)
        :param brands: (list of str) names of brands the product need to have (at least one)
        :param min_price: (float) minimum price for the product
        :param max_price: (float) maximum price for the product
        :return: list of Products that matching the desired the search conditions.
        """
        no_filter = lambda p: True
        product_filter = (lambda p: product_name in p["product"]["name"]) if product_name else no_filter
        categories_filter = (
            lambda p: not (set(p["product"]["categories"]).isdisjoint(set(categories)))) if categories else no_filter
        brands_filter = (lambda p: p["product"]["brand"] in brands) if brands else no_filter

        if max_price is not None and max_price > 0:
            max_price_filter = (lambda p: p["after_discount"] <= max_price)
        else:
            max_price_filter = no_filter
        if min_price is not None and min_price >= 0:
            min_price_filter = (lambda p: p["after_discount"] >= min_price)
        else:
            min_price_filter = no_filter
        temp = []
        for product in self.inventory.values():
            temp.append(product.to_dictionary())
        matched = filter((lambda p: product_filter(p) and categories_filter(p) and brands_filter(p)
                                    and min_price_filter(p) and max_price_filter(p)), temp)
        return matched

    def search_product(self, product_name: str, categories: list = None,
                       brands: list = None,
                       min_price: float = None,
                       max_price: float = None):
        """
        search all products that answer the conditions
        :param product_name: (str) name of the products
        :param categories: (list of str) names of categories the products need to belong to (at least on of them)
        :param brands: (list of str) names of brands the product need to have (at least one)
        :param min_price: (float) minimum price for the product
        :param max_price: (float) maximum price for the product
        :return: list of Products that matching the desired the search conditions *AS DICTIONARIES*
        """
        matched = self._search_products(product_name, categories,
                                        brands,
                                        min_price,
                                        max_price)
        result = [{'store_name': self.name, 'product': item} for item in matched]
        return result

    def close_store_forever(self, admin_user: User):
        """
        deleting all members of the store before removing it from the system
        :param admin_user: User object who has to be admin
        :return: True if successful, False otherwise
        """
        if admin_user.is_admin():
            self.open = False
            initial_owner_permission: Permission = self._permissions[self.initial_owner]
            initial_owner_permission.remove_all_sub_members(admin_user.user_state.user_name)
            if self.name in initial_owner_permission.user.user_state.permissions:
                del initial_owner_permission.user.user_state.permissions[self.name]
            self._permissions.clear()
            self.inventory.clear()
            return True
        else:
            return False  # not an admin

    def _is_permitted_to_watch_history(self, to_check: User):
        """
        check if a given user ha a permit to watch store purchase history
        :param to_check: User to check
        :return: True if the user can wahtch this store purchase history False otherwise
        """

        if to_check.user_state.user_name in self._permissions:
            perm: Permission = self._permissions[to_check.user_state.user_name]
            self._dal.add(perm)
            return perm.watch_purchase_history
        return False  # not in store staff
