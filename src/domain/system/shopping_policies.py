from __future__ import annotations

import enum
import json
import os
import calendar
from dataclasses import dataclass
from typing import TYPE_CHECKING

from datetime import datetime, timedelta, date
from functools import reduce

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event, orm
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.mutable import MutableDict, MutableList

from src.domain.system.DAL import DAL
from src.protocol_classes.classes_utils import TypeChecker, TypedDict

if TYPE_CHECKING:
    from src.domain.system.cart_purchase_classes import Basket, ProductInShoppingCart
    from src.domain.system.products_classes import ProductInInventory

from src.domain.system.db_config import db


class IShoppingPolicies(db.Model):
    __tablename__ = 'shopping_policy'
    _dal: DAL = DAL.get_instance()

    id = db.Column(db.Integer, primary_key=True)
    policy_type = db.Column(db.VARCHAR(40))
    __mapper_args__ = {
        'polymorphic_identity': 'shopping_policy',
        'polymorphic_on': policy_type
    }

    def edit_policy(self, to_edit: int, edited_policy: IShoppingPolicies):
        if to_edit == self.id:
            return edited_policy, self
        return None  # if the id doesn't match

    def apply(self, basket: Basket) -> bool:
        pass

    def give_stuff_to_delete(self):
        return []

    def delete_yourself(self):
        self._dal.delete(self, del_only=True)

    @staticmethod
    def create_specific_leaf(min_basket_quantity: int, max_basket_quantity: int, product_name: str,
                             min_product_quantity: int,
                             max_product_quantity: int, category: str, min_category_quantity: int,
                             max_category_quantity: int, day: str):
        children = None
        if min_basket_quantity is not None or max_basket_quantity is not None:
            children = LeafBasketQuantity(min_basket_quantity, max_basket_quantity, product_name,
                                          min_product_quantity, max_product_quantity, category,
                                          min_category_quantity, max_category_quantity, day)

        if (product_name is not None) and (min_product_quantity is not None or max_product_quantity is not None):
            children = LeafSpecificProductQuantity(min_basket_quantity, max_basket_quantity, product_name,
                                                   min_product_quantity, max_product_quantity, category,
                                                   min_category_quantity, max_category_quantity, day)

        if (category is not None) and (min_category_quantity is not None or max_category_quantity is not None):
            children = LeafSpecificCategoryQuantity(min_basket_quantity, max_basket_quantity, product_name,
                                                    min_product_quantity, max_product_quantity, category,
                                                    min_category_quantity, max_category_quantity, day)

        if day != "":
            children = LeafShoppingDateTime(min_basket_quantity, max_basket_quantity, product_name,
                                            min_product_quantity, max_product_quantity, category,
                                            min_category_quantity, max_category_quantity, day)

        return children

    def refresh_self(self):
        # try:
        #     self._dal._db_session.add(self)
        #     self._dal._db_session.refresh(self)
        # except:
        #     pass
        pass

    def description(self):
        pass

    def is_product_has_shopping_policies(self, product_name, categories):
        return None

    def fetch_policies(self):
        return []


class LeafProductPolicy(IShoppingPolicies):
    __tablename__ = 'leaf_product_policy'
    id = db.Column(db.Integer, db.ForeignKey('shopping_policy.id'), primary_key=True)
    # leaf_product_policy_type = db.Column(db.VARCHAR(length=40))
    min_basket_quantity = db.Column(db.Integer)
    max_basket_quantity = db.Column(db.Integer)
    product_name = db.Column(db.String(50))
    min_product_quantity = db.Column(db.Integer)
    max_product_quantity = db.Column(db.Integer)
    category = db.Column(db.String(50))
    min_category_quantity = db.Column(db.Integer)
    max_category_quantity = db.Column(db.Integer)
    day = db.Column(db.String(50))
    __mapper_args__ = {
        # 'polymorphic_on': leaf_product_policy_type,
        'polymorphic_identity': 'leaf_product_policy'
    }

    def __init__(self, min_basket_quantity: int, max_basket_quantity: int, product_name: str, min_product_quantity: int,
                 max_product_quantity: int, category: str, min_category_quantity: int, max_category_quantity: int,
                 day: str):
        super().__init__()
        self.min_basket_quantity = min_basket_quantity
        self.max_basket_quantity = max_basket_quantity
        self.product_name = product_name
        self.min_product_quantity = min_product_quantity
        self.max_product_quantity = max_product_quantity
        self.category = category
        self.min_category_quantity = min_category_quantity
        self.max_category_quantity = max_category_quantity
        self.day = day

    def edit_policy(self, to_edit: int, edited_policy: IShoppingPolicies):
        if to_edit == self.id:
            return edited_policy, self
        return None  # if the id doesn't match

    def search_for_policy(self, to_search: int):
        return False

    def apply(self, basket: Basket) -> bool:
        pass

    def is_product_has_shopping_policies(self, product_name, categories):
        return None

    def relevant_categories_and_products(self):
        return [], []


class LeafBasketQuantity(LeafProductPolicy):
    __tablename__ = 'leaf_basket_quantity'
    __mapper_args__ = {
        'polymorphic_identity': 'leaf_basket_quantity'
    }

    def __init__(self, min_basket_quantity: int, max_basket_quantity: int, product_name: str, min_product_quantity: int,
                 max_product_quantity: int, category: str, min_category_quantity: int, max_category_quantity: int,
                 day: str):

        super().__init__(min_basket_quantity, max_basket_quantity, product_name, min_product_quantity,
                         max_product_quantity, category, min_category_quantity, max_category_quantity, day)

    def apply(self, basket: Basket) -> bool:
        min_answer: bool = True
        max_answer: bool = True
        basket_quantity = reduce(lambda acc, product: acc + product._product_quantity, basket.products.values(), 0)

        if self.min_basket_quantity is not None and basket_quantity < self.min_basket_quantity:
            min_answer = False
        if self.max_basket_quantity is not None and basket_quantity > self.max_basket_quantity:
            max_answer = False
        return min_answer and max_answer

    def description(self):
        self.refresh_self()
        if self.min_basket_quantity is not None and self.max_basket_quantity is not None:
            desc = "basket quantity is at least " + str(self.min_basket_quantity) + " and at most " + \
                   str(self.max_basket_quantity)
            return desc
        if self.min_basket_quantity is not None:
            desc = "basket quantity is at least " + str(self.min_basket_quantity)
            return desc
        else:
            desc = "basket quantity is at most " + str(self.max_basket_quantity)
            return desc

    def is_product_has_shopping_policies(self, product_name, categories):
        return [self]

    def relevant_categories_and_products(self):
        return [], []


class LeafSpecificProductQuantity(LeafProductPolicy):
    __tablename__ = 'leaf_specific_product_quantity'
    __mapper_args__ = {
        'polymorphic_identity': 'leaf_specific_product_quantity'
    }

    def __init__(self, min_basket_quantity: int, max_basket_quantity: int, product_name: str, min_product_quantity: int,
                 max_product_quantity: int, category: str, min_category_quantity: int, max_category_quantity: int,
                 day: str):
        super().__init__(min_basket_quantity, max_basket_quantity, product_name, min_product_quantity,
                         max_product_quantity, category, min_category_quantity, max_category_quantity, day)

    def apply(self, basket: Basket) -> bool:
        # check if product exist in basket
        if self.product_name in basket.products:
            product: ProductInShoppingCart = basket.products[self.product_name]
            min_answer: bool = True
            max_answer: bool = True
            if self.min_product_quantity is not None and product._product_quantity < self.min_product_quantity:
                min_answer = False
            if self.max_product_quantity is not None and product._product_quantity > self.max_product_quantity:
                max_answer = False
            return min_answer and max_answer
        else:
            return True

    def description(self):
        self.refresh_self()
        if self.min_product_quantity is not None and self.max_product_quantity is not None:
            desc = "The product " + self.product_name + " quantity is at least " + str(self.min_product_quantity) \
                   + " and at most " + str(self.max_product_quantity)
            return desc
        if self.min_product_quantity is not None:
            desc = "The product " + self.product_name + " quantity is at least " + str(self.min_product_quantity)
            return desc
        else:
            desc = "The product " + self.product_name + " quantity is at most " + str(self.max_product_quantity)
            return desc

    def is_product_has_shopping_policies(self, product_name, categories):
        if self.product_name == product_name:
            return [self]
        else:
            return None

    def relevant_categories_and_products(self):
        return [], [self.product_name]


class LeafSpecificCategoryQuantity(LeafProductPolicy):
    __tablename__ = 'leaf_specific_category_quantity'
    __mapper_args__ = {
        'polymorphic_identity': 'leaf_specific_category_quantity'
    }

    def __init__(self, min_basket_quantity: int, max_basket_quantity: int, product_name: str, min_product_quantity: int,
                 max_product_quantity: int, category: str, min_category_quantity: int, max_category_quantity: int,
                 day: str):
        super().__init__(min_basket_quantity, max_basket_quantity, product_name, min_product_quantity,
                         max_product_quantity, category, min_category_quantity, max_category_quantity, day)

    def apply(self, basket: Basket) -> bool:
        quantity_of_category = basket.get_total_quantity_of_category(self.category)
        if quantity_of_category > 0:
            min_answer: bool = True
            max_answer: bool = True
            if self.min_category_quantity is not None and quantity_of_category < self.min_category_quantity:
                min_answer = False
            if self.max_category_quantity is not None and quantity_of_category > self.max_category_quantity:
                max_answer = False
            return min_answer and max_answer
        else:
            return True

    def description(self):
        self.refresh_self()
        if self.min_category_quantity is not None and self.max_category_quantity is not None:
            desc = "The Category " + self.category + " quantity is at least " + str(self.min_category_quantity) \
                   + " and at most " + str(self.max_category_quantity)
            return desc
        if self.min_category_quantity is not None:
            desc = "The Category " + self.category + " quantity is at least " + str(self.min_category_quantity)
            return desc
        else:
            desc = "The Category " + self.category + " quantity is at most " + str(self.max_category_quantity)
            return desc

    def is_product_has_shopping_policies(self, product_name, categories):
        if self.category in categories:
            return [self]
        else:
            return None

    def relevant_categories_and_products(self):
        return [self.category], []


class LeafShoppingDateTime(LeafProductPolicy):
    __tablename__ = 'leaf_shopping_date_time'
    __mapper_args__ = {
        'polymorphic_identity': 'leaf_shopping_date_time'
    }

    def __init__(self, min_basket_quantity: int, max_basket_quantity: int, product_name: str, min_product_quantity: int,
                 max_product_quantity: int, category: str, min_category_quantity: int, max_category_quantity: int,
                 day: str):
        super().__init__(min_basket_quantity, max_basket_quantity, product_name, min_product_quantity,
                         max_product_quantity, category, min_category_quantity, max_category_quantity, day)

    def apply(self, basket: Basket) -> bool:
        temp = calendar.day_name[date.today().weekday()]
        return temp != self.day

    def description(self):
        self.refresh_self()
        return "Shopping is not allowed at " + self.day

    def is_product_has_shopping_policies(self, product_name, categories):
        return None

    def relevant_categories_and_products(self):
        return [], []


class ComplexPolicyTypes(enum.Enum):
    XOR = 1
    OR = 2
    AND = 3

    def to_string(self):
        if self == ComplexPolicyTypes.XOR:
            return "XOR"
        elif self == ComplexPolicyTypes.OR:
            return "OR"
        elif self == ComplexPolicyTypes.AND:
            return "AND"
        else:
            return None

    @staticmethod
    def convert_from_string(to_convert: str):
        to_convert = to_convert.upper()
        if to_convert.upper() == "XOR":
            return ComplexPolicyTypes.XOR
        elif to_convert.upper() == "OR":
            return ComplexPolicyTypes.OR
        elif to_convert.upper() == "AND":
            return ComplexPolicyTypes.AND
        else:
            return None


class ICompositePolicy(IShoppingPolicies):
    __tablename__ = 'i_composite_policy'
    id = db.Column(db.Integer, db.ForeignKey('shopping_policy.id'), primary_key=True)
    # composite_type = db.Column(db.VARCHAR(length=40))
    _shop_policies_ls = db.Column(MutableList.as_mutable(db.JSON))
    _operator = db.Column(db.Integer)
    __mapper_args__ = {
        # 'polymorphic_on': composite_type,
        'polymorphic_identity': 'i_composite_policy'
    }

    def __init__(self):
        super().__init__()
        self._shop_policies_ls = []
        self.shop_policies_dict = TypedDict(int, IShoppingPolicies)

    def edit_policy(self, to_edit: int, edited_policy: IShoppingPolicies):

        for k, policy in self.shop_policies_dict.items():
            policy: IShoppingPolicies = policy
            if policy.id == to_edit:
                if to_edit in self._shop_policies_ls:
                    self._shop_policies_ls.remove(to_edit)
                self._shop_policies_ls.append(edited_policy.id)
                del self.shop_policies_dict[to_edit]
                self.shop_policies_dict[edited_policy.id] = edited_policy
                self._dal.add(self, add_only=True)
                self._dal.flush()  # So we ill able to call .id
                return edited_policy, policy
            else:
                is_edited = policy.edit_policy(to_edit, edited_policy)
                if is_edited is not None:
                    return is_edited
        return None

    def give_stuff_to_delete(self):
        to_delete = []
        for k, child in self.shop_policies_dict.items():
            child: IShoppingPolicies = child
            to_delete.extend(child.give_stuff_to_delete())
            to_delete.append(child)
        to_delete.append(self)
        return to_delete

    def delete_yourself(self):
        self._dal.delete_all(self.give_stuff_to_delete(), del_only=True)

    @property
    def shop_policies_ls(self):
        return self._shop_policies_ls

    @shop_policies_ls.setter
    def shop_policies_ls(self, new_shop_policies_ls: list):
        if new_shop_policies_ls is None:
            self._shop_policies_ls = list()
        if isinstance(new_shop_policies_ls, list):
            self._shop_policies_ls = new_shop_policies_ls
        else:
            raise TypeError(
                f"discount: expected list of int or None, got {type(new_shop_policies_ls)}")

    @property
    def shop_policies_dict(self):
        return self._shop_policies_dict

    @shop_policies_dict.setter
    def shop_policies_dict(self, new_shop_policies_dict: TypedDict):
        if new_shop_policies_dict is None:
            self._shop_policies_dict = TypedDict(int, IShoppingPolicies)
        if isinstance(new_shop_policies_dict, TypedDict) and new_shop_policies_dict.check_types(int, IShoppingPolicies):
            self._shop_policies_dict = new_shop_policies_dict
        else:
            raise TypeError(
                f"discount: expected TypedDict of int to _IDiscount or None, got {type(new_shop_policies_dict)}")

    @orm.reconstructor
    def _init_on_load(self):
        self._shop_policies_dict = self._dal.get_policy_map_with_id_keys(self._shop_policies_ls)

    def apply(self, basket: Basket) -> bool:
        pass

    def add_policy(self, policy: IShoppingPolicies):
        """
        Add policy as a child.
        """
        self._shop_policies_ls.append(policy.id)
        self.shop_policies_dict[policy.id] = policy
        self._dal.add(self, add_only=True)
        self._dal.flush()  # So we ill able to call .id

    def remove_policy(self, to_remove: int):
        """
        removing policy from this complex discount object
        :param to_remove:(int) id of the policy to remove
        :return: the Policy object that was removed. if it was not found, return none
        """
        shop_policies = self.shop_policies_dict
        if to_remove in self._shop_policies_ls:
            self._shop_policies_ls.remove(to_remove)
            self._dal.add(self, add_only=True)
            self._dal.flush()  # So we ill able to call .id
            output = shop_policies.pop(to_remove)
            return output

        for k, policy in shop_policies.items():
            if policy.search_for_policy(to_remove):
                return policy.remove_policy(to_remove)
        return None

    def search_for_policy(self, to_search: int):
        """
        searching a discount in the children discount collection
        :param to_search: id of the discount to search
        :return: True if found, false otherwise
        """
        shop_policies = self.shop_policies_dict
        if to_search in shop_policies:
            return True
        for k, policy in shop_policies.items():
            if policy.search_for_policy(to_search):
                return True
            return False

    @staticmethod
    def create_composite_policies(children_policies: list, operator: str):
        operator_type: ComplexPolicyTypes = ComplexPolicyTypes.convert_from_string(operator)
        if operator_type is None:
            raise TypeError(f" gave a non exists operator: {operator}")
        if operator_type == ComplexPolicyTypes.AND:
            composite_res = CompositeAndShoppingPolicy()
        elif operator_type == ComplexPolicyTypes.OR:
            composite_res = CompositeOrShoppingPolicy()
        else:
            composite_res = CompositeXORShoppingPolicy()
        composite_res.add_policies(children_policies)
        return composite_res

    def add_policies(self, policies):
        for policy in policies:
            self._shop_policies_ls.append(policy.id)
            self.shop_policies_dict[policy.id] = policy
        self._dal.add(self)

    def fetch_policies(self):
        policies = []
        shop_policies = self.shop_policies_dict
        for p_id, policy in shop_policies.items():
            policy: IShoppingPolicies = policy
            policies.append(policy)
            policies.extend(policy.fetch_policies())

        return policies

    def is_product_has_shopping_policies(self, product_name, categories):
        ret_policies = []
        shop_policies = self.shop_policies_dict
        for i, policy in shop_policies.items():
            policy = policy.is_product_has_shopping_policies(product_name, categories)
            if policy is not None:
                ret_policies = ret_policies + policy
        if len(ret_policies) == 0:
            return None
        return ret_policies


class CompositeAndShoppingPolicy(ICompositePolicy):
    __tablename__ = 'composite_and_shopping_policy'
    __mapper_args__ = {
        'polymorphic_identity': 'composite_and_shopping_policy'
    }

    def __init__(self):
        super().__init__()
        self._operator = ComplexPolicyTypes.AND.value

    def apply(self, basket: Basket) -> bool:
        """
        apply all policies if all children policies conditions
        are satisfied.
        """
        # return reduce(lambda a, b: a.apply(basket) & b.apply(basket), self._shop_policies_ls, True)
        valid = True
        for b in self.shop_policies_dict.values():
            res = b.apply(basket)
            valid = valid and res
        return valid
        # return reduce(lambda a, b: a and b.apply(basket), self.shop_policies_dict.values(), True)

    def description(self):
        self.refresh_self()

        ids = ""
        desc = ""
        for p_id, policy in self.shop_policies_dict.items():
            policy: IShoppingPolicies = policy
            ids += f'{policy.id},'
            desc += f'{policy.description()},\n '
        return f'ALL of the following policies must be answered:{ids}\n{desc}\n'


class CompositeOrShoppingPolicy(ICompositePolicy):
    __tablename__ = 'composite_or_shopping_policy'
    __mapper_args__ = {
        'polymorphic_identity': 'composite_or_shopping_policy'
    }

    def __init__(self):
        super().__init__()
        self._operator = ComplexPolicyTypes.OR.value

    def apply(self, basket: Basket) -> bool:
        """
        apply all policies
        """
        valid = False
        for b in self.shop_policies_dict.values():
            res = b.apply(basket)
            valid = valid or res
        return valid
        # return reduce(lambda a, b: a or b.apply(basket), self.shop_policies_dict.values(), False)

    def description(self):
        self.refresh_self()

        ids = ""
        desc = ""
        for p_id, policy in self.shop_policies_dict.items():
            policy: IShoppingPolicies = policy
            ids += f'{policy.id},'
            desc += f'{policy.description()},\n '
        return f'At least one of the following policies must be answered:{ids}\n{desc}\n'


class CompositeXORShoppingPolicy(ICompositePolicy):
    __tablename__ = 'composite_xor_shopping_policy'
    __mapper_args__ = {
        'polymorphic_identity': 'composite_xor_shopping_policy'
    }

    def __init__(self):
        super().__init__()
        self._operator = ComplexPolicyTypes.XOR.value

    def apply(self, basket: Basket) -> bool:
        temp = False
        for policy in self.shop_policies_dict.values():
            res = policy.apply(basket)
            if temp and res:
                return False
            else:
                temp = res or temp
        return temp

    def description(self):
        self.refresh_self()

        ids = ""
        desc = ""
        for p_id, policy in self.shop_policies_dict.items():
            policy: IShoppingPolicies = policy
            ids += f'{policy.id},'
            desc += f'{policy.description()},\n '
        return f'Only one of the following policies must be answered:{ids}\n{desc}\n '
