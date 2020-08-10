import copy
import os

from src.communication.notification_handler import TestEmitter, NotificationHandler
from src.domain.system.data_handler import DataHandler
from src.domain.system.system_facade import SystemFacade
from src.external.publisher import Publisher
from src.protocol_classes.classes_utils import Result, TypedDict, TypedList
from src.service.shopping_interface.shopping_handler import ShoppingHandler
from src.service.store_inventory_interface.inventory_handler import InventoryHandler
from src.service.system_adminstration.sys_admin_handler import SysAdminHandler
from src.service.user_handler.user_handler import UserHandler
from tests.acceptance.bridge.proxy_bridge import ProxyBridge, AcceptanceTestError
from src.external.supply_interface.supply_system import MockShippingSystem
from src.external.payment_interface.payment_system import MockPaymentSystem
from tests.db_config_tests import test_flask


class TestNotificationHandler(NotificationHandler):

    def __init__(self):
        super().__init__(TestEmitter())
        self.notifications = TypedDict(str, TypedList)

    def _emit(self, user_name: str, msg: str) -> None:
        if user_name in self.notifications.keys():
            self.notifications[user_name].append(msg)
        else:
            self.notifications[user_name] = TypedList(str)


class RealBridge(ProxyBridge):

    def __init__(self):
        self.sys_facade = SystemFacade(MockPaymentSystem(), MockShippingSystem())
        self.notification_handler: NotificationHandler = TestNotificationHandler()
        self.user_handler = UserHandler(self.notification_handler)
        self.shopping_handler = ShoppingHandler()
        self.inventor_handler = InventoryHandler()
        self.system_handler = SysAdminHandler()
        self.data_handler = DataHandler.get_instance()

        Publisher.get_instance().set_communication_handler(self.notification_handler)

    def register(self, user_id: int, email: str, username: str, password: str):
        with test_flask.app_context():
            res: Result = self.user_handler.register(user_id, username, password, email)
            if res.succeed:
                user_id: int = res.requesting_id
                self.notification_handler.add_observer(username)
                return user_id
            else:
                raise AcceptanceTestError("RegisterPage failed:\n "
                                          f"Parameters- Email: {email}, "
                                          f"Username: {username}, Password: {password}")

    def login(self, username: str, password: str, user_id: int = -1):
        with test_flask.app_context():
            res: Result = self.user_handler.login(user_id, username, password)
            if res.succeed:
                user_id: int = res.requesting_id
                self.notification_handler.connect(username)
                return user_id
            else:
                raise AcceptanceTestError("LoginPage failed:\n "
                                          "Parameters- "
                                          f"Username: {username}, Password: {password}")

    def logout(self, user_id: int, username: str):
        with test_flask.app_context():
            res: Result = self.user_handler.logout(user_id)
            if res.succeed:
                user_id: int = res.requesting_id
                self.notification_handler.disconnect(username)
                return user_id
            else:
                return -1

    def view_user_purchases(self, user_id: int):
        with test_flask.app_context():
            res: Result = self.shopping_handler.watch_user_purchases(user_id)
            if not res.succeed:
                raise AcceptanceTestError("View Purchases failed:\n "
                                          f"Parameter- User_id: {user_id}")
            else:
                return res.data

    def view_store_purchases(self, user_id: int, store_name: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.watch_store_purchase(user_id, store_name)
            if not res.succeed:
                raise AcceptanceTestError("View Store Purchases failed:\n "
                                          f"Parameter- User_id: {user_id}, store_name {store_name}")
            else:
                return res.data

    # -------------------------------Shopping interface-----------------------------------

    """ :param 1) item name 2) store name 
        :returns tuple (name, store, category, price) on success 
                and raises AcceptanceTestException on fail
    """

    def view_item(self, user_id: int, store_name: str, item_name: str):
        with test_flask.app_context():
            res: Result = self.shopping_handler.watch_info_on_product(user_id, store_name, item_name)
            if res.succeed:
                item_dictionary = res.data
                if len(item_dictionary) == 0:
                    raise AcceptanceTestError("View item failed:\n "
                                              "Parameters- "
                                              f"user_id {user_id}, store_name {store_name}, item_name {item_name}")
                else:
                    return res.requesting_id, res.data
            else:
                raise AcceptanceTestError("View item failed:\n "
                                          "Parameters- "
                                          f"user_id {user_id}, store_name {store_name}, item_name {item_name}")

    """ :param: store name- given by user 
        :returns- if success: tuple (store name,initial_owner, inventory)
                    inventory= list of items (item name, category, price)
                  else raises "AcceptanceTestException" with message 
    """

    def view_store(self, user_id: str, store_name: str):
        with test_flask.app_context():
            res: Result = self.shopping_handler.watch_info_on_store(user_id, store_name)
            store_dictionary = res.data
            if res.succeed:
                if len(store_dictionary) == 0:
                    raise AcceptanceTestError("View Store failed:\n "
                                              f"Parameters store_name {store_name}".format
                                              (store_name=store_name))
                return res.requesting_id, store_dictionary
            else:
                raise AcceptanceTestError("View store failed:\n "
                                          "Parameters- "
                                          f"user_id {user_id}, store_name {store_name}"
                                          .format(user_id=user_id, store_name=store_name))

    """ :param- item name, stores_names, categories , brands ,min_price ,max_price
            *important: unused criteria will contain empty string
        : returns- number of hits
            raises "AcceptanceTestException" with message if failure
    """

    def search_for_items(self, user_id: int, item_name: str, stores_names, categories, brands, min_price,
                         max_price):
        with test_flask.app_context():
            res: Result = self.shopping_handler.search_products(user_id, item_name, stores_names, categories, brands,
                                                                min_price, max_price)
            if res.succeed:
                item_list = res.data
                return res.requesting_id, item_list
            else:
                raise AcceptanceTestError("Search for items failed:\n "
                                          "Parameters- "
                                          f"User_id {user_id}, Item_name {item_name}, Stores_name {stores_names}, Category {categories}"
                                          f"Brand {brands}, Min_price {min_price}, Max_price {max_price}")
                # .format(user_id=user_id, item_name=item_name, stores_name=stores_names,
                #         category=categories,
                #         brand=brands, min_price=min_price, max_price=max_price))

    """ :param- item name, store name and quantity
        :returns - void.  raises "AcceptanceTestException" with message if failure
    """

    def add_item_to_cart(self, user_id: int, store_name: str, item_name: str, quantity: int):
        with test_flask.app_context():
            res: Result = self.shopping_handler.saving_product_to_shopping_cart(item_name, store_name, user_id,
                                                                                quantity)
            if not res.succeed:
                raise AcceptanceTestError("Add items to cart failed failed:\n "
                                          "Parameters- "
                                          f"User_id {user_id}, Item_name {item_name}, Store_name {store_name}, Quantity {quantity}")

            return res.requesting_id

    def edit_item_in_cart(self, user_id: int, store_name: str, item_name: str, quantity: int):
        with test_flask.app_context():
            res: Result = self.shopping_handler.editing_quantity_shopping_cart_item(item_name, store_name, user_id,
                                                                                    quantity)
            if not res.succeed:
                raise AcceptanceTestError("Edit item in cart failed:\n "
                                          "Parameters- "
                                          f"User_id {user_id}, Item_name {item_name}, Store_name {store_name}, Quantity {quantity}")
            return res.requesting_id

    def view_cart(self, user_id: int):
        with test_flask.app_context():
            res: Result = self.shopping_handler.watch_shopping_cart(user_id)
            if res.succeed:
                return res.requesting_id, res.data
            else:
                raise AcceptanceTestError("View cart failed failed:\n "
                                          f"Parameter- User_id {user_id}")

    def purchase(self, user_id: int, credit_card_number: int, data_dict):  # , purchase_entry, quantity):
        with test_flask.app_context():
            res: Result = self.shopping_handler.purchase_items(user_id, **data_dict)
            if not res.succeed:
                raise AcceptanceTestError("Purchase items in cart failed:\n "
                                          f"Parameters- User_id {user_id}, Credit card "
                                          f"{credit_card_number}")
            return res
            # else:
            # a = copy.deepcopy(purchase_entry)
            # a['quantity'] = quantity
            # data_dict.set_up_shopping_data["Purchases"].append({"user_id": user_id, "details": a})

    def add_admin(self, user_id: int, to_add: str):
        with test_flask.app_context():
            res: Result = self.system_handler.add_admin(user_id, to_add)
            return res.succeed

    def is_admin(self, username: str):
        with test_flask.app_context():
            return self.user_handler.is_admin(username)

    # def cancel_pre_purchase(self, user_id):
    #     res: Result = self.shopping_handler.cancel_pre_purchase(user_id)
    #     if not res.succeed:
    #         raise AcceptanceTestError("Cancel prepurchase failed:\n "
    #                                   f"Parameters- User_id {user_id}")

    # ------------------------------Inventory--------------------------------
    """ :params- 1) name of store to open 2) owner's username 
        ::returns- void. raises exception if unsuccessful
    """

    def open_store(self, user_id: int, store_name: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.opening_a_new_store(user_id, store_name)
            if not res.succeed:
                raise AcceptanceTestError("Open Store failed:\n "
                                          f"Parameters: Store_name {store_name}, Owner_user_id {user_id}")

    """ :params- all item's fields
        :returns- void. raises exception if unsuccessful
    """

    def add_item_to_store(self, user_id: int, store_name: str, item_name: str, category: str, brand: str, price: float,
                          quantity: int):
        with test_flask.app_context():
            category_lst = None if category is None else [category]
            res: Result = self.inventor_handler.add_product_to_store(user_id, store_name, item_name, price, quantity,
                                                                     brand,
                                                                     category_lst)
            if not res.succeed:
                raise AcceptanceTestError("Add item to store failed:\n "
                                          f"Parameters: User_id {user_id} Store_name {store_name}, "
                                          f"Item_name {item_name}, Category {category}, Brand {brand}, Price {price},"
                                          f" Quantity {quantity}")

    """ :params- store name , item name
        :returns- void. raises exception if unsuccessful
    """

    def remove_item_from_store(self, user_id: int, store_name: str, item_name: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.remove_product_to_store(user_id, store_name, item_name)
            if not res.succeed:
                raise AcceptanceTestError("Remove item from store failed:\n "
                                          f"Parameters: User_id {user_id} Store_name {store_name}, "
                                          f"Item_name {item_name}")

    """ :param- all item's fields (where no update was done there is an empty string)
        :returns- void. raises exception if unsuccessful
    """

    def update_item_in_store(self, user_id: int, store_name: str, item_name: str, category: str, brand: str,
                             price: float, quantity: int):
        with test_flask.app_context():
            category_lst = None if category is None else [category]
            res: Result = self.inventor_handler.edit_existing_product_in_store(user_id, store_name, item_name, brand,
                                                                               price,
                                                                               quantity, category_lst)
            if not res.succeed:
                raise AcceptanceTestError("Update item in store failed:\n "
                                          f"Parameters: User_id {user_id} Store_name {store_name}, "
                                          f"Item_name {item_name}, Category {category}, Brand {brand}, Price {price}")

    """ :param- 1) store name, 2) current store owner 3) username of person to appoint to owner
        :returns- void. raises exception if unsuccessful
    """

    def appoint_store_owner(self, store_owner_id: int, store_name: str, to_appoint_username: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.adding_new_owner_to_store(store_owner_id, to_appoint_username,
                                                                          store_name)
            if not res.succeed:
                raise AcceptanceTestError("Appoint store owner failed:\n "
                                          f"Parameters: Store_owner_id {store_owner_id}, "
                                          f"To_appoint_username {to_appoint_username} Store_name {store_name} ")
            return res

    #
    # class Approval(enum.Enum):
    #     approved = 1
    #     declined = 2
    #     pending = 3

    def approve_owner(self, user_id, username, store_name):
        """
        approoving to an Appointment agreement of a pending owner
        :param user_id: id of the requesting user
        :param username: name of the user to approve as owner
        :param store_name: name of the store
        :return: Result with process on info
        """
        with test_flask.app_context():
            res: Result = self.shopping_handler.respond_new_owner_to_store(user_id, username, store_name, 1)
            if not res.succeed:
                raise AcceptanceTestError("approoving store owner failed:\n "
                                          f"Parameters: Store_owner_id {user_id}, "
                                          f"To_appoint_username {username} Store_name {store_name} ")
            return res

    def deny_owner(self, user_id, username, store_name):
        """
        denying to an Appointment agreement of a pending owner
        :param user_id: id of the requesting user
        :param username: name of the user to approve as owner
        :param store_name: name of the store
        :return: Result with process on info
        """
        with test_flask.app_context():
            res: Result = self.shopping_handler.respond_new_owner_to_store(user_id, username, store_name, 2)
            if not res.succeed:
                raise AcceptanceTestError("denying store owner failed:\n "
                                          f"Parameters: Store_owner_id {user_id}, "
                                          f"To_appoint_username {username} Store_name {store_name} ")
            return res

    """ :param- 1) store name, 2) current store owner 3) username of person to appoint to manager
        :returns- void. raises exception if unsuccessful
    """

    def appoint_store_manager(self, store_name: str, store_owner_id: int, to_appoint_username: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.adding_new_manager_to_store(store_owner_id, to_appoint_username,
                                                                            store_name)
            if not res.succeed:
                raise AcceptanceTestError("Appoint store manager failed:\n "
                                          f"Parameters: Store_owner_id {store_owner_id}, "
                                          f"To_appoint_username {to_appoint_username} Store_name {store_name} ")

    def change_manager_permissions(self, store_name: str, store_owner_id: int, store_manager_name: str,
                                   can_manage_inventory: bool, appoint_new_store_owner: bool,
                                   appoint_new_store_manager: bool,
                                   edit_management_options_for_appoints: bool,
                                   remove_appointee_store_manager: bool, watch_purchase_history: bool,
                                   open_and_close_store: bool, can_manage_discounts: bool):
        with test_flask.app_context():
            res: Result = self.inventor_handler.editing_permissions_to_store_manager(store_owner_id, store_manager_name,
                                                                                     store_name,
                                                                                     can_manage_inventory,
                                                                                     appoint_new_store_owner,
                                                                                     appoint_new_store_manager,
                                                                                     watch_purchase_history,
                                                                                     open_and_close_store,
                                                                                     can_manage_discounts)
            if not res.succeed:
                raise AcceptanceTestError("Edit store manager permissions failed:\n "
                                          f"Parameters: Store_owner_id {store_owner_id}, Store_manager_name {store_manager_name}, Store_name {store_name},"
                                          f"Can_manage_inventory {can_manage_inventory}, Appoint_new_store_owner {appoint_new_store_owner}, "
                                          f"Appoint_new_store_manager {appoint_new_store_manager}, "
                                          f"Edit_management_options_for_appoints {edit_management_options_for_appoints},"
                                          f"Remove_appointee_store_manager {remove_appointee_store_manager}, Watch_purchase_history {watch_purchase_history},"
                                          f" Open_and_close_store {open_and_close_store}"
                                          f" can_manage_discounts {can_manage_discounts}")

    """ :param- 1) store name, 2) current store owner 3) username of manager to remove 
        :returns - true if removed successfully and false otherwise 
    """

    def remove_store_manager(self, store_name: str, store_owner_id: int, store_manager_name: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.removing_store_manager(store_owner_id, store_manager_name, store_name)
            if not res.succeed:
                raise AcceptanceTestError("Remove store manager failed:\n"
                                          f"Parameters: store_name {store_name}, store_owner_id {store_owner_id},"
                                          f"store_manager_name {store_manager_name}")

    def remove_store_owner(self, store_name: str, store_owner_id: int, store_manager_name: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.removing_store_owner(store_owner_id, store_manager_name, store_name)
            if not res.succeed:
                raise AcceptanceTestError("Remove store owner failed:\n"
                                          f"Parameters: store_name {store_name}, store_owner_id {store_owner_id},"
                                          f"store_owner_name {store_manager_name}")

    def close_store(self, owner_id: int, store_name: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.close_store(owner_id, store_name)
            if not res.succeed:
                raise AcceptanceTestError("Close store failed\n:"
                                          f"Parameters Owner_id {owner_id}, Store_name {store_name}")
            return True

    def add_discount(self, user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                     overall_product_price, overall_category_price, overall_product_quantity, overall_category_quantity,
                     up_to_date, basket_size):
        with test_flask.app_context():
            res: Result = self.inventor_handler.add_discount(user_id, store_name, product_name, discount_type, percent,
                                                             category, free_per_x,
                                                             overall_product_price, overall_category_price,
                                                             overall_product_quantity, overall_category_quantity,
                                                             up_to_date, basket_size)
            if not res.succeed:
                raise AcceptanceTestError("Add discount failed")
            return res.data

    def edit_discount(self, user_id, discount_id, store_name, product_name, discount_type, percent, category,
                      free_per_x, overall_product_price,
                      overall_category_price, overall_product_quantity, overall_category_quantity,
                      up_to_date, basket_size):
        with test_flask.app_context():
            res: Result = self.inventor_handler.edit_discount(user_id, discount_id, store_name, product_name,
                                                              discount_type,
                                                              percent, category,
                                                              free_per_x, overall_product_price,
                                                              overall_category_price, overall_product_quantity,
                                                              overall_category_quantity,
                                                              up_to_date, basket_size)
            if not res.succeed:
                raise AcceptanceTestError("Edit discount failed")

    def remove_discount(self, user_id: int, discount_id: int, store_name: str):
        with test_flask.app_context():
            res: Result = self.inventor_handler.remove_discount(user_id, discount_id, store_name)
            if not res.succeed:
                raise AcceptanceTestError("Remove discount failed")

    def add_policy(self, user_id, storename, min_basket_quantity, max_basket_quantity, product_name,
                   min_product_quantity,
                   max_product_quantity, category, min_category_quantity, max_category_quantity, day):
        with test_flask.app_context():
            res: Result = self.inventor_handler.add_policy(user_id, storename, min_basket_quantity, max_basket_quantity,
                                                           product_name, min_product_quantity,
                                                           max_product_quantity, category, min_category_quantity,
                                                           max_category_quantity, day)
            if not res.succeed:
                raise AcceptanceTestError("Add policy failed")
            return res.data

    def edit_policy(self, user_id, storename, to_edit, min_basket_quantity, max_basket_quantity, product_name,
                    min_product_quantity, max_product_quantity, category, min_category_quantity,
                    max_category_quantity, day):
        with test_flask.app_context():
            res: Result = self.inventor_handler.edit_policy(user_id, storename, to_edit, min_basket_quantity,
                                                            max_basket_quantity,
                                                            product_name, min_product_quantity,
                                                            max_product_quantity, category, min_category_quantity,
                                                            max_category_quantity, day)
            if not res.succeed:
                raise AcceptanceTestError("Edit policy failed")
            return res.data

    def remove_policy(self, user_id, store_name, to_remove):
        with test_flask.app_context():
            res: Result = self.inventor_handler.remove_policy(user_id, store_name, to_remove)
            if not res.succeed:
                raise AcceptanceTestError("Remove policy failed")

    # -------------------------------------SYSTEM ADMIN---------------------------

    def view_system_purchases(self, user_id):
        with test_flask.app_context():
            res: Result = self.system_handler.watch_all_purchases(user_id)
            if not res.succeed:
                raise AcceptanceTestError("View System Purchases failed\n:"
                                          f"Parameters user_id {user_id}")
            else:
                return res.data

    def view_as_admin_user_purchases(self, user_id, username):
        with test_flask.app_context():
            res: Result = self.system_handler.watch_user_purchases(user_id, username)
            if not res.succeed:
                raise AcceptanceTestError("View System Purchases failed\n:"
                                          f"Parameters user_id {user_id}")
            else:
                return res.data

    def view_as_admin_store_purchases(self, user_id, store_name):
        with test_flask.app_context():
            res: Result = self.system_handler.watch_store_purchase(user_id, store_name)
            if not res.succeed:
                raise AcceptanceTestError("View System Purchases failed\n:"
                                          f"Parameters user_id {user_id}")
            else:
                return res.data

    # -------------------------------------SETUP FUNCTIONS---------------------------

    # NOTICE LOGGED OUT
    def register_login_user_just_name(self, user_id: int, username: str):
        email = f"{username}@gmail.com"
        password = "passworD1$"
        user_id = self.register(user_id, email, username, password)
        print(f"SET UP USER : email = {email}, username = {username} , password = {password}")
        return user_id, password

    """ :param- test case id
        :returns username (notice LOGGED OUT)
    """

    def setup_anonymous_user(self, user_id: int, test_case: str):
        username: str = f"user_{test_case}"
        user_id, password = self.register_login_user_just_name(user_id, username)
        return username, password

    """ :param- test case id
        :returns store name and owner name (NOT logged in)
    """

    def setup_anonymous_store(self, user_id: int, test_case: str):
        owner, password = self.setup_anonymous_user(user_id, test_case)
        user_id = self.login(owner, password)
        store_name: str = f"store_{test_case}"
        self.open_store(user_id, store_name)
        self.logout(user_id, owner)
        print(f"SET UP STORE : name = {store_name} , owner = {owner}")
        return store_name, owner, password

    """
        :params- test case id
        :returns- name of store, username of store owner, store manager (they are logged out!!)
                   set up for this test
                        raises exception if register/login/store open/appoint manager fail
    """

    def setup_store_with_manager_setup_anonymous(self, user_id: int, test_case: str):
        manager_username, manager_password = self.setup_anonymous_user(user_id,
                                                                       f"{test_case}_manager")
        store, owner, owner_password = self.setup_anonymous_store(-1, test_case)
        owner_id = self.login(owner, owner_password)
        self.appoint_store_manager(store, owner_id, manager_username)
        self.logout(owner_id, owner)
        print(f"SET UP STORE : name = {store} , owner = {owner}, manager = {manager_username}")
        return store, owner, owner_password, manager_username, manager_password

    """
        :params- store_name, owner user, owner password
        :returns- void. user is logged out at end of function
            raises exception if login/store open fail
    """

    def setup_store_with_other_owner_setup_anonymous(self, user_id: int, test_case: str):
        other_owner_username, other_owner_password = self.setup_anonymous_user(user_id,
                                                                               f"{test_case}_manager")
        store, owner, owner_password = self.setup_anonymous_store(-1, test_case)
        owner_id = self.login(owner, owner_password)
        self.appoint_store_owner(owner_id, store, other_owner_username)
        self.logout(owner_id, owner)
        print(f"SET UP STORE : name = {store} , owner = {owner}, manager = {other_owner_username}")
        return store, owner, owner_password, other_owner_username, other_owner_password

    """
        :params- store_name, owner user, owner password
        :returns- void. user is logged out at end of function
            raises exception if login/store open fail
    """

    def shopping_setup_stores(self, store_name: str, user: str, password):
        user_id = self.login(user, password)
        try:
            self.open_store(user_id, store_name)
        except AcceptanceTestError as e:
            self.logout(user_id, user)
            raise e
        finally:
            self.logout(user_id, user)

    def shopping_setup_item(self, store_owner: str, password: str, store_name: str, item_name: str, category: str,
                            brand: str, price: float,
                            quantity: int):
        user_id = -1
        try:
            user_id = self.login(store_owner, password)
            self.add_item_to_store(user_id, store_name, item_name, category, brand, price, quantity)
        except AcceptanceTestError as e:
            self.logout(user_id, store_owner)
            raise e
        finally:
            self.logout(user_id, store_owner)

    def setup_shopping(self, data_dictionary):
        insert_functions = {"Users": lambda email, username, password: self.register(-1, email, username, password),
                            "Stores": self.shopping_setup_stores,
                            "Inventory": self.shopping_setup_item}
        try:
            for table_name in data_dictionary:
                for row in data_dictionary[table_name]:
                    params = list(row.values())
                    if table_name == "Inventory":
                        for store in data_dictionary["Stores"]:
                            if store["store_name"] == params[0]:
                                owner_username: str = store["owner"]
                                password: str = store["password"]
                                insert_functions[table_name](owner_username, password, *params)
                                break
                    else:
                        insert_functions[table_name](*params)
        except AcceptanceTestError as e:
            raise AcceptanceTestError(f"Error caught in setup_shopping.\n {str(e)}")
