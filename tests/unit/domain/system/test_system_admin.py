# import pytest
#
# from src.domain.system.cart_purchase_classes import Basket, ShoppingCart
# from src.domain.system.data_handler import DataHandler
# from src.domain.system.store_classes import Store
# from src.domain.system.store_managers_classes import StoreAdministration, ShoppingHandler
# from src.domain.system.system_admin import SystemAdmin
# from src.domain.system.users_classes import User, LoggedInUser, UserSystemHandler
# from src.external.payment_interface.payment_system import MockPaymentSystem
# from src.external.supply_interface.supply_system import MockShippingSystem
# from src.protocol_classes.classes_utils import Result
# from src.security.security_system import Encrypter
#
#
# @pytest.fixture(scope="session", autouse=True)
# def set_up_test(request):
#     set_up()
#
# admin_handler = None
# user_id_make_the_purchase = -1
#
# def set_up():
#     global admin_handler, user_id_make_the_purchase
#     REGULAR_USER_ID = 4
#     STORE_MANAGER_USER_ID = 3
#     USER_MAIL_2 = "user2@user2.mail"
#     STORE_MANAGER = 'store_manager'
#     STORE_NAME_1 = "ShuferSal"
#     PASSWORD = 'Shani123!'
#     PASSWORD = Encrypter.hash_password(PASSWORD)
#     OWNER_NAME = "store_owner"
#
#     data_handler: DataHandler = DataHandler().get_instance()
#     _users_handler: UserSystemHandler = UserSystemHandler(data_handler)
#     _users_handler.register_user(-1, "root_user", '!fldmAd12s',
#                                  "root@root.com")
#     _users_handler.login_user(1)
#     _store_administrator: StoreAdministration = StoreAdministration(data_handler, MockShippingSystem())
#     _shopping_handler: ShoppingHandler = ShoppingHandler(data_handler, MockPaymentSystem())
#     _admin_handler: SystemAdmin = SystemAdmin(data_handler)
#
#     user3 = User(STORE_MANAGER_USER_ID, ShoppingCart())
#     user3.user_state = LoggedInUser(STORE_MANAGER, PASSWORD, USER_MAIL_2)
#     user4 = User(REGULAR_USER_ID, ShoppingCart())
#     data_handler.add_or_update_user(REGULAR_USER_ID, user4)
#     user3.user_state.is_connected = True
#     data_handler.add_or_update_user(STORE_MANAGER_USER_ID, user3)
#
#     # Store
#     store1 = Store(STORE_NAME_1, OWNER_NAME, None)
#
#     # Add store to data handler
#     data_handler.add_store(store1)
#
#     # Add product to this store
#     assert store1.add_product(OWNER_NAME, "abc", 4.0, 5)
#     assert _shopping_handler.saving_product_to_shopping_cart("abc", STORE_NAME_1, user3.user_id, 1).succeed
#     user_id_make_the_purchase = user3.user_id
#     assert _shopping_handler.make_purchase_of_all_shopping_cart(user3.user_id, 1111111111111111).succeed
#     admin_handler = _admin_handler
#
# def test_watch_all_purchases():
#     sa: SystemAdmin = admin_handler
#     res: Result = sa.watch_all_purchases(1)
#     assert res.succeed
#     assert res.data[0]['user_id'] == user_id_make_the_purchase
