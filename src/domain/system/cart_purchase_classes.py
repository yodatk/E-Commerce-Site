from __future__ import annotations

import enum
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import orm

from src.domain.system.DAL import DAL
from src.logger.log import Log

if TYPE_CHECKING:
    from src.domain.system.store_classes import Store
from src.domain.system.products_classes import ProductInInventory
from src.protocol_classes.classes_utils import TypeChecker, Result, TypedDict, TypedList

from sqlalchemy.ext.mutable import MutableList, MutableDict
from src.domain.system.db_config import db


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


# String Constants
# CASCADE = 'CASCADE'
#
# db: SQLAlchemy = SQLAlchemy()
# # db: SQLAlchemy = DAL.get_instance().get_db()
# project_directory = os.getcwd()
# db_name = 'db'
# db_path = f'{project_directory}/{db_name}.db'


class Item:
    def __init__(self, quantity, categories, name, price):
        self.quantity = quantity
        self.categories = categories
        self.product_name = name
        self.price = price

# @dataclass()
class ProductInShoppingCart(db.Model):
    """
    class represents an item in shopping cart
    """

    __tablename__ = 'product_in_shopping_cart'
    _dal: DAL = DAL.get_instance()
    id = db.Column(db.Integer, primary_key=True)
    _total_price = db.Column(db.Float)
    _product_quantity = db.Column(db.Integer)
    # _product_id = db.Column(db.Integer)
    _product_data = db.Column(MutableDict.as_mutable(db.JSON))

    _basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'))

    # item: ProductInInventory
    # total_price: float = None

    def __init__(self, total_price, item, basket_id, product_quantity: int):
        if not isinstance(item, ProductInInventory):
            raise TypeError("Not a valid ProductInInventory")
        self._item = item
        # self._product_id = item.id

        self._product_name = item.product.name
        self._product_quantity = product_quantity
        data_dict = dict()
        data_dict["store_name"] = item.store_name
        data_dict["price"] = item.price
        for k, v in item.product.to_dictionary().items():
            data_dict[k] = v
        self._product_data = data_dict
        if total_price is None:
            self._total_price = self._item.price * self._item.quantity
        elif TypeChecker.check_for_positive_number([total_price]):
            self._total_price = total_price
        else:
            raise TypeError("Not a valid total_price")
        if TypeChecker.check_for_positive_number([basket_id]):
            self._basket_id = basket_id
        self._item = Item(self._product_quantity, self._product_data.get('categories', []), self._product_name, self._product_data.get('price', 1))

    @property
    def item(self):
        return Item(self._product_quantity, self._product_data.get('categories', []), self._product_name, self._product_data.get('price', 1))


    def update_total_price(self, new_price: float = None):
        self._total_price = self.item.price * self._product_quantity if new_price is None else new_price

    def to_dictionary(self):
        return {'product': self._product_data, 'total_price': round(self._total_price, 2),
                'quantity': self._product_quantity}

    # def copy(self):
    #     return ProductInShoppingCart(self._item.copy(), self._total_price)


# @dataclass()
class Basket(db.Model):
    """
    class represents a shopping basket of a single user to a single store
    """
    # store: Store
    # products: TypedDict = None

    __tablename__ = 'basket'
    id = db.Column(db.Integer, primary_key=True)
    _products_ls = db.Column(MutableList.as_mutable(db.JSON))
    _is_used = db.Column(db.Boolean)
    # _products_ls = db.relationship("ProductInShoppingCart", lazy="joined")
    # _cart_id = db.Column(db.Integer, db.ForeignKey('shopping_cart.id'), nullable=True)
    _user = db.Column(db.String(50), nullable=True)
    _store_name = db.Column(db.String(50), db.ForeignKey('store._name'))
    # _store = db.relationship("Store", lazy="joined")
    _dal: DAL = DAL.get_instance()

    def __init__(self, store_name: str, products=None, user=None):
        if not isinstance(store_name, str):
            raise TypeError("Not a str")
        self.store_name = store_name
        self._products_ls = [] if products is None else list(products.keys())
        self.products = TypedDict(str, ProductInShoppingCart)
        self._user = user
        self._is_used = True

    @orm.reconstructor
    def loaded(self):
        self._products = TypedDict(str, ProductInShoppingCart)
        baskets_products = self._dal.get_all_products_of_basket(self.id)
        for p in baskets_products:
            p: ProductInShoppingCart = p
            p._product_name = p._product_data["name"]
            self._products[p._product_data["name"]] = p
            self._products_ls.append(p._product_data["name"])

    # @property
    # def store(self):
    #     return self._store

    # @store.setter
    # def store(self, new_store):
    #     if isinstance(new_store, Store):
    #         self._store = new_store
    #     else:
    #         raise TypeError("Not of type Store: store")

    @property
    def store_name(self):
        return self._store_name

    @store_name.setter
    def store_name(self, new_store_name):
        if isinstance(new_store_name, str):
            self._store_name = new_store_name
        else:
            raise TypeError("Not of type string")

    @property
    def products(self):
        return self._products

    @products.setter
    def products(self, new_products):
        if isinstance(new_products, TypedDict) and new_products.check_types(str, ProductInShoppingCart):
            self._products = new_products
        else:
            raise TypeError("Not of type ProductInShoppingCart: products")

    def clear_connections_to_inventory(self):
        for product in self.products.values():
            product: ProductInShoppingCart = product
            product._product_in_inventory_id = None
            product._item = None

    def edit_quantity_of_product(self, product_name: str, new_quantity: int):
        """
        editing quantity of a product in the basket
        :param product_name: (str) name of the product
        :param new_quantity: (int) new quantity of the product
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([product_name]) and TypeChecker.check_for_positive_ints(
                [new_quantity])):
            # TODO: problem with logger
            # log = Log.get_instance().get_logger()
            # log.error(f"ERROR IN 'edit_quantity_of_product' in Basket class: wrong types: expected str, and positive "
            #           f"int, instead got {type(product_name)}: {product_name} , {type(new_quantity)}: {new_quantity}")
            log = Log.get_instance().get_logger()
            log.error(
                f"ERROR IN 'edit_quantity_of_product' in Basket class: wrong types: expected str, and positive int, "
                f"instead got {type(product_name)}: {product_name} , {type(new_quantity)}: {new_quantity}")
            return Result(False, -1,
                          f'TYPEERROR: Expecting str and positive int. Got {type(product_name)}, {type(new_quantity)}',
                          {"product_name": product_name, "store_name": self.store_name,
                           "quantity": self.products[product_name]._product_quantity,
                           "total_price": round(self.products[product_name]._total_price, 2)})
        else:
            if product_name in self.products:
                if new_quantity == 0:
                    # del self.products[product_name]
                    p = self.products.pop(product_name)
                    self._dal.add(p, add_only=True)
                    self._dal.delete(p)
                else:
                    p: ProductInShoppingCart = self.products[product_name]
                    self._dal.add(p, add_only=True)
                    p._product_quantity = new_quantity
                    # to_edit: ProductInInventory = p._item
                    # to_edit.quantity = new_quantity
                return Result(True, -1, "product edited successfully",
                              {"product_name": product_name, "store_name": self.store_name,
                               "quantity": new_quantity,
                               "total_price": self.products[
                                   product_name]._total_price if product_name in self.products else 0})
            else:
                return Result(False, -1, "The desired product is not in the basket to edit",
                              {"product_name": product_name, "store_name": self.store_name,
                               "quantity": 0,
                               "total_price": 0})

    def add_product_to_basket(self, product_name: str, quantity: int):
        """
        adding product to basket if available in the store this basket relates to.
         if the product does not exists in the store, will raise an error
         if the product already exists in the basket, will add to it's quantity.
        :param product_name:
        :param quantity:
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([product_name]) and TypeChecker.check_for_positive_ints(
                [quantity])):
            return Result(False, -1, f'Expecting str and positive int. Got {type(product_name)}, {type(quantity)}',
                          None)
        elif quantity == 0:
            return Result(False, -1, "can't add a product with quantity 0 ", None)
        else:
            my_store: Store = self._dal.get_store_by_name(self.store_name)
            to_add = my_store.get_copy_of_product(product_name, quantity)
            if to_add is None:  # product was not found \ lacking quantity
                return Result(False, -1, "wanted product was not found in the given store", -2)
            elif not to_add:
                return Result(False, -1, "not enough quantity in the store", None)
            else:
                if product_name in self.products:  # product is already in basket -> add to it
                    p: ProductInShoppingCart = self.products[product_name]
                    self._dal.add(p, add_only=True)
                    p._product_quantity += quantity
                    # to_add_to: ProductInInventory = self.products[product_name]._item
                    # to_add_to.quantity += quantity
                    p.update_total_price()  # TODO: check if need to call DAL here
                    self._dal.add(self, add_only=True)
                else:  # add new product to basket
                    p = ProductInShoppingCart((to_add.price * quantity), to_add, self.id, quantity)
                    # p = ProductInShoppingCart((to_add.price * to_add.quantity), to_add, self.id)
                    self._dal.add(p, add_only=True)
                    self._products_ls.append(p.item.product_name)
                    self.products[product_name] = p
                    self._dal.add(self, add_only=True)
                return Result(True, -1, "product was added to basket successfully", None)

    def remove_product_from_basket(self, product_name: str):
        """
        removing product from basket
        :param product_name: (str) name of the product
        :return: True if product was deleted, raise exception if product was not found at all
        """
        if product_name not in self.products:
            return Result(False, -1, "the product that needs to be removed doesn't exists in this basket", None)
        else:
            p = self.products.pop(product_name)
            self._dal.add(p, add_only=True)
            self._dal.delete(p)
            # del self.products[product_name]
            return Result(True, -1, "removal success", None)

    def get_total_price_of_product(self, product_name: str):
        """
        return the total price of products according to quantity and price
        :param product_name:(str) name of product to calculate total price for
        :return: total price of the quantity * price per unit. if product not found, return -1
        """
        if product_name not in self.products:
            return -1
        else:
            # current: ProductInInventory = self.products[product_name]
            return self.products[product_name]._total_price

    def get_total_value_of_basket(self):
        """
        return the total price of the basket according to it's baskets
        :return: positive number(int or float) which is the total price of the basket
        """
        output = 0
        for p_name in self.products.keys():
            output += self.get_total_price_of_product(p_name)
        return output

    def get_total_quantity_of_category(self, category: str):
        """
        :param category: name of category
        :return: total quantity of input category in basket
        """
        quantity = 0
        values = self.products.values()
        for product in values:
            p: ProductInInventory = product._item
            if category in p.categories:
                quantity += product._product_quantity
        return quantity

    def to_dictionary(self):
        """
        :return: dictionary representation of this object
        """
        products = []
        for k, product in self.products.items():
            self._dal.add(product, add_only=True)
            products.append(product.to_dictionary())
        return {"store": self.store_name, "basket": products, "total_price": round(self.get_total_value_of_basket(), 2)}

    def pre_purchase(self):
        """
        save actual products from store before actual purchase
        :return: list of tuples
        """
        my_store: Store = self._dal.get_store_by_name(self.store_name)
        if not my_store.open:
            output = [(p, "store is closed, cannot purchase product") for p in self.products]
            self.products.clear()
            return output
        else:
            missing_products = {"store_name": self.store_name, "problems": []}
            for p in self.products.values():
                product = p.item
                result_quantity = my_store.pre_purchase_from_store(product.product_name, p._product_quantity)
                if p._product_quantity > result_quantity:
                    p._product_quantity = result_quantity
                    missing_products['problems'].append((product.product_name, f"there are only {result_quantity} left"))
            return missing_products

    def cancel_purchase(self):
        """
        Cancel pre-purchase because products were missing
        :return None
        """
        for p in self.products.values():
            my_store: Store = self._dal.get_store_by_name(self.store_name)
            my_store.add_product_after_product_cancellation(p)

    def copy(self):
        return Basket(self.store_name,
                      TypedDict(str, ProductInShoppingCart, {p.item.product.name: p.copy() for p in self.products}),
                      self._user)


class ShoppingCart:
    """
    class represents the total baskets of a single user.
    """

    # id = db.Column(db.Integer, primary_key=True)
    # _baskets_ls = db.relationship("Basket", lazy="joined")
    _dal: DAL = DAL.get_instance()

    def __init__(self, baskets: TypedDict = None, user=None):
        # self._baskets_ls = []
        if baskets is None:
            baskets = TypedDict(str, Basket)
        self.baskets = baskets
        self._user = user

    # @orm.reconstructor
    # def loaded(self):
    #     self._baskets = TypedDict(str, Basket)
    #     for b in self._baskets_ls:
    #         self._baskets[b.store_name] = b

    @property
    def baskets(self):
        return self._baskets

    @baskets.setter
    def baskets(self, new_baskets: TypedDict):
        if isinstance(new_baskets, dict):  # and new_baskets.check_types(str, Basket):
            self._baskets = new_baskets
        else:
            raise TypeError("Not of type dict(str,Basket): baskets")

    # @property
    # def is_real_products(self):
    #     return self._is_real_products
    #
    # @is_real_products.setter
    # def is_real_products(self, is_real_products: bool):
    #     if type(is_real_products) == bool:
    #         self._is_real_products = is_real_products
    #     else:
    #         raise TypeError("not of type bool : is_real_products")

    def is_empty(self):
        """
        :return: True if no products in cart, False otherwise
        """
        return len(self.baskets) == 0

    def add_product(self, store: Store, product_to_add: str, quantity: int, user_id: str):
        """
        adding product to the shopping cart to the right basket(or create new basket)
        :param store: (Store) store to get the product from
        :param product_to_add: (str) name of the product
        :param quantity: (int) wanted quantity of the product
        :return: True if product added successfully,False otherwise
        """
        from src.domain.system.store_classes import Store
        if not (isinstance(store, Store) and TypeChecker.check_for_non_empty_strings(
                [product_to_add]) and TypeChecker.check_for_positive_ints([quantity])):
            raise TypeError(
                f"expected Store,str,int. got instead {type(store)}, {type({product_to_add})}, {type(quantity)}")
        elif quantity == 0:
            raise TypeError("cannot add quantity of 0")
        elif not store.open:
            if store.name in self.baskets:
                b = self.baskets.pop(store.name)
                self._dal.add(b, add_only=True)
                self._dal.delete(b, del_only=True)
                # del self.baskets[store.name]
            return Result(False, -1, "Store is closed", None)
        else:
            for bas in self.baskets.values():
                self._dal.add(bas, add_only=True)
            if store.name not in self.baskets:
                # basket of store already exists in
                basket = Basket(store.name, user=user_id)
                self._dal.add(basket, add_only=True)
                self._dal.flush()
                is_added: Result = basket.add_product_to_basket(product_to_add, quantity)
                if is_added.succeed:  # if successful - adding basket to shopping cart
                    self.baskets[store.name] = basket
                else:
                    return is_added
            else:
                basket: Basket = self.baskets[store.name]
                self._dal.add(basket, add_only=True)
                is_added: Result = basket.add_product_to_basket(product_to_add, quantity)
            self.calc_update_price_of_basket(basket.store_name)
            # self._baskets_ls.append(basket)
            self._dal.add(basket, add_only=True)
            return is_added

    def calc_updated_price_of_all_baskets(self):
        """
        return the total discounted price of the basket according to it's baskets
        :return: positive number(int or float) which is the total discounted price of the basket
        """
        for k in self.baskets.keys():
            self.calc_update_price_of_basket(k)

    def calc_update_price_of_basket(self, store_name: str):
        """
        updating price of a single basket
        :param store_name: name of the store
        :return: None
        """
        if store_name in self.baskets:
            bas: Basket = self.baskets[store_name]
            self._dal.add(bas, add_only=True)
            for k, p in bas.products.items():
                self._dal.add(p, add_only=True)
                p: ProductInShoppingCart = p
                p.update_total_price()
            store: Store = self._dal.get_store_by_name(bas.store_name)
            new_basket: Basket = store.apply_discount_on_basket(bas)
            self.baskets[store_name] = new_basket
            return True
        else:
            return False  # store was not found

    def remove_product(self, store_name: str, product_name: str):
        """
        Removing product from basket of given store
        :param store_name:(str) name of the store
        :param product_name:(str) name of the product
        :return: Result with info on process
        """

        if not TypeChecker.check_for_non_empty_strings([store_name, product_name]):
            # log: Log = Log.get_instance() log.get_logger().error( f"ERROR IN 'remove_product' in ShoppingCart
            # class: expected non-empty str, non-empty str instead got {type(store)}: {store}, {type(product_name)}:
            # {product_name}")
            raise TypeError(f"expeted str,str . got instead {type(store_name)}, {type(product_name)}")

        else:
            if store_name not in self.baskets:
                return Result(False, -1, "shopping cart doesn't have basket of that store", None)
            else:
                basket: Basket = self.baskets[store_name]
                self._dal.add(basket, add_only=True)
                store: Store = self._dal.get_store_by_name(basket.store_name)
                if not store.open:
                    if store.name in self.baskets:
                        # del self.baskets[basket.store.name]
                        b = self.baskets.pop(basket.store_name)
                        self._dal.delete(b)
                    return Result(False, -1, "Store is closed", None)
                res: Result = basket.remove_product_from_basket(product_name)
                if res.succeed and len(
                        basket.products) == 0:  # if removal was successful and basket is empty - remove basket
                    # del self.baskets[store]
                    b = self.baskets.pop(store_name)
                    self._dal.add(b, add_only=True)
                    self._dal.delete(b)
                self.calc_update_price_of_basket(basket.store_name)
                return res

    def edit_product(self, store: str, product_name: str, new_quantity: int):
        """
        edit the quantity of one of the products in one of the baskets
        :param store: (str) name of the store the basket belong to
        :param product_name: (str) name of the product to edit
        :param new_quantity: (int) new quantity to edit
        :return: Result with info on process
        """
        if not (TypeChecker.check_for_non_empty_strings([store, product_name]) and TypeChecker.check_for_positive_ints(
                [new_quantity])):
            # log: Log = Log.get_instance() log.get_logger().error( f"ERROR IN 'edit_product' in ShoppingCart class:
            # expected non-empty str, non-empty str, positive int, instead got {type(store)}: {store},
            # {type(product_name)}: {product_name}, {type(new_quantity)}: {new_quantity}")
            return Result(False, -1,
                          f"expected str,str,int. instead got {type(store)}, {type(product_name)}, {type(new_quantity)}",
                          None)
        elif store not in self.baskets:  # doesnt have basket for that store
            # Log.get_instance().get_logger().error( f"ERROR IN 'edit_product' in ShoppingCart class: was trying to
            # edit product in a Basket that doesn't exists in this cart. not suppose to happen")
            return Result(False, -1, "shopping cart doesn't have basket of that store", None)
        else:
            basket: Basket = self.baskets[store]
            self._dal.add(basket, add_only=True)
            store: Store = self._dal.get_store_by_name(basket.store_name)
            if not store.open:
                if basket.store_name in self.baskets:
                    # del self.baskets[basket.store.name]
                    s = self.baskets.pop(basket.store_name)
                    self._dal.delete(s)
                return Result(False, -1, "Store is closed", None)
            res = basket.edit_quantity_of_product(product_name, new_quantity)
            if res.succeed and len(basket.products) == 0:
                # del self.baskets[store]
                s = self.baskets.pop(store)
                self._dal.delete(s)
            elif res.succeed:
                self.calc_update_price_of_basket(basket.store_name)
                self._dal.add(basket)
                return Result(True, res.requesting_id, res.msg,
                              {"product_name": product_name, "store_name": store._name,
                               "quantity": new_quantity,
                               "total_price": basket.products[
                                   product_name]._total_price if product_name in basket.products else 0})

            return res

    def apply_policies_for_shopping_cart(self):
        for store_name in self.baskets.keys():
            self.apply_policies_for_basket(store_name)

    def apply_policies_for_basket(self, store_name: str):
        if store_name in self.baskets:
            bas: Basket = self.baskets[store_name]
            store: Store = self._dal.get_store_by_name(bas.store_name)
            if not store.apply_policies_on_basket(bas):
                return False
            return True
        else:
            return False

    def get_total_value_of_shopping_cart(self):
        """
        return the total value of the products in the shopping cart
        :return: int or float of the total price of the cart
        """
        output = 0
        for basket in self.baskets.values():
            output += basket.get_total_value_of_basket()
        return output

    def to_dictionary(self):
        """
        :return: dictionary representation of the shopping cart
        """
        self.calc_updated_price_of_all_baskets()
        baskets = []
        for store, bas in self.baskets.items():
            baskets.append(bas.to_dictionary())
        return {"baskets": baskets,
                "total_price": round(self.get_total_value_of_shopping_cart(), 2)}

    def pre_purchase(self):
        self.calc_updated_price_of_all_baskets()
        baskets_to_delete = []
        problems_with_products = []
        for basket in self.baskets.values():
            store: Store = self._dal.get_store_by_name(basket.store_name)
            if not store.open:
                baskets_to_delete.append(basket.store_name)
            res: dict = basket.pre_purchase()
            if res['problems']:
                problems_with_products.append(res)
        for name in baskets_to_delete:
            # del self.baskets[name]
            s = self.baskets.pop(name)
            self._dal.delete(s, del_only=True)
            self._dal.flush()  # So we ill able to call .id
        if not problems_with_products:  # if list is empty -> no problems at all:
            for basket in self.baskets.values():
                if not self.apply_policies_for_basket(basket.store_name):
                    self.cancel_purchase()
                    return Result(False, -1, "Shopping policies are violated", problems_with_products)
            return Result(True, -1, "all products are ready for purchase", self.get_total_value_of_shopping_cart())

        else:
            self.cancel_purchase()
            return Result(False, -1, "Some Products were missing. details in data", problems_with_products)

    def cancel_purchase(self):
        """
        return items in shopping cart back to inventory
        :return: None
        """
        for basket in self.baskets.values():
            basket.cancel_purchase()

    def after_purchase(self, user_id: int, user_name: str = None):
        """
        create and return a Purchase. after that clear shopping cart from products
        :return: PurchaseReport to return to the client and save in the history of purchases
        """
        if user_name is None:
            user_name = f'Guest#{user_id}'
        purchase_list: TypedList = TypedList(Purchase)
        current_time = datetime.now()
        total_price = self.get_total_value_of_shopping_cart()
        purchase_type = PurchaseType.Immediate
        # p_id: str = f'{user_id}-{purchase_type.to_string()}-{current_time.timestamp()}'
        stores_to_check_list = []
        if user_name is not None:
            for basket in self.baskets.values():
                basket: Basket = basket
                self._dal.add(basket, add_only=True)
                basket.clear_connections_to_inventory()
                store: Store = self._dal.get_store_by_name(basket.store_name)
                stores_to_check_list.append(store)
                current_purchase: Purchase = Purchase(purchase_type=purchase_type.value, user_name=user_name,
                                                      basket_fk=basket.id, at_dt=current_time,
                                                      store_name=basket.store_name, basket_obj=basket)
                self._dal.add(current_purchase, add_only=True)
                self._dal.flush()  # So we ill able to call .id
                purchase_list.append(current_purchase)

                store.add_purchases(TypedList(Purchase, [current_purchase]))
                self._dal.add(store, add_only=True)
                self._dal.flush()  # So we ill able to call .id
                # for notifications

            for bas in self.baskets.values():
                bas: Basket = bas
                bas._is_used = False
                self._dal.add(bas, add_only=True)
            self.baskets.clear()
            # self._baskets_ls.clear()
            # self._dal.add(self, add_only=True)
            self._dal.flush()  # So we ill able to call .id
        return PurchaseReport(purchase_type, purchase_list, current_time, float(total_price),
                              user_name), stores_to_check_list  # TODO: check current purchase


class PurchaseType(enum.Enum):
    Immediate = 1

    def to_string(self):
        if self == PurchaseType.Immediate:
            return "Immediate"
        else:
            return "Other"


class Purchase(db.Model):
    __tablename__ = 'purchase'
    _purchase_id = db.Column(db.String(100), primary_key=True)
    _purchase_type = db.Column(db.Integer)
    _user_name = db.Column(db.String(50))
    _store_name = db.Column(db.String(50), db.ForeignKey("store._name"))
    _basket_fk = db.Column(db.Integer, db.ForeignKey("basket.id"))
    _basket = db.relationship("Basket", lazy="joined")
    _at_date_time = db.Column(db.DateTime)

    def __init__(self, purchase_type: int, user_name: str, basket_fk: int,
                 store_name: str, at_dt: datetime = datetime.now(), basket_obj=None):
        self.purchase_type = purchase_type
        self._user_name = user_name
        self._basket_fk = basket_fk
        self.basket = basket_obj
        self.store_name = store_name
        self.at_date_time = at_dt
        self._purchase_id = f"{purchase_type}-{user_name}-{store_name}-{str(at_dt)}"

    @property
    def store_name(self):
        return self._store_name

    @store_name.setter
    def store_name(self, new_store_name: str):
        if new_store_name is None or not type(new_store_name) == str or new_store_name == "":
            raise TypeError("not a valid purchase id")
        self._store_name = new_store_name

    @property
    def purchase_id(self):
        return self._purchase_id

    @purchase_id.setter
    def purchase_id(self, new_purchase_id: int):
        if new_purchase_id is None or not type(new_purchase_id) == int:
            raise TypeError("not a valid purchase id")
        self._purchase_id = new_purchase_id

    @property
    def basket(self):
        return self._basket

    @basket.setter
    def basket(self, new_basket: Basket):
        if new_basket is None or not isinstance(new_basket, Basket):
            raise TypeError("not a valid purchase id")
        self._basket = new_basket

    @property
    def purchase_type(self):
        return self._purchase_type

    @purchase_type.setter
    def purchase_type(self, new_purchase_type: int):
        if new_purchase_type is None or not type(new_purchase_type) == int:
            raise TypeError("not a valid PurchaseType")
        self._purchase_type = new_purchase_type

    @property
    def at_date_time(self):
        return self._at_date_time

    @at_date_time.setter
    def at_date_time(self, new_at_dt: datetime):
        if new_at_dt is None or not type(new_at_dt) == datetime:
            raise TypeError("not a valid date time")
        self._at_date_time = new_at_dt

    def to_dictionary(self):
        p_type = "Immediate" if self.purchase_type == PurchaseType.Immediate.value else "Other"
        return {
            "purchase_id": self.purchase_id,
            "purchase_type": p_type,
            "user_name": self._user_name,
            "time_of_purchase": self._at_date_time,
            "basket": self.basket.to_dictionary()
        }


@dataclass()
class PurchaseReport:
    purchase_type: PurchaseType
    purchase_list: TypedList
    date_of_purchase: datetime
    total_price: float
    user_name: str

    # purchase_id: int

    def __post_init__(self):
        if not isinstance(self.purchase_type, PurchaseType):
            raise TypeError("Not a valid PurchaseType")

        if not isinstance(self.purchase_list, TypedList) or not self.purchase_list.check_types(Purchase):
            raise TypeError("Not of type TypedList(Purchase): purchase_list")

        if not isinstance(self.user_name, str):
            raise TypeError("Not of type str: user_name")

        # if not isinstance(self.purchase_id, int):
        #     raise TypeError("Not of type int: purchase_id")

        if not isinstance(self.total_price, float) or self.total_price <= 0:
            raise TypeError("Not a valid price, expected float with value > 0")

        if not isinstance(self.date_of_purchase, datetime):
            raise TypeError("Not of type datetime: date_of_purchase")

    def to_dictionary(self):
        p_type = "Immediate" if self.purchase_type == PurchaseType.Immediate else "Other"
        return {
            "purchase_type": p_type,
            "purchases": [p.to_dictionary() for p in self.purchase_list],
            "time_of_purchase": self.date_of_purchase,
            "total_price": round(self.total_price, 2),
            "username": self.user_name,
            # "purchase_id": self.purchase_id,
        }
