from __future__ import annotations

import enum
import json
import os
from dataclasses import dataclass
from typing import TYPE_CHECKING

from datetime import datetime, timedelta
from functools import reduce

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, orm
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import MutableList

from src.domain.system.DAL import DAL
from src.protocol_classes.classes_utils import TypeChecker, TypedDict

if TYPE_CHECKING:
    from src.domain.system.cart_purchase_classes import Basket, ProductInShoppingCart
    from src.domain.system.products_classes import ProductInInventory

from src.domain.system.db_config import db

__discount_id__ = 0


# Thanks for: https://stackoverflow.com/questions/1337095/sqlalchemy-inheritance
# Build according to here structure: https://flask.palletsprojects.com/en/1.1.x/patterns/sqlalchemy/
# https://github.com/sqlalchemy/sqlalchemy/issues/4858
# @event.listens_for(Engine, "connect")
# def set_sqlite_pragma(dbapi_connection, connection_record):
#     cursor = dbapi_connection.cursor()
#     '''
#     By default SQLite do not enforce foreign keys.
#     So: https://stackoverflow.com/questions/2614984/sqlite-sqlalchemy-how-to-enforce-foreign-keys
#     '''
#     cursor.execute("PRAGMA foreign_keys=ON")
#     cursor.close()


# class DBError(Exception):
#     """Base class for db exceptions"""
#     pass
#
#
# # String Constants
# CASCADE = 'CASCADE'
#
# db: SQLAlchemy = SQLAlchemy()
# #db: SQLAlchemy = DAL.get_instance().get_db()
# project_directory = os.getcwd()
# db_name = 'db'
# db_path = f'{project_directory}/{db_name}.db'
# d = DAL.get_instance()
# d.update_session(db.session)

# def generate_id():
#     """
#     generating new discount id (positive integer)
#     :return: new discount id
#     """
#     global __discount_id__
#     __discount_id__ += 1
#     return __discount_id__


@dataclass()
class CategoryToNeededPrice:
    category: str
    needed_price: float

    def __post_init__(self):
        if not isinstance(self.category, str):
            raise TypeError("discounts.py -> Not a valid str: category")
        if not (TypeChecker.check_for_positive_number([self.needed_price])):
            raise TypeError("discounts.py -> Not a valid float/int: needed_price")

    def to_dictionary(self):
        return {'category': self.category, 'needed_price': self.needed_price}

    def __str__(self):
        return f'{self.needed_price}$ from category {self.category}'


@dataclass()
class CategoryToNeededItems:
    category: str
    needed_items: int

    def __post_init__(self):
        if not isinstance(self.category, str):
            raise TypeError("discounts.py -> Not a valid str: category")
        if not (TypeChecker.check_for_positive_number([self.needed_items])):
            raise TypeError("discounts.py -> Not a valid int: needed_items")

    def to_dictionary(self):
        return {'category': self.category, 'needed_items': self.needed_items}

    def __str__(self):
        return f'{self.needed_items} from category {self.category}'


@dataclass()
class ProductToQuantity:
    product: str
    needed_items: int

    def __post_init__(self):
        if not isinstance(self.product, str):
            raise TypeError("discounts.py -> Not a valid str: product")
        if not (TypeChecker.check_for_positive_number([self.needed_items])):
            raise TypeError("discounts.py -> Not a valid int: needed_items")

    def to_dictionary(self):
        return {'product': self.product, 'needed_items': self.needed_items}

    def __str__(self):
        return f'{self.needed_items} of {self.product}'


@dataclass()
class ProductToNeededPrice:
    product: str
    needed_price: float

    def __post_init__(self):
        if not isinstance(self.product, str):
            raise TypeError("discounts.py -> Not a valid str: product")
        if not (TypeChecker.check_for_positive_number([self.needed_price])):
            raise TypeError("discounts.py -> Not a valid float/int: needed_price")

    def to_dictionary(self):
        return {'product': self.product, 'needed_price': self.needed_price}

    def __str__(self):
        return f'{self.needed_price}$ worth of {self.product}'


class _IDiscountCondition(db.Model):
    __tablename__ = 'discount_condition'
    condition_type = db.Column(db.VARCHAR(40))
    __mapper_args__ = {
        'polymorphic_identity': 'discount_condition',
        'polymorphic_on': condition_type
    }
    id = db.Column(db.Integer, primary_key=True)
    _end_time = db.Column(db.DateTime)

    def __init__(self, end_time: datetime):
        self.end_time = end_time

    @property
    def end_time(self):
        return self._end_time

    @end_time.setter
    def end_time(self, new_end_time: datetime):
        if isinstance(new_end_time, datetime):
            self._end_time = new_end_time
        else:
            raise TypeError(f"discount: expected datetime or None, got {type(new_end_time)}")

    def is_discount_time_valid(self) -> bool:
        """
        :return: True if the date time of the discount is still  valid, False otherwise
        """
        return self._end_time > datetime.now()

    def check_condition(self, basket: Basket) -> bool:
        return self.is_discount_time_valid()

    def get_description_condition(self):
        return f"until date {self._end_time.strftime('%d-%m-%Y')}"

    @staticmethod
    def create_simple_condition(end_time: datetime):
        return _IDiscountCondition(end_time=end_time)

    def is_product_affected_by_discount(self, product_name, categories) -> bool:
        return False

    def relevant_products_and_categories(self):
        return [], []


class DiscountConditionCombo(_IDiscountCondition):
    __tablename__ = 'discount_condition_combo'
    __mapper_args__ = {
        'polymorphic_identity': 'discount_condition_combo',
    }
    id = db.Column(db.Integer, db.ForeignKey('discount_condition.id'), primary_key=True)
    _size_of_basket_cond = db.Column(db.Integer)
    _over_all_price_category_cond = db.Column(db.JSON)
    _over_all_price_product_cond = db.Column(db.JSON)
    _product_list_cond = db.Column(db.JSON)
    _overall_category_quantity = db.Column(db.JSON)

    def __init__(self, end_time: datetime, size_of_basket_cond: int = None, over_all_price_category_cond: list = None,
                 over_all_price_product_cond: list = None, product_list_cond: list = None,
                 overall_category_quantity: list = None):
        super().__init__(end_time)
        self.size_of_basket_cond = size_of_basket_cond
        self.over_all_price_category_cond = over_all_price_category_cond
        self.over_all_price_product_cond = over_all_price_product_cond
        self.product_list_cond = product_list_cond
        self.overall_category_quantity = overall_category_quantity

    def get_description_condition(self):
        base = f"until date {self._end_time.date().strftime('%d-%m-%Y')}"
        if self.size_of_basket_cond is not None and self.size_of_basket_cond > 0:
            base = f'{base}\n minimum size of basket: {self._size_of_basket_cond}\n'

        if self.over_all_price_product_cond is not None and len(self.over_all_price_product_cond) > 0:
            all_p_descriptions = [str(p) for p in self.over_all_price_product_cond]
            description = reduce((lambda acc, curr: f'{acc}, {curr}'), all_p_descriptions)
            base = f'{base}\n minimum price for products: {description}'

        if self.over_all_price_category_cond is not None and len(self.over_all_price_category_cond) > 0:
            all_p_descriptions = [str(p) for p in self.over_all_price_category_cond]
            description = reduce((lambda acc, curr: f'{acc}, {curr}'), all_p_descriptions)
            base = f'{base}\n minimum price for category: {description}'

        if self.product_list_cond is not None and len(self.product_list_cond) > 0:
            all_p_descriptions = [str(p) for p in self.product_list_cond]
            description = reduce((lambda acc, curr: f'{acc}, {curr}'), all_p_descriptions)
            base = f'{base}\nminimum quantity for products: {description}\n'

        if self.overall_category_quantity is not None and len(self.overall_category_quantity) > 0:
            all_p_descriptions = [str(p) for p in self.overall_category_quantity]
            description = reduce((lambda acc, curr: f'{acc}, {curr}'), all_p_descriptions)
            base = f'{base}\nminimum quantity for category: {description}'
        return base

    def relevant_products_and_categories(self):
        categories = []
        products = []
        if self.over_all_price_product_cond is not None and len(self.over_all_price_product_cond) > 0:
            product_names = [p.product for p in self.over_all_price_product_cond]
            products = products + product_names
        if self.over_all_price_category_cond is not None and len(self.over_all_price_category_cond) > 0:
            categories_names = [c.category for c in self.over_all_price_category_cond]
            categories = categories + categories_names
        if self.product_list_cond is not None and len(self.product_list_cond) > 0:
            product_names = [p.product for p in self.product_list_cond]
            products = products + product_names
        if self.overall_category_quantity is not None and len(self.overall_category_quantity) > 0:
            for category in categories:
                categories_names = [c.category for c in self.overall_category_quantity]
                categories = categories + categories_names
        return products, categories

    def is_product_affected_by_discount(self, product_name: str, categories: list) -> bool:
        if self.size_of_basket_cond is not None and self.size_of_basket_cond > 0:
            return True
        elif self.over_all_price_product_cond is not None and len(self.over_all_price_product_cond) > 0:
            product_names = [p.product for p in self.over_all_price_product_cond]
            if product_name in product_names:
                return True
        elif self.over_all_price_category_cond is not None and len(self.over_all_price_category_cond) > 0:
            categories_names = [c.category for c in self.over_all_price_category_cond]
            for category in categories:
                if category in categories_names:
                    return True
        elif self.product_list_cond is not None and len(self.product_list_cond) > 0:
            product_names = [p.product for p in self.product_list_cond]
            if product_name in product_names:
                return True
        elif self.overall_category_quantity is not None and len(self.overall_category_quantity) > 0:
            categories_names = [c.category for c in self.overall_category_quantity]
            for category in categories:
                if category in categories_names:
                    return True
        return False

    @staticmethod
    def create_combo_condition(end_time: datetime, size_of_basket_cond: int = None,
                               over_all_price_category_cond: list = None,
                               over_all_price_product_cond: list = None, product_list_cond: list = None,
                               overall_category_quantity: list = None):
        if size_of_basket_cond is None and over_all_price_category_cond is None and over_all_price_product_cond is None and product_list_cond is None and overall_category_quantity is None:
            return _IDiscountCondition(end_time)
        else:
            if over_all_price_category_cond is not None:
                over_all_price_category_cond = [CategoryToNeededPrice(c["category_name"], c["needed_price"]) for c in
                                                over_all_price_category_cond]

            if overall_category_quantity is not None:
                overall_category_quantity = [CategoryToNeededItems(c["category_name"], c["needed_items"]) for c in
                                             overall_category_quantity]

            if over_all_price_product_cond is not None:
                over_all_price_product_cond = [ProductToNeededPrice(p["product_name"], p["needed_price"]) for p in
                                               over_all_price_product_cond]
            if product_list_cond is not None:
                product_list_cond = [ProductToQuantity(p["product_name"], p["needed_items"]) for p in
                                     product_list_cond]

            return DiscountConditionCombo(end_time, size_of_basket_cond, over_all_price_category_cond,
                                          over_all_price_product_cond, product_list_cond, overall_category_quantity)

    @property
    def size_of_basket_cond(self):
        return self._size_of_basket_cond

    @size_of_basket_cond.setter
    def size_of_basket_cond(self, new_size_of_basket_cond: int):
        if new_size_of_basket_cond is None or type(new_size_of_basket_cond) == int:
            self._size_of_basket_cond = new_size_of_basket_cond
        else:
            raise TypeError(f"discount: expected int or None, got {type(new_size_of_basket_cond)}")

    @property
    def over_all_price_category_cond(self):
        return [CategoryToNeededPrice(c["category"], c["needed_price"]) for c in
                json.loads(self._over_all_price_category_cond)]

    @over_all_price_category_cond.setter
    def over_all_price_category_cond(self, new_over_all_price_category_cond: list):
        if new_over_all_price_category_cond is None or isinstance(new_over_all_price_category_cond, list):
            self._over_all_price_category_cond = json.dumps(
                [x.to_dictionary() for x in new_over_all_price_category_cond])
        else:
            raise TypeError(f"discount: expected list or None, got {type(new_over_all_price_category_cond)}")

    @property
    def over_all_price_product_cond(self):
        return [ProductToNeededPrice(p["product"], p["needed_price"]) for p in
                json.loads(self._over_all_price_product_cond)]

    @over_all_price_product_cond.setter
    def over_all_price_product_cond(self, new_over_all_price_product_cond: list):
        if new_over_all_price_product_cond is None or isinstance(new_over_all_price_product_cond, list):
            self._over_all_price_product_cond = json.dumps([x.to_dictionary() for x in new_over_all_price_product_cond])
        else:
            raise TypeError(f"discount: expected list or None, got {type(new_over_all_price_product_cond)}")

    @property
    def product_list_cond(self):
        return [ProductToQuantity(p["product"], p["needed_items"]) for p in
                json.loads(self._product_list_cond)]

    @product_list_cond.setter
    def product_list_cond(self, new_product_list_cond: list):
        if new_product_list_cond is None or isinstance(new_product_list_cond, list):
            self._product_list_cond = json.dumps([x.to_dictionary() for x in new_product_list_cond])
        else:
            raise TypeError(f"discount: expected list or None, got {type(new_product_list_cond)}")

    @property
    def overall_category_quantity(self):
        return [CategoryToNeededItems(c["category"], c["needed_items"]) for c in
                json.loads(self._overall_category_quantity)]

    @overall_category_quantity.setter
    def overall_category_quantity(self, new_overall_category_quantity: list):
        if new_overall_category_quantity is None or isinstance(new_overall_category_quantity, list):
            self._overall_category_quantity = json.dumps([x.to_dictionary() for x in new_overall_category_quantity])
        else:
            raise TypeError(f"discount: expected list or None, got {type(new_overall_category_quantity)}")

    def is_size_of_basket_cond_valid(self, basket: Basket) -> bool:
        """
        check if the basket answers the given size cond
        :param basket: (Basket) the basket to check
        :return: True if the size of the basket is valid, False otherwise
        """
        return self.size_of_basket_cond is None or sum(
            [p._product_quantity for p in basket.products.values()]) >= self.size_of_basket_cond


    def is_over_all_price_category_cond_valid(self, basket: Basket) -> bool:
        """
        check if the basket answers the given categories having enough product to have the given price
        :param basket: (Basket) the basket to check
        :return: True each category have the given price value with products, False otherwise
        """
        if self.over_all_price_category_cond is None:
            return True
        for category in self.over_all_price_category_cond:
            category_to_price: CategoryToNeededPrice = category
            filtered_by_category_items = [p._total_price for k, p in
                                          basket.products.items()
                                          if category_to_price.category in p.item.categories]
            total = reduce((lambda acc, price: acc + price), filtered_by_category_items)
            if total < category_to_price.needed_price:
                return False
        return True

    def is_overall_category_quantity_valid(self, basket):
        """
        check if the basket have enough quantity of each category
        :param basket:  (Basket) the basket to check
        :return: True each category have the given quantity , False otherwise
        """
        if self.overall_category_quantity is None:
            return True
        for category in self.overall_category_quantity:
            category_to_quantity: CategoryToNeededItems = category
            filtered_by_category_items = [p.item.quantity for k, p in basket.products.items() if
                                          category_to_quantity.category in p.item.categories]
            total = reduce((lambda acc, quantity: acc + quantity), filtered_by_category_items)
            if total < category_to_quantity.needed_items:
                return False
        return True

    def is_over_all_price_product_cond_valid(self, basket: Basket) -> bool:
        """
        check if the basket answers the given categories having enough product to have the given price
        :param basket: (Basket) the basket to check
        :return: True each category have the given price value with products, False otherwise
        """
        if self.over_all_price_product_cond is None:
            return True
        for product in self.over_all_price_product_cond:
            product_to_price: ProductToNeededPrice = product
            if product_to_price.product in basket.products and basket.products[
                product_to_price.product]._total_price < product_to_price.needed_price:
                return False
        return True

    def is_overall_product_quantity_valid(self, basket):
        """
        check if the basket have enough quantity of each product needed
        :param basket:  (Basket) the basket to check
        :return: True each Product have the given quantity , False otherwise
        """
        if self.product_list_cond is None:
            return True
        for product in self.product_list_cond:
            product_to_quantity: ProductToQuantity = product
            if product_to_quantity.product in basket.products and basket.products[
                product_to_quantity.product].item.quantity < product_to_quantity.needed_items:
                return False
        return True

    def check_condition(self, basket: Basket) -> bool:
        """
        checking the given baskets is answering all discount conditions
        :param basket:
        :return:
        """
        return self.is_discount_time_valid() and self.is_size_of_basket_cond_valid(
            basket) and self.is_over_all_price_category_cond_valid(
            basket) and self.is_over_all_price_product_cond_valid(basket) and self.is_overall_category_quantity_valid(
            basket) and self.is_overall_product_quantity_valid(basket)


class _IDiscountStrategy(db.Model):
    __tablename__ = 'discount_strategy'
    id = db.Column(db.Integer, primary_key=True)
    discount_type = db.Column(db.VARCHAR(length=40))
    __mapper_args__ = {
        'polymorphic_identity': 'discount_strategy',
        'polymorphic_on': discount_type
    }

    def activate_discount(self, basket: Basket) -> Basket:
        """
        Activate the Discount strategy on the Basket, to reduce it's price if possible
        :param basket: (Basket) basket to activate the discount to
        :return: basket after discount was activated, or the same basket if the discount was not possible
        """
        return basket

    def get_description_strategy(self):
        return ""

    def is_product_affected_by_discount(self, product_name: str, categories: list) -> bool:
        return False

    def relevant_products_and_categories(self):
        return [], []

    def activate_discount_on_single_product(self, product: ProductInInventory, current_price: float) -> float:
        """
        activating discount strategy for marketing purposes when showing the product in the store
        :param product: product to calc it's reduce price
        :param current_price: current discounted price
        :return: reduced price after this strategy
        """
        return current_price


class BasketDiscountStrategy(_IDiscountStrategy):
    _discount_percent = db.Column(db.Float)
    __mapper_args__ = {"polymorphic_identity": "basket_discount_strategy"}

    def __init__(self, discount_percent: float):
        self.discount_percent = discount_percent

    @declared_attr
    def _discount_percent(cls):
        return _IDiscountStrategy.__table__.c.get('_discount_percent', db.Column(db.Float))

    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, new_discount_percent: float):
        if isinstance(new_discount_percent, float) and 0 <= new_discount_percent < 1:
            self._discount_percent = new_discount_percent
        else:
            raise TypeError(
                f"discount: expected float from 0 to 1, got {type(new_discount_percent)}: {new_discount_percent}")

    def activate_discount(self, basket: Basket) -> Basket:
        """
        giving given percentage of discount on the given product
        :param basket:  (Basket) basket to activate the discount to
        :return:  basket after discount was activated, or the same basket if the product was not in the basket
        """
        for product, item in basket.products.items():
            item._total_price = item._total_price * (1 - self.discount_percent)
        return basket

    def activate_discount_on_single_product(self, product: ProductInInventory, current_price: float) -> float:
        """
        activating discount strategy for marketing purposes when showing the product in the store
        :param product: product to calc it's reduce price
        :param current_price: current discounted price
        :return: reduced price after this strategy
        """
        return current_price * (1 - self.discount_percent)

    def get_description_strategy(self):
        return f"get discount {self.discount_percent * 100}% on entire baskets"

    def is_product_affected_by_discount(self, product_name: str, categories: list) -> bool:
        return True

    def relevant_products_and_categories(self):
        return [], []

    @staticmethod
    def create_basket_discount_strategy(discount_percent: float):
        return BasketDiscountStrategy(discount_percent)


class ProductDiscountStrategy(_IDiscountStrategy):
    _discount_percent = db.Column(db.Float)
    _discounted_product = db.Column(db.String(100))
    __mapper_args__ = {"polymorphic_identity": "product_discount_strategy"}

    def __init__(self, discount_percent: float, discounted_product: str):
        self.discounted_product = discounted_product
        self.discount_percent = discount_percent

    # When we have multiple classes inherit and having the same column when using single table inheritance
    # we should use the following which pointed by https://stackoverflow.com/questions/17111453/sqlalchemy-single-table-inheritance-same-column-in-childs
    # and suggested by SQLAlchemy docs.
    @declared_attr
    def _discount_percent(cls):
        return _IDiscountStrategy.__table__.c.get('_discount_percent', db.Column(db.Float))

    def activate_discount_on_single_product(self, product: ProductInInventory, current_price: float) -> float:
        """
        activating discount strategy for marketing purposes when showing the product in the store
        :param product: product to calc it's reduce price
        :param current_price: current discounted price
        :return: reduced price after this strategy
        """
        if product.product.name == self.discounted_product:
            return current_price * (1 - self.discount_percent)
        return current_price

    @property
    def discounted_product(self):
        return self._discounted_product

    @discounted_product.setter
    def discounted_product(self, new_discounted_product: str):
        if isinstance(new_discounted_product, str):
            self._discounted_product = new_discounted_product
        else:
            raise TypeError(f"discount: expected str, got {type(new_discounted_product)}")

    def is_product_affected_by_discount(self, product_name: str, categories: list) -> bool:
        return product_name == self.discounted_product

    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, new_discount_percent: float):
        if isinstance(new_discount_percent, float) and 0 <= new_discount_percent < 1:
            self._discount_percent = new_discount_percent
        else:
            raise TypeError(
                f"discount: expected float from 0 to 1, got {type(new_discount_percent)}: {new_discount_percent}")

    def activate_discount(self, basket: Basket) -> Basket:
        """
        giving given percentage of discount on the given product
        :param basket:  (Basket) basket to activate the discount to
        :return:  basket after discount was activated, or the same basket if the product was not in the basket
        """
        if self.discounted_product in basket.products:
            item: ProductInShoppingCart = basket.products[self.discounted_product]
            item._total_price = item._total_price * (1 - self.discount_percent)
        return basket

    def get_description_strategy(self):
        return f"get discount of {self.discount_percent * 100}% on products: {self.discounted_product}"

    def relevant_products_and_categories(self):
        return [self.discounted_product], []

    @staticmethod
    def create_product_discount_strategy(discount_percent: float, discounted_product: str):
        return ProductDiscountStrategy(discount_percent, discounted_product)


class CategoryDiscountStrategy(_IDiscountStrategy):
    __mapper_args__ = {
        'polymorphic_identity': 'category_discount_strategy'
    }
    _discount_percent = db.Column(db.Float)
    _discounted_category = db.Column(db.String(100))

    def __init__(self, discount_percent: float, discounted_category: str):
        self.discounted_category = discounted_category
        self.discount_percent = discount_percent

    @declared_attr
    def _discount_percent(cls):
        return _IDiscountStrategy.__table__.c.get('_discount_percent', db.Column(db.Float))

    def activate_discount_on_single_product(self, product: ProductInInventory, current_price: float) -> float:
        """
        activating discount strategy for marketing purposes when showing the product in the store
        :param product: product to calc it's reduce price
        :param current_price: current discounted price
        :return: reduced price after this strategy
        """
        if self.discounted_category in product.product.categories:
            return current_price * (1 - self.discount_percent)
        return current_price

    @property
    def discounted_category(self):
        return self._discounted_category

    @discounted_category.setter
    def discounted_category(self, new_discounted_category: str):
        if isinstance(new_discounted_category, str):
            self._discounted_category = new_discounted_category
        else:
            raise TypeError(f"discount: expected str, got {type(new_discounted_category)}")

    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, new_discount_percent: float):
        if isinstance(new_discount_percent, float) and 0 <= new_discount_percent < 1:
            self._discount_percent = new_discount_percent
        else:
            raise TypeError(
                f"discount: expected float from 0 to 1, got {type(new_discount_percent)}: {new_discount_percent}")

    def is_product_affected_by_discount(self, product_name: str, categories: list) -> bool:
        return self.discounted_category in categories

    def activate_discount(self, basket: Basket) -> Basket:
        """
        giving given percentage of discount on the given category
        :param basket:  (Basket) basket to activate the discount to
        :return:  basket after discount was activated, or the same basket if the given category was not in the basket
        """
        filtered_by_category_items = [p for k, p in basket.products.items() if
                                      self.discounted_category in p.item.categories]
        for p in filtered_by_category_items:
            p._total_price = p._total_price * (1 - self.discount_percent)
        return basket

    def get_description_strategy(self):
        return f"get discount of {self.discount_percent * 100}% on category: {self.discounted_category}"

    @staticmethod
    def create_category_discount_strategy(discount_percent: float, discounted_category: str):
        return CategoryDiscountStrategy(discount_percent, discounted_category)

    def relevant_products_and_categories(self):
        return [], [self.discounted_category]


class FreePerXProductDiscountStrategy(_IDiscountStrategy):
    __mapper_args__ = {
        'polymorphic_identity': 'free_per_x_product_discount_strategy'
    }
    _product = db.Column(db.String(100))
    _is_duplicate = db.Column(db.Boolean)
    _per = db.Column(db.Integer)
    _free = db.Column(db.Integer)

    @declared_attr
    def _product(cls):
        return _IDiscountStrategy.__table__.c.get('_discounted_product', db.Column(db.String(100)))

    @declared_attr
    def _per(cls):
        return _IDiscountStrategy.__table__.c.get('_per', db.Column(db.Integer))

    @declared_attr
    def _free(cls):
        return _IDiscountStrategy.__table__.c.get('_free', db.Column(db.Integer))

    @declared_attr
    def _is_duplicate(cls):
        return _IDiscountStrategy.__table__.c.get('_is_duplicate', db.Column(db.Boolean))

    def __init__(self, product: str, free: int, per: int, is_duplicate: bool = True):
        if free >= per:
            raise TypeError("free amount cannot be greater than per amount")

        self.is_duplicate = is_duplicate
        self.product = product
        self.free_amount = free
        self.per_x_amount = per

    def is_product_affected_by_discount(self, product_name: str, categories: list) -> bool:
        return self.product == product_name

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, new_product: str):
        if isinstance(new_product, str) and new_product != "":
            self._product = new_product

        else:
            raise TypeError(f"discount: expected dtr, got {type(new_product)}")

    @property
    def free_amount(self):
        return self._free

    @free_amount.setter
    def free_amount(self, new_free: int):
        if isinstance(new_free, int):
            self._free = new_free

        else:
            raise TypeError(f"discount: expected int, got {type(new_free)}")

    @property
    def per_x_amount(self):
        return self._per

    @per_x_amount.setter
    def per_x_amount(self, new_per: int):
        if isinstance(new_per, int):
            self._per = new_per

        else:
            raise TypeError(f"discount: expected int, got {type(new_per)}")

    @property
    def is_duplicate(self):
        return self._is_duplicate

    @is_duplicate.setter
    def is_duplicate(self, new_is_duplicate: bool):
        if type(new_is_duplicate) == bool:
            self._is_duplicate = new_is_duplicate
        else:
            raise TypeError(
                f"discount: expected bool, got {type(new_is_duplicate)}: {new_is_duplicate}")

    def activate_discount(self, basket: Basket) -> Basket:
        """
        reducing price on the given product if it's exists in baskets
        in the given quantity, else, returning the same basket without the discount
        :param basket: (Basket) basket to activate this discount to
        :return: basket with reduce price after discount, or the same discount if there is not enough of that product
        """
        if self.product in basket.products:
            product: ProductInShoppingCart = basket.products[self.product]
            temp_base_price: float = float(float(product._total_price) / float(product.item.quantity))
            temp_quantity = product.item.quantity
            if self.is_duplicate:
                while temp_quantity >= self.free_amount + self.per_x_amount:
                    product._total_price = product._total_price - temp_base_price * self.free_amount
                    temp_quantity -= (self.free_amount + self.per_x_amount)
                return basket
            else:
                if temp_quantity >= self.free_amount + self.per_x_amount:
                    product._total_price = product._total_price - temp_base_price * self.free_amount
                return basket
        else:
            return basket

    def relevant_products_and_categories(self):
        return [self.product], []

    def get_description_strategy(self):
        return f"get free {self.free_amount} on every {self.per_x_amount} of product {self.product}"

    @staticmethod
    def create_free_per_x_product_discount_strategy(product_name: str, free_amount: int, per_x_amount: int,
                                                    is_duplicate: bool = True):
        if free_amount >= per_x_amount:
            raise TypeError(
                f"discounts.py:480 -> free_amount({free_amount}) cannot be bigger or equal than per_x_amount({per_x_amount})")

        return FreePerXProductDiscountStrategy(product_name, free_amount, per_x_amount, is_duplicate)


class FreePerXCategoryDiscountStrategy(_IDiscountStrategy):
    __mapper_args__ = {
        'polymorphic_identity': 'free_per_x_category_discount_strategy'
    }
    _category = db.Column(db.String(100))
    _is_duplicate = db.Column(db.Boolean)
    _per = db.Column(db.Integer)
    _free = db.Column(db.Integer)

    @declared_attr
    def _category(cls):
        return _IDiscountStrategy.__table__.c.get('_discounted_category', db.Column(db.String(100)))

    @declared_attr
    def _per(cls):
        return _IDiscountStrategy.__table__.c.get('_per', db.Column(db.Integer))

    @declared_attr
    def _free(cls):
        return _IDiscountStrategy.__table__.c.get('_free', db.Column(db.Integer))

    @declared_attr
    def _is_duplicate(cls):
        return _IDiscountStrategy.__table__.c.get('_is_duplicate', db.Column(db.Boolean))

    def __init__(self, category: str, free: int, per: int, is_duplicate: bool = True):
        if free >= per:
            raise TypeError("free amount cannot be greater than per amount")
        self.is_duplicate = is_duplicate
        self.category = category
        self.free_amount = free
        self.per_x_amount = per

    def is_product_affected_by_discount(self, product_name: str, categories: list) -> bool:
        return self.category in categories

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, new_category: str):
        if isinstance(new_category, str) and new_category != "":
            self._category = new_category

        else:
            raise TypeError(f"discount: expected dtr, got {type(new_category)}")

    @property
    def free_amount(self):
        return self._free

    @free_amount.setter
    def free_amount(self, new_free: int):
        if isinstance(new_free, int):
            self._free = new_free

        else:
            raise TypeError(f"discount: expected int, got {type(new_free)}")

    @property
    def per_x_amount(self):
        return self._per

    @per_x_amount.setter
    def per_x_amount(self, new_per: int):
        if isinstance(new_per, int):
            self._per = new_per

        else:
            raise TypeError(f"discount: expected int, got {type(new_per)}")

    @property
    def is_duplicate(self):
        return self._is_duplicate

    @is_duplicate.setter
    def is_duplicate(self, new_is_duplicate: bool):
        if type(new_is_duplicate) == bool:
            self._is_duplicate = new_is_duplicate
        else:
            raise TypeError(
                f"discount: expected bool, got {type(new_is_duplicate)}: {new_is_duplicate}")

    def activate_discount(self, basket: Basket) -> Basket:
        """
        reducing price on the given category if it's exists in baskets
        in the given quantity, else, returning the same basket without the discount
        :param basket: (Basket) basket to activate this discount to
        :return: basket with reduce price after discount, or the same discount if there is not enough of that category
        """
        filtered_products_by_category = [p for k, p in basket.products.items() if
                                         self.category in p.item.categories]
        if len(filtered_products_by_category) == 0:
            return basket
        for p in filtered_products_by_category:
            product: ProductInShoppingCart = p
            temp_base_price: float = float(float(product._total_price) / float(product.item.quantity))
            temp_quantity = product.item.quantity
            if self.is_duplicate:
                while temp_quantity >= self.free_amount + self.per_x_amount:
                    product._total_price = product._total_price - temp_base_price * self.free_amount
                    temp_quantity -= (self.free_amount + self.per_x_amount)
            else:
                if temp_quantity >= self.free_amount + self.per_x_amount:
                    product._total_price = product._total_price - temp_base_price * self.free_amount
        return basket

    def get_description_strategy(self):
        return f"get free {self.free_amount} on every {self.per_x_amount} of category {self.category}"

    def relevant_products_and_categories(self):
        return [], [self.category]

    @staticmethod
    def create_free_per_x_product_discount_strategy(category_name: str, free_amount: int, per_x_amount: int,
                                                    is_duplicate: bool = True):
        if free_amount >= per_x_amount:
            raise TypeError(
                f"discounts.py:546 -> free_amount({free_amount}) cannot be bigger or equal than per_x_amount({per_x_amount})")
        return FreePerXCategoryDiscountStrategy(category_name, free_amount, per_x_amount, is_duplicate)


class _IDiscount(db.Model):
    """
    Discount Interface to define the different conditions parameters the
    """
    __tablename__ = 'discount'
    _dal: DAL = DAL.get_instance()
    id = db.Column(db.Integer, primary_key=True)
    _discount_strategy_fk = db.Column(db.Integer, db.ForeignKey('discount_strategy.id'))
    _discount_condition_fk = db.Column(db.Integer, db.ForeignKey('discount_condition.id'))
    _discount_strategy = db.relationship(_IDiscountStrategy, lazy="joined")
    _discount_condition = db.relationship(_IDiscountCondition, lazy="joined")
    discount_type = db.Column(db.VARCHAR(40))
    __mapper_args__ = {
        'polymorphic_identity': 'i_discount',
        'polymorphic_on': discount_type
    }

    # def __init__(self, discount_condition: _IDiscountCondition = None, discount_strategy: _IDiscountStrategy = None,
    #              discount_id: int = -1):
    def __init__(self, discount_condition: _IDiscountCondition = None, discount_strategy: _IDiscountStrategy = None):
        if discount_condition is None:
            discount_condition = _IDiscountCondition(datetime.now())
        if discount_strategy is None:
            discount_strategy = _IDiscountStrategy()
        self.discount_condition = discount_condition
        self.discount_strategy = discount_strategy
        self.is_implemented = False
        self.is_possible = False
        # self._id = generate_id() if discount_id < 0 else discount_id

    # def update_parent(self, parent_id):
    #     self._complex_parent_id = parent_id

    def give_all_stuff_to_delete(self):
        return [self.discount_strategy, self.discount_condition, self]

    def delete_from_db(self):
        self._dal.delete_all(self.give_all_stuff_to_delete(), del_only=True)
        self._dal.flush()  # So we ill able to call .id

    def reset_flags(self):
        self.is_implemented = False
        self.is_possible = False

    def refresh_self(self):
        try:
            self._dal._db_session.add(self)
            self._dal._db_session.refresh(self)
        except:
            pass

    def get_description(self):
        self.refresh_self()
        return f'{self.discount_strategy.get_description_strategy()}\n  condition: {self.discount_condition.get_description_condition()}\n'

    def is_product_affected_by_discount(self, product_name: str, categories: list):
        if self.discount_strategy.is_product_affected_by_discount(product_name,
                                                                  categories) or self.discount_condition.is_product_affected_by_discount(
            product_name, categories):
            return [self]
        return None

    # @property
    # def id(self):
    #     return self._id
    #
    # @id.setter
    # def id(self, new_id: _IDiscountCondition):
    #     if isinstance(new_id, int):
    #         self._id = new_id
    #     else:
    #         raise TypeError(f"discount: expected positive int, got {type(new_id)}")

    @property
    def discount_condition(self):
        return self._discount_condition

    @discount_condition.setter
    def discount_condition(self, new_discount_condition: _IDiscountCondition):
        if isinstance(new_discount_condition, _IDiscountCondition):
            self._discount_condition = new_discount_condition
        else:
            raise TypeError(f"discount: expected _IDiscountCondition or None, got {type(new_discount_condition)}")

    @property
    def discount_strategy(self):
        return self._discount_strategy

    @discount_strategy.setter
    def discount_strategy(self, new_discount_strategy: _IDiscountStrategy):
        if isinstance(new_discount_strategy, _IDiscountStrategy):
            self._discount_strategy = new_discount_strategy
        else:
            raise TypeError(f"discount: expected _IDiscountStrategy, got {type(new_discount_strategy)}")

    @property
    def is_implemented(self):
        return self._is_implemented

    @is_implemented.setter
    def is_implemented(self, new_is_implemented: bool):
        if isinstance(new_is_implemented, bool):
            self._is_implemented = new_is_implemented
        else:
            raise TypeError(f"discount: expected bool or None, got {type(new_is_implemented)}")

    @property
    def is_possible(self):
        return self._is_possible

    @is_possible.setter
    def is_possible(self, new_is_possible: bool):
        if isinstance(new_is_possible, bool):
            self._is_possible = new_is_possible
        else:
            raise TypeError(f"discount: expected bool or None, got {type(new_is_possible)}")

    def basic_discount_application(self, basket: Basket) -> Basket:
        """
        basic application of activating first the condition
        :param basket:
        :return:
        """
        self.is_possible = self.discount_condition is None or self.discount_condition.check_condition(basket)
        if self.is_possible:
            total_price_of_basket_before_discount = basket.get_total_value_of_basket()
            output_basket: Basket = self.discount_strategy.activate_discount(basket.copy())
            if output_basket.get_total_value_of_basket() < total_price_of_basket_before_discount:
                self.is_implemented = True
                return output_basket
            else:
                return basket
        else:
            return basket

    def apply(self, basket: Basket) -> Basket:
        """
        applying giving discount if the condition to the discount true.
        :param basket: (Basket) basket to apply discount to
        :return: basket after Discount if possible
        """
        return self.basic_discount_application(basket)

    def search_for_discount(self, to_search: int):
        return None

    def remove_discount(self, to_remove: int):
        return None

    def edit_discount(self, to_edit: int, edited_discount: _IDiscount):
        if to_edit == self.id:
            self.discount_condition = edited_discount.discount_condition
            self.discount_strategy = edited_discount._discount_strategy
            return self
        return None  # if the id doesn't match

    def relevant_products_and_categories(self):
        condition_tuple = self.discount_condition.relevant_products_and_categories()
        strategy_tuple = self.discount_strategy.relevant_products_and_categories()
        return condition_tuple[0] + strategy_tuple[0], condition_tuple[1] + strategy_tuple[1]

    def get_all_discounts(self):
        """
        :return: list of all discounts in the discount children. build from id an description
        """
        return []


class ComplexDiscountTypes(enum.Enum):
    XOR = 1
    OR = 2
    AND = 3

    def to_string(self):
        if self == ComplexDiscountTypes.XOR:
            return "XOR"
        elif self == ComplexDiscountTypes.OR:
            return "OR"
        elif self == ComplexDiscountTypes.AND:
            return "AND"
        else:
            return None

    @staticmethod
    def convert_from_string(to_convert: str):
        to_convert = to_convert.upper()
        if to_convert.upper() == "XOR":
            return ComplexDiscountTypes.XOR
        elif to_convert.upper() == "OR":
            return ComplexDiscountTypes.OR
        elif to_convert.upper() == "AND":
            return ComplexDiscountTypes.AND
        else:
            return None


class ComplexDiscount(_IDiscount):
    __tablename__ = 'complex_discount'
    id = db.Column(db.Integer, db.ForeignKey("discount.id"), primary_key=True)
    # _parent_id = db.Column(db.ForeignKey("discount.id"))
    # _dal = DAL.get_instance()
    # Relationship for inheritance
    _children_discounts_ls = db.Column(MutableList.as_mutable(db.JSON))
    _operator = db.Column(db.Integer)
    # SAWarning: Implicitly combining column discount.id with column complex_discount.id under attribute 'id'.  Please configure one or more attributes for these same-named columns explicitly.
    #   util.warn(msg)
    __mapper_args__ = {
        'polymorphic_identity': 'complex_discount',
        # 'inherit_condition': _parent_id == _IDiscount.id
    }

    def __init__(self, discount_condition: _IDiscountCondition, discount_strategy: _IDiscountStrategy,
                 children_discounts: dict = None):
        super().__init__(discount_condition, discount_strategy)
        # {id1: _IDiscount, id2: _IDiscount}
        self._children_discounts_ls = [] if children_discounts is None else list(children_discounts.keys())
        self._children_discounts_dict = TypedDict(int, _IDiscount, children_discounts)

    @orm.reconstructor
    def _init_on_load(self):
        self._children_discounts_dict = self._dal.get_discount_map_with_id_keys(self._children_discounts_ls)

    @property
    def children_discounts_ls(self):
        return self._children_discounts_ls

    @children_discounts_ls.setter
    def children_discounts_ls(self, new_children_discounts: list):
        if new_children_discounts is None:
            self._children_discounts_ls = list()
        if isinstance(new_children_discounts, list):
            self._children_discounts_ls = new_children_discounts
        else:
            raise TypeError(
                f"discount: expected list of int or None, got {type(new_children_discounts)}")

    @property
    def children_discounts_dict(self):
        return self._children_discounts_dict

    @children_discounts_dict.setter
    def children_discounts_dict(self, new_children_discounts: TypedDict):
        if new_children_discounts is None:
            self._children_discounts_dict = TypedDict(int, _IDiscount)
        if isinstance(new_children_discounts, TypedDict) and new_children_discounts.check_types(int, _IDiscount):
            self._children_discounts_dict = new_children_discounts
        else:
            raise TypeError(
                f"discount: expected TypedDict of int to _IDiscount or None, got {type(new_children_discounts)}")

    def give_all_stuff_to_delete(self):
        to_delete = []
        for k, child in self.children_discounts_dict.items():
            child: _IDiscount = child
            to_delete.extend(child.give_all_stuff_to_delete())
            to_delete.extend([child.discount_condition, child.discount_strategy, child])
        to_delete.extend([self.discount_condition, self.discount_strategy, self])
        return to_delete

    def delete_from_db(self):
        self._dal.delete_all(self.give_all_stuff_to_delete(), del_only=True)
        self._dal.flush()  # So we ill able to call .id

    def get_all_discounts(self):
        """
        :return: list of all discounts in the store. build from id an description
        """
        output = []
        for k, child in self.children_discounts_dict.items():
            output.append(child)
            output.extend(child.get_all_discounts())
        return output

    def reset_flags(self):
        for k, child in self.children_discounts_dict.items():
            child: _IDiscount = child
            child.reset_flags()
        self.is_possible = False
        self.is_implemented = False

    def add_discount(self, new_discount: _IDiscount):
        """
        adding new discount to this complex Discount
        :param new_discount: new discount to add
        :return: None
        """
        # self.children_discounts[new_discount.id] = new_discount
        # self._children_discounts = json.dumps(json.loads(self._children_discounts) + [new_discount.id])
        self.children_discounts_ls.append(new_discount.id)
        self.children_discounts_dict[new_discount.id] = new_discount
        self._dal.add(self, add_only=True)
        self._dal.flush()  # So we ill able to call .id

    def remove_discount(self, to_remove: int):
        """
        removing discount from this complex discount object
        :param to_remove:(int) id of the discount to remove
        :return: the Discount object that was removed. if it was not found, return none
        """
        if to_remove in self.children_discounts_dict:
            self.children_discounts_ls.remove(to_remove)
            output = self.children_discounts_dict.pop(to_remove)
            self._dal.add(self, add_only=True)
            self._dal.flush()  # So we ill able to call .id
            return output

        for k, discount in self.children_discounts_dict.items():
            deleted: _IDiscount = discount.remove_discount(to_remove)
            if deleted is not None:
                return deleted
        return None

    def edit_discount(self, to_edit: int, edited_discount: _IDiscount):
        """
        edit the discount of the given discount id to the given discount
        :param to_edit:(int) id of the discount to edit
        :param edited_discount: new discount to put instead
        :return: the edited discount. if it was not found, return None
        """
        for k, discount in self.children_discounts_dict.items():
            discount: _IDiscount = discount
            if discount.id == to_edit:
                if to_edit in self._children_discounts_ls:
                    self._children_discounts_ls.remove(to_edit)
                self._children_discounts_ls.append(edited_discount.id)
                del self.children_discounts_dict[to_edit]
                self._children_discounts_dict[edited_discount.id] = edited_discount
                self._dal.add(self, add_only=True)
                self._dal.flush()  # So we ill able to call .id
                return edited_discount, discount
            else:
                is_edited = discount.edit_discount(to_edit, edited_discount)
                if is_edited is not None:
                    return is_edited
        return None

    def search_for_discount(self, to_search: int):
        """
        searching a discount in the children discount collection
        :param to_search: id of the discount to search
        :return: True if found, false otherwise
        """
        children_discounts = self.children_discounts_dict
        if to_search in children_discounts:
            return children_discounts[to_search]
        for k, discount in children_discounts.items():
            discount: _IDiscount = discount
            found = discount.search_for_discount(to_search)
            if found is not None:
                return found
        return None

    @staticmethod
    def combine_discounts(list_of_discount: list, operator: str,
                          basic_condition: _IDiscountCondition = None, basic_strategy: _IDiscountStrategy = None):
        operator_type: ComplexDiscountTypes = ComplexDiscountTypes.convert_from_string(operator)
        if operator_type is None:
            raise TypeError(f"discount.py:694 -> gave a non exists operator: {operator}")
        children_discount = {d.id: d for d in list_of_discount}
        if operator_type == ComplexDiscountTypes.XOR:
            return CompositeXorDiscount(discount_condition=basic_condition, discount_strategy=basic_strategy,
                                        children_discounts=children_discount)
        elif operator_type == ComplexDiscountTypes.OR:
            return CompositeOrDiscount(discount_condition=basic_condition, discount_strategy=basic_strategy,
                                       children_discounts=children_discount)
        elif operator_type == ComplexDiscountTypes.AND:
            return CompositeAndDiscount(discount_condition=basic_condition, discount_strategy=basic_strategy,
                                        children_discounts=children_discount)

    def is_product_affected_by_discount(self, product_name: str, categories: list):
        output = []
        for k, discount in self.children_discounts_dict.items():
            discount: _IDiscount = discount
            found = discount.is_product_affected_by_discount(product_name, categories)
            if found is not None:
                output = output + found
        if not output:
            output = None
        return output


class CompositeXorDiscount(ComplexDiscount):
    __tablename__ = 'composite_xor_discount'
    __mapper_args__ = {
        'polymorphic_identity': 'composite_xor_discount'
    }

    def __init__(self, discount_condition: _IDiscountCondition, discount_strategy: _IDiscountStrategy,
                 children_discounts: dict = None):
        super().__init__(discount_condition, discount_strategy, children_discounts)
        self._operator = ComplexDiscountTypes.XOR.value

    def get_description(self):
        all_ids = ""
        all_descriptions = ""
        for discount_id, discount in self.children_discounts_dict.items():
            discount: _IDiscount = discount
            all_ids += f'{discount_id},'
            all_descriptions += f' {discount.get_description()},\n '
        return f'Only 1 discount of the following discount:{all_ids}\n{all_descriptions}\n the entire Discount properties:{super().get_description()}'

    def apply(self, basket: Basket) -> Basket:
        """
        Pick and apply the best discount from the given ones
        """
        chosen_discount: _IDiscount = None
        min_total = basket.get_total_value_of_basket()
        for discount in self.children_discounts:
            discount: _IDiscount = discount
            copy_basket: Basket = basket.copy()
            copy_basket = discount.apply(copy_basket)
            current_total = copy_basket.get_total_value_of_basket()
            if min_total > current_total:
                chosen_discount = discount
                min_total = current_total
        if chosen_discount is not None:
            basket = chosen_discount.apply(basket)
            return self.basic_discount_application(basket)
        return basket


class CompositeOrDiscount(ComplexDiscount):
    __tablename__ = 'composite_or_discount'
    __mapper_args__ = {
        'polymorphic_identity': 'composite_or_discount'
    }

    def __init__(self, discount_condition: _IDiscountCondition, discount_strategy: _IDiscountStrategy,
                 children_discounts: dict = None):
        super().__init__(discount_condition, discount_strategy, children_discounts)
        self._operator = ComplexDiscountTypes.OR.value

    def get_description(self):
        all_ids = ""
        all_descriptions = ""
        for discount_id, discount in self.children_discounts_dict.items():
            discount: _IDiscount = discount
            all_ids += f'{discount_id},'
            all_descriptions += f' {discount.get_description()},\n '
        return f'Any one of the following discounts:{all_ids}\n{all_descriptions}\n the entire Discount properties:{super().get_description()}'

    def apply(self, basket: Basket) -> Basket:
        """
        apply all the possible discounts from the list
        """
        chosen_discounts: list = []
        for k, d in self.children_discounts_dict.items():
            d: _IDiscount = d
            if d.discount_condition.check_condition(basket):
                chosen_discounts.append(d)
        if not len(chosen_discounts) == 0:
            for d in chosen_discounts:
                basket = d.discount_strategy.activate_discount(basket)
            self.basic_discount_application(basket)
        return basket


class CompositeAndDiscount(ComplexDiscount):
    __tablename__ = 'composite_and_discount'
    __mapper_args__ = {
        'polymorphic_identity': 'composite_and_discount'
    }

    def __init__(self, discount_condition: _IDiscountCondition, discount_strategy: _IDiscountStrategy,
                 children_discounts: dict = None):
        super().__init__(discount_condition, discount_strategy, children_discounts)
        self._operator = ComplexDiscountTypes.AND.value

    def get_description(self):

        all_ids = ""
        all_descriptions = ""
        for discount_id, discount in self.children_discounts_dict.items():
            discount: _IDiscount = discount
            all_ids += f'{discount_id},'
            all_descriptions += f' {discount.get_description()},\n '
        return f'ALL of the following discount conditions must be answered:{all_ids}\n{all_descriptions}\n the entire Discount properties:{super().get_description()}'

    def apply(self, basket: Basket) -> Basket:
        """
        apply all the possible discounts from the list
        """
        chosen_discounts: list = []
        for d in self.children_discounts_dict:
            d: _IDiscount = d
            if d.discount_condition.check_condition(basket):
                chosen_discounts.append(d)
            else:
                return basket
        if not len(chosen_discounts) == 0:
            for d in chosen_discounts:
                basket = d.discount_strategy.activate_discount(basket)
            self.basic_discount_application(basket)
        return basket

# print()
# REGULAR_USER_ID = 4
# STORE_MANAGER_USER_ID = 3
# USER_MAIL_2 = "user2@user2.mail"
# STORE_MANAGER = 'store_manager'
# STORE_NAME_1 = "ShuferSal"
# PASSWORD = 'Shani123!'
# PASSWORD = Encrypter.hash_password(PASSWORD)
# OWNER_NAME = "store_owner"
#
# data_handler: DataHandler = DataHandler().get_instance()
# _users_handler: UserSystemHandler = UserSystemHandler(data_handler)
# _users_handler.register_user(1, "root_user", '!fldmAd12s', "root@root.com")
# _users_handler.login_user(1)
# _store_administrator: StoreAdministration = StoreAdministration(data_handler, MockSupplySystem())
# _shopping_handler: ShoppingHandler = ShoppingHandler(data_handler, MockPaymentSystem())
# _admin_handler: SystemAdmin = SystemAdmin(data_handler)
#
# user3 = User(STORE_MANAGER_USER_ID, ShoppingCart())
# user3.user_state = LoggedInUser(STORE_MANAGER, PASSWORD, USER_MAIL_2)
# user4 = User(REGULAR_USER_ID, ShoppingCart())
# data_handler.add_or_update_user(REGULAR_USER_ID, user4)
# user3.user_state.is_connected = True
# data_handler.add_or_update_user(STORE_MANAGER_USER_ID, user3)
#
# # Store
# store1 = Store(STORE_NAME_1, OWNER_NAME)
#
# # Add store to data handler
# data_handler.add_store(store1)
#
# # Add product to this store
# assert store1.add_product(OWNER_NAME, "Milk 1%", 14.0, 50)
# assert store1.add_product(OWNER_NAME, "Bred", 14.0, 50)
# assert store1.add_product(OWNER_NAME, "Meat", 24.0, 50)
# assert store1.add_product(OWNER_NAME, "Oat meal", 14.0, 50)
#
# # Now the user adds this product to his shopping cart
# assert _shopping_handler.saving_product_to_shopping_cart("Milk 1%", STORE_NAME_1, user3.user_id, 1).succeed
#
# # Make the purchase
# assert _shopping_handler.make_purchase_of_all_shopping_cart(user3.user_id, 1111111111111111).succeed
#
# now = datetime.now()
# upTo = now + timedelta(days=0, hours=1)
# upTo2 = now + timedelta(days=0, hours=0, minutes=30)
#
#
# def discount_function(p):
#     print(type(p))
#
#
# an_d = CompositeAndDiscount()
# an_d.add_discount(LeafDiscount(upTo, ProductInShoppingCart()))
#
# if __name__ == '__main__':
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
#     # https://flask-sqlalchemy.palletsprojects.com/en/2.x/signals/
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     # To see the queries that are being run
#     # app.config['SQLALCHEMY_ECHO'] = True
#     db.init_app(app)
#     with app.app_context():
#         db.create_all()
# # The following commented was tested
# s.add_all([
#     ProductDiscountStrategy(0.3, "phone"),
#     BasketDiscountStrategy(0.6),
#     FreePerXCategoryDiscountStrategy("Home Products", 1, 3, False),
#     ProductDiscountStrategy(0.5, "rocket"),
#     FreePerXProductDiscountStrategy("ring", 1, 3, True),
#     CategoryDiscountStrategy(0.5, "Boats"), ])
# s.commit()
#
# for p in s.query(_IDiscountStrategy):
#     print("=============================")
#     if isinstance(p, ProductDiscountStrategy):
#         print("Product Discount")
#         print(p.discounted_product)
#     elif isinstance(p, BasketDiscountStrategy):
#         print("Basket Discount Strategy")
#         print(p.discount_percent)
#     elif isinstance(p, CategoryDiscountStrategy):
#         print("Category Discount")
#         print(p.discounted_category)
#     elif isinstance(p, FreePerXProductDiscountStrategy):
#         print("Free Per X Product")
#         print(f'{p.free_amount}, {p.per_x_amount}, {p.product}')
#     elif isinstance(p, FreePerXCategoryDiscountStrategy):
#         print("Free Per X Category")
#         print(f'{p.free_amount}, {p.per_x_amount}, {p.category}')
#     else:
#         print('Type unknown')
#     print("=============================")
#
#
# s.add_all([
#
#     _IDiscountCondition(datetime.now() + timedelta(days=0, hours=0, minutes=30)),
#
#     _IDiscountCondition(datetime.now() + timedelta(days=0, hours=5, minutes=15)),
#
#     DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=5, minutes=15),
#         5,
#         [CategoryToNeededPrice("cat1", 5.7), CategoryToNeededPrice("cat2", 6.5)],
#         [ProductToNeededPrice("bake", 3.3), ProductToNeededPrice("wow", 4.6)],
#         [ProductToQuantity("water", 3), ProductToQuantity("bred", 5)],
#         [CategoryToNeededItems("cat1", 4), CategoryToNeededItems("cat2", 6)]),
#
#     DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=3, minutes=45),
#         0,
#         [CategoryToNeededPrice("cat1", 3.7), CategoryToNeededPrice("cat2", 6.2)],
#         [ProductToNeededPrice("bake", 1.3), ProductToNeededPrice("wow", 3.6)],
#         [ProductToQuantity("water", 2), ProductToQuantity("bred", 1)],
#         [CategoryToNeededItems("cat1", 7), CategoryToNeededItems("cat2", 2)]),
# ])
# s.commit()
#
# for p in s.query(DiscountConditionCombo):
#     print("=============================")
#     # Note that here, the order we check isinstance is important
#     # because DiscountConditionCombo inherit from _IDiscountCondition
#     print("Discount Condition Combo")
#     print(p.size_of_basket_cond)
#     print(p.product_list_cond)
#     print(p.over_all_price_product_cond)
#     print(p.overall_category_quantity)
#     print(p.over_all_price_category_cond)
#     print(p.end_time)
#     print("=============================")
#
#
# # Insert prerequesit objects
# s1 = ProductDiscountStrategy(0.3, "phone")
# d1 = DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=3, minutes=45),
#         0,
#         [CategoryToNeededPrice("cat1", 3.7), CategoryToNeededPrice("cat2", 6.2)],
#         [ProductToNeededPrice("bake", 1.3), ProductToNeededPrice("wow", 3.6)],
#         [ProductToQuantity("water", 2), ProductToQuantity("bred", 1)],
#         [CategoryToNeededItems("cat1", 7), CategoryToNeededItems("cat2", 2)])
#
# s.add_all([s1,d1])
# s.commit()
#
# s.add_all([
#     _IDiscount(d1, s1)
# ])
# s.commit()
#
# # Eventually, with a clean database I expect 4 iterations.
# for p in s.query(_IDiscount):
#     print("=============================")
#     print("Discount Condition Combo")
#     print(p.discount_condition)
#     print(p.discount_condition.over_all_price_product_cond)
#     print(p.discount_strategy)
#     print(p.discount_strategy.discount_percent)
#     print("=============================")
#
# comp1 = ComplexDiscount(
#         DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=5, minutes=15),
#         5,
#         [CategoryToNeededPrice("cat1", 5.7), CategoryToNeededPrice("cat2", 6.5)],
#         [ProductToNeededPrice("bake", 3.3), ProductToNeededPrice("wow", 4.6)],
#         [ProductToQuantity("water", 3), ProductToQuantity("bred", 5)],
#         [CategoryToNeededItems("cat1", 4), CategoryToNeededItems("cat2", 6)]),
#         FreePerXCategoryDiscountStrategy("Home Products", 1, 3, False),
#         {}
#     )
#
# comp2 = ComplexDiscount(
#         DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=5, minutes=15),
#         5,
#         [CategoryToNeededPrice("abcdefg", 5.7), CategoryToNeededPrice("abcdefg", 6.5)],
#         [ProductToNeededPrice("abcdefg", 3.3), ProductToNeededPrice("abcdefg", 4.6)],
#         [ProductToQuantity("abcdefg", 3), ProductToQuantity("abcdefg", 5)],
#         [CategoryToNeededItems("abcdefg", 4), CategoryToNeededItems("abcdefg", 6)]),
#         FreePerXCategoryDiscountStrategy("abcdefg", 1, 3, False),
#         {}
#     )
#
# d.add_all([
#     comp1,
#     comp2
# ])
# d.commit()
#
#
#
# comp3 = CompositeAndDiscount(
#     DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=5, minutes=15),
#         5,
#         [CategoryToNeededPrice("cat1", 5.7), CategoryToNeededPrice("cat2", 6.5)],
#         [ProductToNeededPrice("bake", 3.3), ProductToNeededPrice("wow", 4.6)],
#         [ProductToQuantity("water", 3), ProductToQuantity("bred", 5)],
#         [CategoryToNeededItems("cat1", 4), CategoryToNeededItems("cat2", 6)]),
#     FreePerXCategoryDiscountStrategy("Home Products", 1, 3, False),
#     {
#         # comp1.id: comp1,
#         comp2.id: comp2
#     }
# )
#
# d.add_all([
#     comp3
# ])
# d.commit()
#
# base_discount = _IDiscount(
#     DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=5, minutes=15),
#         5,
#         [CategoryToNeededPrice("cat1", 5.7), CategoryToNeededPrice("cat2", 6.5)],
#         [ProductToNeededPrice("bake", 3.3), ProductToNeededPrice("wow", 4.6)],
#         [ProductToQuantity("water", 3), ProductToQuantity("bred", 5)],
#         [CategoryToNeededItems("cat1", 4), CategoryToNeededItems("cat2", 6)]),
#     FreePerXCategoryDiscountStrategy("Home Products", 1, 3, False)
# )
#
# d.add_all([
#     base_discount
# ])
# d.commit()
#
# comp5 = CompositeOrDiscount(
#     DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=5, minutes=15),
#         5,
#         [CategoryToNeededPrice("cat1", 5.7), CategoryToNeededPrice("cat2", 6.5)],
#         [ProductToNeededPrice("bake", 3.3), ProductToNeededPrice("wow", 4.6)],
#         [ProductToQuantity("water", 3), ProductToQuantity("bred", 5)],
#         [CategoryToNeededItems("cat1", 4), CategoryToNeededItems("cat2", 6)]),
#     FreePerXCategoryDiscountStrategy("Home Products", 1, 3, False),
#     {
#         base_discount.id: base_discount,
#         comp3.id: comp3
#     }
# )
#
# d.add_all([
#     comp5
# ])
#
# d.commit()
#
# comp6 = CompositeXorDiscount(
#     DiscountConditionCombo(
#         datetime.now() + timedelta(days=0, hours=5, minutes=15),
#         5,
#         [CategoryToNeededPrice("cat1", 5.7), CategoryToNeededPrice("cat2", 6.5)],
#         [ProductToNeededPrice("bake", 3.3), ProductToNeededPrice("wow", 4.6)],
#         [ProductToQuantity("water", 3), ProductToQuantity("bred", 5)],
#         [CategoryToNeededItems("cat1", 4), CategoryToNeededItems("cat2", 6)]),
#     FreePerXCategoryDiscountStrategy("Home Products", 1, 3, False),
#     {
#         base_discount.id: base_discount,
#         comp3.id: comp3,
#         comp5.id: comp5
#     }
# )
#
# d.add_all([
#     comp6
# ])
#
# d.commit()
#
#
# print("==============ComplexDiscount===============")
# for p in d.query(ComplexDiscount):
#     print('---------------------------------')
#     print(p.children_discounts)
#     print('---------------------------------')
#
# print("=============================")
#
# print("==============CompositeAndDiscount===============")
# for p in d.query(CompositeAndDiscount):
#     print('---------------------------------')
#     print(p.children_discounts)
#     print('---------------------------------')
# print("=============================")
#
# print("=============CompositeOrDiscount================")
# for p in d.query(CompositeOrDiscount):
#     print('---------------------------------')
#     print(p.children_discounts)
#     print('---------------------------------')
# print("=============================")
#
# print("=============CompositeXorDiscount1================")
# for p in d.query(CompositeXorDiscount):
#     print('---------------------------------')
#     print(p.children_discounts)
#     p.add_discount(comp2)
#     d.add(p)
#     print('---------------------------------')
# print("=============================")
# d.commit()
# print("=============CompositeXorDiscount2================")
# for p in d.query(CompositeXorDiscount):
#     print('---------------------------------')
#     print(p.children_discounts)
#     p.remove_discount(comp2.id)
#     d.add(p)
#     print('---------------------------------')
# print("=============================")
# d.commit()
# print("=============CompositeXorDiscount3================")
# for p in d.query(CompositeXorDiscount):
#     print('---------------------------------')
#     print(p.children_discounts)
#     print('---------------------------------')
# print("=============================")
# print("=============CompositeXorDiscount4================")
# for p in d.query(CompositeXorDiscount):
#     print('---------------------------------')
#     p.edit_discount(comp2.id, comp1)
#     d.add(p)
#     print('---------------------------------')
# print("=============================")
# d.commit()
# print("=============CompositeXorDiscount3================")
# for p in d.query(CompositeXorDiscount):
#     print('---------------------------------')
#     print(p.children_discounts)
#     print('---------------------------------')
# print("=============================")
