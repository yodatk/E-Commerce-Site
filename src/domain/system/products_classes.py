from sqlalchemy import orm

from src.domain.system.discounts import _IDiscount, _IDiscountStrategy
from src.domain.system.shopping_policies import IShoppingPolicies
from src.protocol_classes.classes_utils import TypedList, TypedDict
from sqlalchemy.ext.mutable import MutableDict, MutableList
from src.domain.system.DAL import DAL
from src.domain.system.db_config import db


class Product(db.Model):
    """
    Data class to represents a Product in the system. have the following fields:
        1. name (string) - the name of the product
        2. brand(string) - the brand of the product
        3. categories(list of strings) - categories of the product
    """
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column(db.String(50))
    _brand = db.Column(db.String(50))
    _categories = db.Column(MutableList.as_mutable(db.JSON))
    _description = db.Column(db.String(500))

    def __hash__(self):
        return hash(self._name)

    def __init__(self, name: str, brand: str = "", categories: list = None, description: str = ""):
        if categories is None:
            categories = []

        self._name = name
        self._brand = brand
        self._categories = categories
        self._description = description

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name: str):
        if new_name is None or not type(new_name) == str or new_name.strip() == "":
            raise TypeError("not a valid string")
        self._name = new_name

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description: str):
        if new_description is None or not type(new_description) == str:  # or new_description.strip() == "":
            raise TypeError("not a valid string")
        self._description = new_description

    @property
    def brand(self):
        return self._brand

    @brand.setter
    def brand(self, new_brand: str):
        if new_brand is None or not type(new_brand) == str:
            raise TypeError("not a valid string")
        self._brand = new_brand

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, new_categories: list):
        if new_categories is None or new_categories == []:
            self._categories = []
        elif not isinstance(new_categories, list):
            raise TypeError(f"not a valid categories list")
        self._categories = new_categories

    def __eq__(self, other):
        if isinstance(other, Product):
            return self.name == other.name and self.brand == other.brand
        else:
            return False

    def copy(self):
        """
        copy constructor for Product
        :return: new Product object with the same properties as this product
        """
        return Product(self.name, self.brand, self.categories, self.description)

    def to_dictionary(self):
        """
        :return: dictionary representation of the Product
        """
        return {
            "name": self.name,
            "brand": self.brand,
            "categories": [c for c in self.categories],
            "description": self.description
        }


class ProductInInventory(db.Model):
    __tablename__ = 'product_in_inventory'
    id = db.Column(db.Integer, primary_key=True)
    _dal = DAL.get_instance()
    _product_pk = db.Column(db.Integer, db.ForeignKey('product.id'))
    _product = db.relationship("Product", lazy="joined")
    _store_fk = db.Column(db.String(50), db.ForeignKey("store._name"))
    _store = db.relationship("Store", lazy="joined",
                             foreign_keys=[_store_fk])

    _price = db.Column(db.Float)
    _quantity = db.Column(db.Integer)
    _policies = db.Column(MutableList.as_mutable(db.JSON))
    _discounts = db.Column(MutableList.as_mutable(db.JSON))

    def __hash__(self):
        return hash(f"{self._store_fk}-{self._product_pk}")

    def __init__(self, product: Product, price: float, quantity: int = 0, store_name: str = "", store_obj=None):
        self.product = product
        self.price = price
        self.quantity = quantity
        self.store_name = store_name
        self._store = store_obj
        self._discounts = []
        self._policies = []

    @property
    def product_name(self):
        return self.product.name

    @property
    def discounts(self):
        return self._dal.get_discount_map_with_id_keys(self._discounts)

    @discounts.setter
    def discounts(self, new_discounts: TypedDict):
        if not isinstance(new_discounts, TypedDict) and not new_discounts.check_types(int, _IDiscount):
            raise TypeError("not a valid Discounts list")
        if len(new_discounts) != 0:
            self._discounts = [k for k, p in new_discounts.items()]

    def add_policy(self, policy: IShoppingPolicies):

        if policy.id not in self._policies:
            self._policies.append(policy.id)

    def add_discount(self, discount: _IDiscount):
        if discount.id not in self._discounts:
            self._discounts.append(discount.id)

    def clear_discounts(self):
        self._discounts.clear()

    def clear_policies(self):
        self._policies.clear()

    def remove_policy(self, policy_id):

        if policy_id in self._policies:
            if policy_id in self._policies:
                self._policies.remove(policy_id)

    def remove_discount(self, discount_id):
        if discount_id not in self._discounts:
            if discount_id in self._discounts:
                self._discounts.remove(discount_id)

    @property
    def policies(self):
        return self._dal.get_policy_map_with_id_keys(self._policies)

    @policies.setter
    def policies(self, new_policies: TypedDict):
        if not isinstance(new_policies, TypedDict) and not new_policies.check_types(int, IShoppingPolicies):
            raise TypeError("not a valid Policies list")
        if len(new_policies) != 0:
            self._policies = [k for k, p in new_policies.items()]

    @property
    def store_name(self):
        return self._store_fk

    @store_name.setter
    def store_name(self, new_store_name: str):
        if not isinstance(new_store_name, str):
            raise TypeError("not a valid Store name")
        self._store_fk = new_store_name

    @property
    def product(self):
        return self._product

    @product.setter
    def product(self, new_p: Product):
        if not isinstance(new_p, Product):
            raise TypeError("not a valid Product")
        self._product = new_p
        self._dal.add(self._product)
        self._dal.commit()

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, new_p: float):
        if not isinstance(new_p, float) and not isinstance(new_p, int):
            raise TypeError("not a valid Price")
        self._price = new_p

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, new_q: int):
        if type(new_q) != int or new_q < 0:
            raise TypeError("quantity must be int from 0 and above")
        self._quantity = new_q

    def __eq__(self, other):
        if isinstance(other, ProductInInventory):
            return self._product == other._product
        else:
            return False

    def copy(self):
        """
        :return: ProductInInventory with the same properties as this one

        """
        return ProductInInventory(self.product.copy(), self.price, self.quantity, self.store_name)

    def to_dictionary(self):
        """
        :return: dictionary representation of the Product
        """
        price_after_discount: float = self.price
        for k, discount in self.discounts.items():
            discount: _IDiscount = discount
            strategy: _IDiscountStrategy = discount.discount_strategy
            price_after_discount = strategy.activate_discount_on_single_product(self, price_after_discount)

        return {
            "product": self.product.to_dictionary(),
            "price": round(self.price, 2),
            "quantity": self.quantity,
            "store_name": self.store_name,
            "discounts": [d.get_description() for k, d in self.discounts.items()],
            "after_discount": round(price_after_discount, 2),
            "policies": [p.description() for k, p in self.policies.items()]
        }

    def check_quantity_of_category(self, category: str):
        """

        :param category: name of category
        :return: quantity of products in input category, if the category doesn't exist, return 0.
        """
        if category in self.product.categories:
            return self.quantity
        else:
            return 0


class PermissionDenied(Exception):
    """Exception when user try to edit something in store Even though he can't"""


class AlreadyExists(Exception):
    """Exception when user already is in management position, and trying to be appointed again"""


class ProductDoesNotExists(Exception):
    """Exception when trying to reach for a product that was not found in the inventory"""

# if __name__ == '__main__':
#     d = DAL.get_instance()
#     d.update_session(db.session)
#     app = Flask(__name__)
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
#     # https://flask-sqlalchemy.palletsprojects.com/en/2.x/signals/
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#     # To see the queries that are being run
#     app.config['SQLALCHEMY_ECHO'] = True
#     db.init_app(app)
#     with app.app_context():
#         db.create_all()
