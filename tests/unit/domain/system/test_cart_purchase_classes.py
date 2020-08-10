import os
from datetime import datetime, timedelta

import pytest

from src.domain.system.DAL import DAL
from src.domain.system.cart_purchase_classes import ShoppingCart, Basket, ProductInShoppingCart
from src.domain.system.data_handler import DataHandler
from src.domain.system.permission_classes import Permission, Role
from src.domain.system.store_classes import Store
from src.domain.system.users_classes import User, LoggedInUser
from src.protocol_classes.classes_utils import TypedList, TypedDict, Result
from src.security.security_system import Encrypter
from tests.db_config_tests import test_flask

STORE_NAME = "store"
STORE_INITIAL_OWNER = "owner"

initial_owner: User = None
shop_cart: ShoppingCart = None
store: Store = None
bas: Basket = None
dal: DAL = None


@pytest.fixture(scope="session", autouse=True)
def set_up_test(request):
    with test_flask.app_context():
        try:
            os.remove('db_test.db')
            print("Removed DB")
        except:
            print("Removed db failed")
        data_handler = DataHandler()
        data_handler.create_all(lambda dbi: dbi.init_app(test_flask))
        set_up()


def set_up():
    global bas, store, dal, shop_cart, initial_owner
    initial_owner = User(1)
    initial_owner.user_state = LoggedInUser(STORE_INITIAL_OWNER, Encrypter.hash_password(password="!,fldmAd12s"),
                                            "habibi@g.com")
    store = Store(STORE_NAME, STORE_INITIAL_OWNER, True, datetime.now(), None, None, initial_owner.user_state)
    # product_1 = Product("p1", "b1", ['c1'], "")
    # p1 = ProductInInventory(product_1, 10.0, 50, "store", store)
    store.add_product("p1", 50.0, 50, "b1", TypedList(str, ['c1']))
    store.add_product("p2", 20.0, 50, "b2", TypedList(str, ['c2']))

    initial_permission: Permission = \
        Permission.define_permissions_for_init(
            Role.store_initial_owner,
            STORE_INITIAL_OWNER,
            STORE_NAME,
            None,
            initial_owner.user_state,
            store,
            None)

    store.add_store_member(initial_permission)
    initial_owner.user_state.add_permission(initial_permission)
    bas = Basket(store.name, None, initial_owner.user_state.user_name)
    bas.add_product_to_basket('p1', quantity=2)
    shop_cart = ShoppingCart(TypedDict(str, Basket, {store.name: bas}))


def test_add_item_to_basket():
    with test_flask.app_context():
        assert len(bas.products) == 1
        res: Result = bas.add_product_to_basket('p1', -1)
        assert not res.succeed
        res: Result = bas.add_product_to_basket('p2', 1)
        assert res.succeed
        assert len(bas.products) == 2


# def test_total_price_after_discount():
#     with test_flask.app_context():
#         amount = bas.get_total_value_of_basket()
#         assert amount == 120
#         end_time = datetime.now() + timedelta(days=1)
#         res: Result = store.add_free_per_x_product_discount_discount(end_time, product_name='p1',
#                                                                      free_amount=1,
#                                                                      per_x_amount=2)
#         amount = bas.get_total_value_of_basket()
#         assert amount == 120
        # store.remove_discount_from_store(res.data)
        # id: Result = store.add_free_per_x_category_discount_discount(end_time, 'c1', 1, 2)
        # id: int = id.data
        # bas.add_product_to_basket('p2', 2)
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 80
        # store.remove_discount_from_store(id)
        # id: Result = store.add_simple_category_discount(end_time, discount_percent=0.5,
        #                                                 discounted_category='c1')
        # id: int = id.data
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 80
        #
        # bas.edit_quantity_of_product('p2', 1)
        # store.remove_discount_from_store(id)
        #
        # store.add_simple_product_discount(end_time, discount_percent=0.5, discounted_product='p1')
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 40
        #
        # store.remove_discount_from_store(id)
        # shop_cart.calc_update_price_of_basket(store.name)
        # id: Result = store.add_simple_product_discount(end_time, 0.4, discounted_product='p1', size_of_basket_cond=2)
        # id: int = id.data
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 40
        # store.remove_discount_from_store(id)
        # id: Result = store.add_simple_product_discount(end_time, 0.4, discounted_product='p1', size_of_basket_cond=5)
        # id: int = id.data
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 40
        # store.remove_discount_from_store(id)
        # id: Result = store.add_simple_product_discount(end_time, 0.4, discounted_product='p1',
        #                                                product_list_cond=[{'product_name': 'p2', 'needed_items': 1}])
        # id: int = id.data
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 40
        # store.remove_discount_from_store(id)
        # id: Result = store.add_simple_product_discount(end_time, 0.4, discounted_product='p1',
        #                                                product_list_cond=[{'product_name': 'p2', 'needed_items': 3}])
        # id: int = id.data
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 40
        # store.remove_discount_from_store(id)
        # shop_cart.calc_update_price_of_basket(store.name)
        # assert bas.get_total_value_of_basket() == 40

@pytest.mark.parametrize("product, output", [('p1', 100), ('p2', 20), ('p3', -1)])
def test_calc_price_of_product(product, output):
    assert bas.get_total_price_of_product(product) == output


def test_total_price_of_basket():
    assert bas.get_total_value_of_basket() == 120
    new_bas: Basket = Basket(store.name, None, initial_owner.user_state.user_name)
    assert new_bas.get_total_value_of_basket() == 0


def test_edit_quantity():
    res: Result = bas.edit_quantity_of_product('p1', -1)
    assert not res.succeed
    res: Result = bas.edit_quantity_of_product('p1', 1)
    assert res.succeed
    assert bas.products['p1'].item.quantity == 1
    res: Result = bas.edit_quantity_of_product('p3', 1)
    assert not res.succeed
    res: Result = bas.edit_quantity_of_product('p1', 0)
    assert res.succeed
    assert 'p1' not in bas.products


def test_remove_product_basket():
    assert len(bas.products) == 1
    res: Result = bas.remove_product_from_basket('p3')
    assert not res.succeed
    res: Result = bas.remove_product_from_basket('p2')
    assert res.succeed
    assert len(bas.products) == 0


# shopping cart functions

def test_check_init_shopping_cart():
    with pytest.raises(TypeError):
        ShoppingCart(1, 1)
    with pytest.raises(TypeError):
        ShoppingCart(1)
    ShoppingCart()
    ShoppingCart(TypedDict(str, Basket), False)


def test_calc_value_cart():
    new_cart = ShoppingCart()
    assert new_cart.get_total_value_of_shopping_cart() == 0


def test_add_product():
    with test_flask.app_context():
        s2: Store = Store("store2", "initial 2")
        s2.add_product('p1', 5.0, 10)
        s2.add_product('p2', 10.0, 50)
        res: Result = shop_cart.add_product(s2, 'p1', 1, str(1))
        assert res.succeed and len(shop_cart.baskets) == 2
        res: Result = shop_cart.add_product(s2, 'p3', 1, str(1))
        assert not res.succeed
        res: Result = shop_cart.add_product(s2, 'p1', 1, str(1))
        assert res.succeed and len(shop_cart.baskets) == 2
        res: Result = shop_cart.add_product(s2, 'p2', 1, str(1))
        assert res.succeed and len(shop_cart.baskets) == 2


def test_remove_product():
    with test_flask.app_context():
        bas1 = shop_cart.baskets
        assert len(shop_cart.baskets) == 2
        res: Result = shop_cart.remove_product('store2', 'p3')
        assert not res.succeed
        res: Result = shop_cart.remove_product('store2', 'p1')
        assert res.succeed
        assert len(shop_cart.baskets) == 2


def test_edit_product_quantity_cart():
    with test_flask.app_context():
        assert len(shop_cart.baskets) == 2
        res: Result = shop_cart.edit_product('store2', 'p1', 1)
        assert not res.succeed
