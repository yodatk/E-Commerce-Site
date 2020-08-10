import os
from datetime import datetime, timedelta

import pytest

from src.domain.system.data_handler import DataHandler
from src.domain.system.permission_classes import Role, Permission
from src.domain.system.products_classes import ProductInInventory, Product
from src.domain.system.store_classes import Store
from src.protocol_classes.classes_utils import TypedDict, TypedList
from src.domain.system.users_classes import LoggedInUser, User
from src.security.security_system import Encrypter
from tests.db_config_tests import test_flask

p1: ProductInInventory = None
p2: ProductInInventory = None
s: Store = None
inventory: TypedDict = None
initial_owner: User = None
data_handler: DataHandler = None
temp_date = datetime.now() + timedelta(days=1)


# ALL_PRODUCT_TEST = [f"Product{i}" for i in range(1, 5)]
# ALL_PRODUCTS_INVENTORY_TESTS = [f'ProductInInventory{i}' for i in range(1, 8)]
# PRODUCT_INVENTORY_DEPENDENCIES = ALL_PRODUCT_TEST + [f'test_price_and_discount::{i}' for i in
#                                                      ALL_TESTS_PRICE_AND_DISCOUNT]


@pytest.fixture(scope="session", autouse=True)
def set_up_test(request):
    # setting db in debug mode
    # setting db in debug mode
    global data_handler
    with test_flask.app_context():
        try:
            os.remove('db_test.db')
            print("Removed DB")
        except:
            print("Removed db failed")
        data_handler = DataHandler()
        data_handler.create_all(lambda dbi: dbi.init_app(test_flask))
        set_up_for_store()


def set_up_for_store():
    global s, initial_owner, data_handler
    data_handler = DataHandler()
    initial_owner = User(1)
    initial_owner.user_state = LoggedInUser("owner", Encrypter.hash_password(password="!,fldmAd12s"), "habibi@g.com")
    s = Store("store", 'owner')  # ("store", 'owner', inventory=inventory)
    initial_permission: Permission = Permission.define_permissions_for_init(Role.store_initial_owner,
                                                                            "owner", "store")
    s.add_store_member(initial_permission)
    initial_owner.user_state.add_permission(initial_permission)
    s.add_product("p1", 10.0, 5)
    s.add_product("p2", 10.0, 5)

    # inventory = TypedDict(str, ProductInInventory)
    # p1 = ProductInInventory(Product('p1'), price=10.0, quantity=5)
    # p2 = ProductInInventory(Product('p2'), price=10.0, quantity=5)
    # s.inventory['p1'] = p1
    # s.inventory
    # inventory['p1'] = p1
    # inventory['p2'] = p2


# Product tests
@pytest.mark.dependency(name="Product2")
@pytest.mark.parametrize("test_input,output",
                         [(Product(name="p1", brand="b1"), True),
                          (Product(name="p2", brand="b1"), False),
                          (Product(name="p1", brand="b2"), False),
                          (Product(name="p1"), False)]
                         )
def test_eq_product(test_input, output):
    """
    checks the eq of product
    :return:
    """
    p1_test = Product("p1", "b1")
    assert (p1_test == test_input) == output


# @pytest.mark.dependency(name="Product3")
def test_copy_product():
    copied: Product = Product(name="p1", brand="b1", categories=TypedList(str, ['c1', 'c2'])).copy()
    assert copied.name == "p1"
    assert copied.brand == "b1"
    assert len(copied.categories) == 2
    for i in copied.categories:
        assert i in ['c1', 'c2']


# @pytest.mark.dependency(name="Product4")
@pytest.mark.parametrize("test_input,output1",
                         [(Product(name="p1", brand="b1", categories=TypedList(str, ['c1', 'c2'])),
                           {"name": 'p1', "brand": 'b1', "description": "", "categories": ['c1', 'c2']}),
                          (Product(name="p1", brand="b1"),
                           {"name": 'p1', "brand": 'b1', "description": "", "categories": []})])
def test_to_dictionary_product(test_input, output1):
    assert test_input.to_dictionary() == output1


#
#
# product in inventory tests
# @pytest.mark.dependency(name="ProductInInventory1", depends=ALL_PRODUCT_TEST + ALL_TESTS_PRICE_AND_DISCOUNT)
def test_check_input_type_product_inventory():
    """
    checks the constructor type-checking
    :return:
    """
    with pytest.raises(TypeError):
        x = ProductInInventory("wrong_type", 100, 5)
    with pytest.raises(TypeError):
        x = ProductInInventory(Product("p1"), 100, "5")
    x = ProductInInventory(Product("p1"), 100.0, 5)


# @pytest.mark.parametrize("test_input, output", [(ProductInInventory(Product("p1", "b1"), 100, 5), 5),
#                                                 (ProductInInventory(Product("p1", "b2"), 100, 0), 0)])
# # @pytest.mark.dependency(name="ProductInInventory2", depends=ALL_PRODUCT_TEST + ALL_TESTS_PRICE_AND_DISCOUNT)
def test_quantity_product_in_inventory():
    x = ProductInInventory(Product("p1", "b1"), 100, 5)
    assert x.quantity == 5
    y = ProductInInventory(Product("p1", "b2"), 100, 0)
    assert y.quantity == 0


# # @pytest.mark.dependency(name="ProductInInventory3", depends=ALL_PRODUCT_TEST + ALL_TESTS_PRICE_AND_DISCOUNT)
def test_set_quantity_product_in_inventory():
    """
    checks set quantity in ProductInInventory
    :return:
    """
    p1 = ProductInInventory(Product("p1", "b1"), 100, 10)
    with pytest.raises(TypeError):
        p1.quantity = -5
    p1.quantity = 5
    assert p1.quantity == 5
    p1.quantity = 0
    assert p1.quantity == 0


# # @pytest.mark.dependency(name="ProductInInventory4", depends=ALL_PRODUCT_TEST + ALL_TESTS_PRICE_AND_DISCOUNT)
# @pytest.mark.parametrize("test_input, output", [(ProductInInventory(Product("p1", "b1"), 100, 5), True),
#                                                 (ProductInInventory(Product("p1", "b2"), 100, 5), False),
#                                                 (ProductInInventory(Product("p1", "b1"), 150, 5), True),
#                                                 (ProductInInventory(Product("p1"), 100, 5), False)])
def test_eq_products_in_inventory():
    """
    checks the equal function in ProductsInInventory
    :param test_input:
    :param output:
    :return:
    """
    p1 = ProductInInventory(Product("p1", "b1"), 100, 5)
    x = ProductInInventory(Product("p1", "b1"), 100, 5)
    assert p1 == x
    y = ProductInInventory(Product("p1", "b2"), 100, 5)
    assert not (p1 == y)


# @pytest.mark.dependency(name="ProductInInventory5", depends=ALL_PRODUCT_TEST + ALL_TESTS_PRICE_AND_DISCOUNT)
def test_copy():
    p1 = ProductInInventory(Product("p1", "b1", TypedList(str, ['c1', 'c2'])), 150, 5)
    copied: ProductInInventory = p1.copy()
    assert p1 == copied
    assert copied.price == p1.price
    assert copied.product.categories == ['c1', 'c2']


# # @pytest.mark.dependency(name="ProductInInventory6", depends=ALL_PRODUCT_TEST + ALL_TESTS_PRICE_AND_DISCOUNT)
# @pytest.mark.parametrize("test_input,output1",
#                          [(ProductInInventory(Product(name="p1", brand="b1",
#                                                       categories=TypedList(str, ['c1', 'c2'])), price=10),
#                            {'product': {'name': 'p1', 'brand': 'b1', "description": "", 'categories': ['c1', 'c2']},
#                             'price': 10}),
#                           (ProductInInventory(Product(name="p1", brand="b1", categories=TypedList(str, ['c1', 'c2'])),
#                                               price=100, quantity=5),
#                            {'product': {'name': 'p1', 'brand': 'b1', "description": "", 'categories': ['c1', 'c2']},
#                             'price': 100, 'quantity': 5, "store_name": ""})])
# @pytest.mark.dependency(name="ProductInInventory7", depends=ALL_PRODUCT_TEST + ALL_TESTS_PRICE_AND_DISCOUNT)
def test_to_diciontary_product_in_inventory():
    x = ProductInInventory(Product(name="p1", brand="b1", categories=TypedList(str, ['c1', 'c2'])), price=10)
    print(x.to_dictionary())
    x_dict = {'after_discount': 10, 'discounts': [], 'policies': [], 'product': {'name': 'p1', 'brand': 'b1', "description": "", 'categories': ['c1', 'c2']}, 'price': 10,
              'quantity': 0, 'store_name': ''}
    assert x.to_dictionary() == x_dict
