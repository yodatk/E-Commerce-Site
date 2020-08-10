import calendar
import os

import pytest

from src.domain.system.cart_purchase_classes import ShoppingCart, Basket
from src.domain.system.data_handler import DataHandler
from src.domain.system.store_classes import Store
from src.domain.system.store_managers_classes import ShoppingHandler
from src.domain.system.system_admin import SystemAdmin
# from src.domain.system.system_realtime_subjects import StoreAlertHandler
from src.domain.system.users_classes import UserSystemHandler, LoggedInUser, User
from src.domain.system.shopping_policies import LeafSpecificProductQuantity, LeafBasketQuantity, \
    LeafSpecificCategoryQuantity, \
    LeafShoppingDateTime, CompositeAndShoppingPolicy, CompositeOrShoppingPolicy, CompositeXORShoppingPolicy
from src.external.payment_interface.payment_system import MockPaymentSystem
from src.external.supply_interface.supply_system import MockShippingSystem
from src.protocol_classes.classes_utils import TypedList
from src.security.security_system import Encrypter
from datetime import datetime, date
from tests.db_config_tests import test_flask

REGULAR_USER_ID = 4
STORE_MANAGER_USER_ID = 3
USER_MAIL_2 = "user2@user2.mail"
STORE_MANAGER = 'store_manager'
STORE_NAME_1 = "ShuferSal"
PASSWORD = 'Shani123!'
PASSWORD = Encrypter.hash_password(PASSWORD)
OWNER_NAME = "store_owner"
basket: Basket
data_handler: DataHandler = None


@pytest.fixture(scope="session", autouse=True)
def set_up_test(request):
    with test_flask.app_context():
        global data_handler
        try:
            os.remove('db_test.db')
            print("Removed DB")
        except:
            print("Removed db failed")
        data_handler = DataHandler()
        data_handler.create_all(lambda dbi: dbi.init_app(test_flask))
        set_up()


def set_up():
    with test_flask.app_context():
        global basket
        data_handler: DataHandler = DataHandler().get_instance()
        user3 = User(STORE_MANAGER_USER_ID)
        user3.user_state = LoggedInUser(STORE_MANAGER, PASSWORD, USER_MAIL_2)
        user4 = User(REGULAR_USER_ID)
        data_handler.add_or_update_user(REGULAR_USER_ID, user4)
        user3.user_state.is_connected = True
        data_handler.add_or_update_user(STORE_MANAGER_USER_ID, user3)
        _users_handler: UserSystemHandler = UserSystemHandler(data_handler)
        _shopping_handler: ShoppingHandler = ShoppingHandler(data_handler, MockPaymentSystem(), MockShippingSystem())
        _admin_handler: SystemAdmin = SystemAdmin(data_handler)

        user3 = User(STORE_MANAGER_USER_ID)
        user3.user_state = LoggedInUser(STORE_MANAGER, PASSWORD, USER_MAIL_2)
        user4 = User(REGULAR_USER_ID)
        data_handler.add_or_update_user(REGULAR_USER_ID, user4)
        user3.user_state.is_connected = True
        data_handler.add_or_update_user(STORE_MANAGER_USER_ID, user3)

        # Store
        # store1 = Store(STORE_NAME_1, OWNER_NAME, StoreAlertHandler())
        store1 = Store(STORE_NAME_1, OWNER_NAME)

        # Add store to data handler
        data_handler.add_store(store1)

        # Add product to this store
        assert store1.add_product("Milk 1%", 10.0, 50, categories=TypedList(str, ['c1', 'milk']))
        assert store1.add_product("Bred", 10.0, 50)
        assert store1.add_product("Meat", 20.0, 50)
        assert store1.add_product("Oat meal", 10.0, 50)

        # Now the user adds this product to his shopping cart
        assert _shopping_handler.saving_product_to_shopping_cart("Milk 1%", STORE_NAME_1, user3.user_id, 2).succeed
        assert _shopping_handler.saving_product_to_shopping_cart("Bred", STORE_NAME_1, user3.user_id, 1).succeed

        basket = user3.shopping_cart.baskets[STORE_NAME_1]


# LeafSpecificProductQuantity
def test_apply_leaf_product_quantity():
    with test_flask.app_context():
        policy_1 = LeafSpecificProductQuantity(None, None, "Milk 1%", 1, None, None, None, None, None)
        policy_2 = LeafSpecificProductQuantity(None, None, "Milk 1%", None, 3, None, None, None, None)
        policy_3 = LeafSpecificProductQuantity(None, None, "Milk 1%", 1, 3, None, None, None, None)
        assert policy_1.apply(basket)
        assert policy_2.apply(basket)
        assert policy_3.apply(basket)
        policy_4 = LeafSpecificProductQuantity(None, None, "Milk 1%", 3, 5, None, None, None, None)
        assert not policy_4.apply(basket)


# LeafBasketQuantity
def test_apply_leaf_basket_quantity():
    with test_flask.app_context():
        policy_1 = LeafBasketQuantity(4, None, None, None, None, None, None, None, None)
        policy_2 = LeafBasketQuantity(2, None, None, None, None, None, None, None, None)
        policy_3 = LeafBasketQuantity(1, 3, None, None, None, None, None, None, None)
        policy_4 = LeafBasketQuantity(None, 5, None, None, None, None, None, None, None)
        assert not policy_1.apply(basket)
        assert policy_2.apply(basket)
        assert policy_3.apply(basket)
        assert policy_4.apply(basket)


# LeafSpecificCategoryQuantity
def test_leaf_category_quantity():
    with test_flask.app_context():
        global basket
        policy_1 = LeafSpecificCategoryQuantity(None, None, None, None, None, "milk", None, 2, None)
        policy_2 = LeafSpecificCategoryQuantity(None, None, None, None, None, "milk", None, 1, None)
        policy_3 = LeafSpecificCategoryQuantity(None, None, None, None, None, "milk", 1, 2, None)
        policy_4 = LeafSpecificCategoryQuantity(None, None, None, None, None, "milk", 3, None, None)
        assert policy_1.apply(basket)
        assert not policy_2.apply(basket)
        assert policy_3.apply(basket)
        assert not policy_4.apply(basket)


# LeafShoppingDateTime
def test_leaf_time():
    with test_flask.app_context():
        policy_1 = LeafShoppingDateTime(None, None, None, None, None, None, None, None,
                                        calendar.day_name[date.today().weekday()])
        policy_2 = LeafShoppingDateTime(None, None, None, None, None, None, None, None,
                                        "Friday" if calendar.day_name[date.today().weekday()] != "Friday" else "Sunday")
        assert not policy_1.apply(basket)
        assert policy_2.apply(basket)


# CompositeAndShoppingPolicy
def test_composite_and():
    with test_flask.app_context():
        global data_handler
        policy_1 = LeafSpecificProductQuantity(None, None, "Milk 1%", 1, None, None, None, None, None)
        policy_2 = LeafBasketQuantity(2, None, "Milk 1%", 1, None, None, None, None, None)
        composite_and_policies = CompositeAndShoppingPolicy()
        data_handler._dal.add_all([policy_1, policy_2, composite_and_policies], add_only=True)
        data_handler._dal.flush()
        composite_and_policies.add_policy(policy_1)
        composite_and_policies.add_policy(policy_2)
        assert composite_and_policies.apply(basket)
        policy_3 = LeafSpecificCategoryQuantity(None, None, None, None, None, "milk", 3, None, None)
        data_handler._dal.add_all([policy_3], add_only=True)
        data_handler._dal.flush()
        composite_and_policies.add_policy(policy_3)

        assert not composite_and_policies.apply(basket)


# CompositeOrShoppingPolicy
def test_composite_or():
    with test_flask.app_context():
        policy_1 = LeafShoppingDateTime(None, None, None, None, None, None, None, None,
                                        calendar.day_name[date.today().weekday()])
        policy_2 = LeafSpecificCategoryQuantity(4, None, None, None, None, "milk", None, 2, None)
        or_policies = CompositeOrShoppingPolicy()
        data_handler._dal.add_all([policy_1, policy_2, or_policies], add_only=True)
        data_handler._dal.flush()
        or_policies.add_policy(policy_1)
        or_policies.add_policy(policy_2)
        assert or_policies.apply(basket)
        policy_3 = LeafSpecificCategoryQuantity(None, None, None, None, None, "milk", 3, None, None)
        data_handler._dal.add_all([policy_3], add_only=True)
        data_handler._dal.flush()
        or_policies.add_policy(policy_3)
        assert or_policies.apply(basket)


# CompositeXORShoppingPolicy
def test_composite_xor():
    with test_flask.app_context():
        xor_policies = CompositeXORShoppingPolicy()
        policy_1 = LeafSpecificProductQuantity(None, None, "Milk 1%", 1, None, None, None, None, None)
        data_handler._dal.add_all([policy_1, xor_policies], add_only=True)
        data_handler._dal.flush()
        xor_policies.add_policy(policy_1)
        assert xor_policies.apply(basket)

        policy_2 = LeafBasketQuantity(4, None, "electric 1%", 1, None, None, None, None, None)
        data_handler._dal.add_all([policy_2], add_only=True)
        data_handler._dal.flush()
        xor_policies.add_policy(policy_2)
        assert xor_policies.apply(basket)

        policy_3 = LeafShoppingDateTime(None, None, None, None, None, None, None, None,
                                        "Friday" if calendar.day_name[date.today().weekday()] != "Friday" else "Sunday")
        data_handler._dal.add_all([policy_3], add_only=True)
        data_handler._dal.flush()
        xor_policies.add_policy(policy_3)

        assert not xor_policies.apply(basket)


def test_combination_of_composite():
    with test_flask.app_context():
        composite_or = CompositeOrShoppingPolicy()
        composite_xor = CompositeXORShoppingPolicy()
        composite_and = CompositeAndShoppingPolicy()
        combination_1 = CompositeAndShoppingPolicy()
        combination_2 = CompositeXORShoppingPolicy()

        policy_1 = LeafSpecificProductQuantity(None, None, "Milk 1%", 1, None, None, None, None, None)
        policy_2 = LeafBasketQuantity(2, None, None, None, None, None, None, None, None)
        data_handler._dal.add_all(
            [composite_or, composite_xor, composite_and, combination_1, combination_2, policy_1, policy_2],
            add_only=True)
        data_handler._dal.flush()
        composite_and.add_policy(policy_1)
        composite_and.add_policy(policy_2)
        assert composite_and.apply(basket)

        policy_3 = LeafShoppingDateTime(None, None, None, None, None, None, None, None,
                                        "Friday" if calendar.day_name[date.today().weekday() != "Friday"] else "Sunday")
        policy_4 = LeafSpecificCategoryQuantity(None, None, None, None, None, "milk", 3, None, None)
        data_handler._dal.add_all(
            [policy_3, policy_4],
            add_only=True)
        data_handler._dal.flush()
        composite_or.add_policy(policy_3)
        composite_or.add_policy(policy_4)

        combination_1.add_policy(composite_and)
        combination_1.add_policy(composite_or)
        assert combination_1.apply(basket)

        policy_5 = LeafSpecificCategoryQuantity(None, None, None, None, None, "c1", 3, None, None)
        policy_6 = LeafBasketQuantity(5, None, None, None, None, None, None, None, None)
        data_handler._dal.add_all(
            [policy_5, policy_6],
            add_only=True)
        data_handler._dal.flush()
        composite_xor.add_policy(policy_5)
        composite_xor.add_policy(policy_6)

        combination_1.add_policy(composite_xor)
        assert not combination_1.apply(basket)

        combination_2.add_policy(composite_and)
        combination_2.add_policy(composite_xor)
        assert combination_2.apply(basket)

        combination_2.add_policy(composite_or)
        assert not combination_2.apply(basket)
