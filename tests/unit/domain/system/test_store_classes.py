import os

import pytest

from src.domain.system.data_handler import DataHandler
from src.domain.system.store_classes import Store
from src.protocol_classes.classes_utils import TypedDict, Result, TypedList
from src.domain.system.products_classes import ProductInInventory, Product
from src.domain.system.permission_classes import Role, Permission
from src.domain.system.cart_purchase_classes import Basket, ShoppingCart, Purchase, PurchaseType
from src.domain.system.users_classes import LoggedInUser, User
from src.security.security_system import Encrypter
from datetime import datetime, timedelta

from tests.db_config_tests import test_flask

p1: ProductInInventory = None
p2: ProductInInventory = None
s: Store = None
inventory: TypedDict = None
initial_owner: User = None
manager: User = None
data_handler: DataHandler = None


# ALL_PRODUCT_TEST = [f"Product{i}" for i in range(1, 5)]
# ALL_PRODUCTS_INVENTORY_TESTS = [f'ProductInInventory{i}' for i in range(1, 8)]
# PRODUCT_INVENTORY_DEPENDENCIES = ALL_PRODUCT_TEST + [f'test_price_and_discount::{i}' for i in
#                                                      ALL_TESTS_PRICE_AND_DISCOUNT]


@pytest.fixture(scope="session", autouse=True)
def set_up_test(request):
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
    global p1, p2, s, inventory, initial_owner, manager
    inventory = TypedDict(str, ProductInInventory)
    p1 = ProductInInventory(Product('p1'), price=5, quantity=5)
    p2 = ProductInInventory(Product('p2'), price=10, quantity=5)
    inventory['p1'] = p1
    inventory['p2'] = p2
    initial_owner = User(1)
    initial_owner.user_state = LoggedInUser("owner", Encrypter.hash_password(password="!,fldmAd12s"), "habibi@g.com")
    manager = User(2)
    manager.user_state = LoggedInUser('manager', Encrypter.hash_password(password="!,fldmAd12s"), "habibi2@g.com")
    s = Store("store", 'owner', inventory=inventory)
    initial_permission: Permission = Permission.define_permissions_for_init(Role.store_initial_owner, "owner", "store",
                                                                            None)
    s.add_store_member(initial_permission)
    initial_owner.user_state.add_permission(initial_permission)


def test_store_type_check():
    # unsuccessful
    with pytest.raises(TypeError):
        s = Store(5, 'owner')
    with pytest.raises(TypeError):
        s = Store(name="s_name", initial_owner='owner', inventory="wrong_type")
    with pytest.raises(TypeError):
        s = Store(name="s_name", initial_owner='owner', opened=None)
    with pytest.raises(TypeError):
        s = Store(name="s_name", initial_owner='owner', creation_date="wrong type")
    # successful
    s1 = Store(name="s_name", initial_owner='owner', inventory=TypedDict(str, ProductInInventory), opened=True,
               creation_date=datetime.now() - timedelta(days=1))
    s2 = Store(name="s_name", initial_owner='owner', inventory=TypedDict(str, ProductInInventory), opened=True)
    s3 = Store(name="s_name", initial_owner='owner', inventory=TypedDict(str, ProductInInventory))
    s4 = Store(name="s_name", initial_owner='owner')


#
#
# # @pytest.mark.dependency(name="Store2", depends=ALL_PERMOSSION_TESTS)
@pytest.mark.parametrize("test_input, output",
                         [(Store(name="s_name", initial_owner='owner',
                                 inventory=TypedDict(str, ProductInInventory),
                                 opened=True,
                                 creation_date=datetime.now() - timedelta(days=1)), True),
                          (Store(name="s_name", initial_owner='owner',
                                 inventory=TypedDict(str, ProductInInventory),
                                 opened=True,
                                 creation_date=datetime.now()),
                           True),
                          (Store(name="s_name", initial_owner='owner',
                                 inventory=TypedDict(str, ProductInInventory),
                                 opened=False), True),
                          (Store(name="s_name", initial_owner='owner', opened=True,
                                 creation_date=datetime.now() - timedelta(days=1)), True),
                          (Store(name="s2_name", initial_owner='owner',
                                 inventory=TypedDict(str, ProductInInventory),
                                 opened=True,
                                 creation_date=datetime.now() - timedelta(days=1)), False)])
# @pytest.mark.dependency(name="Store3", depends=ALL_PERMOSSION_TESTS)
def test_eq_store(test_input, output):
    """
    checks the equal function in Store
    :param test_input:
    :param output:
    :return:
    """
    s1 = Store(name="s_name", initial_owner='owner', inventory=TypedDict(str, ProductInInventory), opened=True,
               creation_date=datetime.now() - timedelta(days=1))
    assert (s1 == test_input) == output


def test_copy_store():
    s2: Store = s.copy()
    assert s2.name == s.name and s2.initial_owner == s.initial_owner and s2.open == s.open and s2.creation_date == s.creation_date
    assert all(p in s2.inventory for p in s.inventory) and all(p in s.inventory for p in s2.inventory)


#
# def test_dictionary_store(): assert s.to_dictionary() == {'creation_date': s.creation_date.strftime('%Y-%m-%d
# %H:%M:%S.%f'), 'initial_owner': 'owner', 'inventory': [{'price': {'base_price': 0, 'after_discount': 0},
# 'product': {'name': 'p1', 'brand': '', "description": "", 'categories': []}, 'quantity': 5, "store_name": ""},
# {'price': {'base_price': 0, 'after_discount': 0}, 'product': {'name': 'p2', 'brand': '', "description": "",
# 'categories': []}, 'quantity': 5, "store_name": ""}], 'name': 'store', 'open': True, "permissions": {
# p.user.user_state.user_name: p for p in s.get_permissions().values()}}


def test_add_purchases():
    with pytest.raises(TypeError):
        s.add_purchases(5)
    with pytest.raises(TypeError):
        s.add_purchases(TypedList(str, ["hey", 'you']))
    assert len(s.purchases) == 0
    # purchases = TypedList(Purchase, [Purchase(PurchaseType.Immediate.value, "owner", 12, "store", datetime.now())])
    # s.add_purchases(purchases)
    # assert len(s.purchases) == 1


def test_open_store():
    global s
    s.open_store()
    assert s.open


def test_close_store():
    global s
    s.close_store()
    assert not s.open


def test_add_store_member():
    p: Permission = Permission.define_permissions_for_init(Role.store_initial_owner, "owner", "store")
    res: Result = s.add_store_member(p)
    assert not res.succeed
    p: Permission = Permission.define_permissions_for_init(Role.store_manager, "manager", "store")
    res: Result = s.add_store_member(p)
    assert res.succeed


def test_remove_member():
    global s
    res: bool = s.remove_member(initial_owner.user_state.user_name)
    assert res
    res: bool = s.remove_member(manager.user_state.user_name)
    assert res


def test_get_copy_of_product():
    with test_flask.app_context():
        p23 = Product('p1')
        x = ProductInInventory(p23, price=2.0, quantity=1)
        assert s.get_copy_of_product('p1', 1) == x
        assert not s.get_copy_of_product('p1', 7)


def test_add_product():
    global s
    s.add_product('new_product', 100.0, 1)
    product: ProductInInventory = s.inventory['new_product']
    assert product.price == 100 and product.quantity == 1 and product.product.name == 'new_product'


def test_add_product_after_product_cancellation():
    assert 'new_product_new_product' not in s.inventory
    s.add_product('new_product_new_product', 100.0, 1)
    product: ProductInInventory = s.inventory['new_product_new_product']
    assert product.price == 100 and product.quantity == 1 and product.product.name == 'new_product_new_product'


def test_pre_purchase_from_store():
    global s
    with pytest.raises(TypeError):
        s.pre_purchase_from_store(1, '1')
    with pytest.raises(TypeError):
        s.pre_purchase_from_store('p1', '1')
    with pytest.raises(TypeError):
        s.pre_purchase_from_store(1, 1)
    s.pre_purchase_from_store('p1', 1)


def test_remove_product_from_store():
    global s
    with pytest.raises(TypeError):
        s.remove_product_from_store(1)
        assert s.remove_product_from_store('p1')
        assert not s.remove_product_from_store('p400')

# def test_edit_product_in_store():
#     global s, inventory, p1, p2
#     with test_flask.app_context():
#         set_up_for_store()
#         s.edit_product_in_store('p1', 'brand1', 100.0, 6, TypedList(str, ['cat1']))
#         product: ProductInInventory = s.inventory['p1']
#         assert product.price == 100.0 and product.quantity == 5 and product.product.name == 'p1' and \
#                product.product.brand == 'brand1' and 'cat1' in product.product.categories


# @pytest.mark.parametrize("product_name, categories,brands,min_price,max_price,output",
#                          [('p', None, None, None, None, 2),
#                           ('p', None, None, 0, None, 2),
#                           ('p1', None, None, None, None, 1),
#                           ('p2', None, None, None, None, 1),
#                           ('p', ['cat1'], None, None, None, 1),
#                           ('p', None, ['brand1'], None, None, 1),
#                           ('p', None, None, 200, None, 0),
#                           ('p', None, None, 100, None, 1),
#                           ('p', None, None, None, 50, 1),
#                           ])
# def test_search(product_name: str, categories, brands, min_price,
#                 max_price, output):
#     assert len(s.search_product(product_name, categories, brands, min_price, max_price)) == output
