from datetime import datetime

from src.domain.system.DAL import DAL
from src.domain.system.persistency_handler import PersistencyHandler
from src.domain.system.data_handler import DataHandler
from src.domain.system.store_managers_classes import StoreAdministration, ShoppingHandler
from src.domain.system.system_admin import SystemAdmin
from src.domain.system.users_classes import UserSystemHandler, LoggedInUser
from src.external.payment_interface.payment_system import _PaymentSystem, MockPaymentSystem
from src.external.supply_interface.supply_system import _ShippingSystem, MockShippingSystem
from src.protocol_classes.classes_utils import Result, TypedList, TypeChecker


class AuthException(Exception):
    """Exceptions regarding restrictions"""


class SystemFacade:
    __instance = None

    def __init__(self, payment_system: _PaymentSystem, supply_system: _ShippingSystem):
        data_handler: DataHandler = DataHandler.get_instance()
        self._dal: DAL = DAL.get_instance()
        self._users_handler: UserSystemHandler = UserSystemHandler(data_handler)
        # self._users_handler.register_user(-1, "root_user", 'passworD1$',
        #                                  "root@root.com")  # registering_default_admin
        self._persistency_handler = PersistencyHandler(data_handler)
        self._store_administrator: StoreAdministration = StoreAdministration(data_handler)
        self._shopping_handler: ShoppingHandler = ShoppingHandler(data_handler, payment_system, supply_system)
        self._admin_handler: SystemAdmin = SystemAdmin(data_handler)
        # check connection to external systems
        if (not payment_system.check_connection()) or (not supply_system.check_connection()):
            exit(-1)
        if SystemFacade.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            SystemFacade.__instance = self

    def send_db_status_subject(self, dalSubject):
        self._dal.set_subject(dalSubject)

    def insert_some_fun(self):
        self._persistency_handler.insert_some_fun()

    def commit_session(self):
        self._persistency_handler.commit_session()

    @staticmethod
    def get_instance():
        """ Static access method. """
        if SystemFacade.__instance is None:
            SystemFacade(MockPaymentSystem(), MockShippingSystem())
        return SystemFacade.__instance

    def create_all(self, init_app):
        return self._persistency_handler.create_all(init_app)

    def get_store_by_name(self, storename: str):
        return self._users_handler.get_store_by_name(storename)

    def register(self, user_id: int, username: str, password: str, email: str):
        """
        registering a user if is not already in the system
        :param user_id: (int) user id of the user to register
        :param username: (str) username of the user to register
        :param password: (str) encrypted password of the user to register
        :param email: (str) email of the user to register
        :return: Result object contains True / False if the operation succeeded, user_id and message
        """
        return self._users_handler.register_user(user_id, username, password, email)

    def login(self, user_id: int, user):
        """
        logging a user if exists
        :param user_id: (int) user_id of the user to login
        :return: Result object contains True / False if the operation succeeded, user_id and message
        """
        return self._users_handler.login_user(user_id, user)

    def logout(self, user_id: int):
        """
        logging out the given username
        :param user_id: (int) user id of the user that wants to logout.
        :return: Result object with info on the process
        """
        return self._users_handler.logout(user_id)

    def user_state_is_none(self, user_id: int):
        return self._users_handler.user_state_is_none(user_id)

    def get_user_stored_password_by_id(self, user_id: int):
        """
        :param user_id: (int) user id of the wanted user
        :return:  stored password of user, if exists
        """
        return self._users_handler.get_user_stored_password(user_id)

    def get_user_by_username_as_result(self, username: str) -> Result:
        return self._users_handler.get_user_by_username_as_result(username)

    def check_username_exist(self, username: str):
        """
        :param user_id: (int) user id of the wanted user
        :param username:  (str) user name of the wanted user
        :return: Result object with info on the process
        """
        return self._users_handler.check_username_already_exist(username)

    def watch_info_on_store(self, username: str, store_name: str):
        """
        watch information on specific store
        :param user_id: (int) id of the requesting user
        :param store_name: (str) the store name
        :return: Store info
        """
        return self._shopping_handler.watch_info_on_store(username, store_name)

    def watch_info_on_product(self, user_id: int, store_name: str, product_name: str):
        """
        watch information on specific store
        :param store_name: (str) the store name
        :param user_id: (int) id of the requesting user
        :param product_name: (str) the product name
        :return: product info from store
        """
        return self._shopping_handler.watch_info_on_product(user_id, product_name, store_name)

    def get_all_stores_of_user(self, username: str):
        """
        get all the stores that the current user have administration permission in
        :param user_id: (int) id of the user
        :return: list of stores that the current user is managing or owning
        """
        return self._store_administrator.get_all_stores_of_user(username)

    def get_all_products_of_store(self, user_id: int, store_name: str):
        """
        get all the products of the current store
        :param user_id: (int) id of the user
        :param store_name: (str) name of store
        :return: list of products of the current store
        """
        return self._store_administrator.get_all_products_of_store(user_id, store_name)

    def watch_shopping_cart(self, user_id: int):
        """
        retrieve the shopping cart of the user
        :param user_id: (int) user id of the user to register
        :return: list of products in the shopping cart
        """
        return self._shopping_handler.display_products_in_shopping_cart(user_id)

    def search_stores(self, user_id: int, store_search_name: str):
        """
        searching all stores that contains the given name
        :param user_id:(int) user searching
        :param store_search_name:(str) name to search
        :return: all the stores that contains this prefix as dictionaries
        """
        return self._shopping_handler.search_stores(user_id, store_search_name)

    def search_products(self, user_id: int, product_name: str, stores_names: list = None, categories: list = None,
                        brands: list = None, min_price: float = None, max_price: float = None):
        """
        search in all stores for products that answers the search conditions
        :param user_id: (str) id of the user name requesting
        :param product_name: (str) name of the products
        :param stores_names: (TypedList of str) name of wanted stores
        :param categories: (list of str) names of categories the products need to belong to (at least on of them)
        :param brands: (list of str) names of brands the product need to have (at least one)
        :param min_price: (float) minimum price for the product
        :param max_price: (float) maximum price for the product
        :return: list of Products that matching the desired the search conditions
        """
        if type(user_id) != int:
            return Result(False, -1, "wrong type for user-id", None)
        try:
            stores_names = TypedList(str, stores_names) if stores_names is not None else None
            categories = TypedList(str, categories) if categories is not None else None
            brands = TypedList(str, brands) if brands is not None else None
            if (min_price is not None and not TypeChecker.check_for_positive_number([min_price])) or (
                    max_price is not None and not TypeChecker.check_for_positive_number([max_price])):
                return Result(False, user_id, "given lists are not valid for search", None)
        except TypeError:
            return Result(False, user_id, "given lists are not valid for search", None)

        return self._shopping_handler.search_products(user_id, product_name, stores_names=stores_names,
                                                      categories=categories,
                                                      brands=brands, min_price=min_price, max_price=max_price)

    def saving_product_to_shopping_cart(self, product_name: str, store_name: str,
                                        user_id: int, quantity: int):
        """
        saving the given product in shopping cart
        :param product_name: (str) name of the desired product
        :param store_name: (str) name of the store that have the product
        :param user_id: (int) user_id of the user who wants to add the item
        :param quantity: (int) quantity of the product
        :return: Result obj: True,empty message if succeeded, otherwise: False, indicative messages about
                    the errors.
        """
        return self._shopping_handler.saving_product_to_shopping_cart(product_name, store_name, user_id, quantity)

    def removing_item_from_shopping_cart(self, product_name: str, store_name: str, user_id: int):
        """
        removing a given item from shopping item
        :param user_id: (int) user id of user that wants to remove the product
        :param product_name: (str) name of product to remove
        :param store_name: (str) name of store
        :return Result with True, empty message if Succeeded, Result with False, error message otherwise
        """
        if user_id == -1:
            return Result(False, user_id, "first action in system can't be removal, the cart is already empty", None)
        return self._shopping_handler.removing_item_from_shopping_cart(product_name, store_name, user_id)

    def editing_quantity_shopping_cart_item(self, product_name: str, store_name: str, user_id: int, new_quantity: int):
        """
        editing quantity of item in shopping cart
        :param product_name: (str) product name to edit
        :param store_name: (str) store name where the product belong
        :param user_id: (int) user_id of the user that want to edit the quantity
        :param new_quantity:(int) new quantity of the product
        :return: Result with True, empty message if Succeeded, Result with False, error message otherwise
        """
        if user_id == -1:
            return Result(False, user_id, "first action in system can't be editing, the cart is already empty", None)
        return self._shopping_handler.editing_quantity_shopping_cart_item(product_name, store_name, user_id,
                                                                          new_quantity)

    def combine_discounts(self, user_id: int, store_name: str, discounts_list_id: list, operator: str):
        """
        combine several discount to one complex discount
        :param user_id: (int) user id of the user that want to edit the quantity
        :param store_name: (str) store name where the product belong
        :param discounts_list_id: list of discount id to combine
        :param operator: chosen operator - XOR, AND or OR
        :return: Result with info of the process
        """
        return self._store_administrator.combine_discounts(user_id, store_name, discounts_list_id, operator)

    def opening_a_new_store(self, user_id: int, store_name: str):
        """
        opening a new store by a registered user
        :param user_id:(int) id of the user who wants to open a store
        :param store_name: (str) name of the store to open
        :return:  Result object with info on the process
        """
        if not TypeChecker.check_for_non_empty_strings([store_name]) or not TypeChecker.check_for_positive_number(
                [user_id]):
            return Result(False, user_id if type(user_id) == int else -1,
                          "username and store name need to be of type string and cannot be empty", None)
        res: Result = self._store_administrator.open_a_new_store(user_id, store_name=store_name.strip())
        return res

    def opening_existing_store(self, user_id: int, store_name: str):
        """
        opening a new store by a registered user
        :param user_id:(int) id of the user who wants to open a store
        :param store_name: (str) name of the store to open
        :return: Result object with info on the process
        """
        if not TypeChecker.check_for_non_empty_strings([store_name]) or not TypeChecker.check_for_positive_number(
                [user_id]):
            return Result(False, user_id if type(user_id) == int else -1,
                          "username  and store name need to be of type string and cannot be empty",
                          None)
        return self._store_administrator.open_existing_store(user_id,
                                                             store_name=store_name)

    def add_product_to_store(self, user_id: int, store_name: str, product_name: str, base_price: float, quantity: int,
                             brand: str = "", categories: TypedList = None, description: str = ""):
        """
        adding new product to store
        :param user_id: (int) id of the user that is adding new product
        :param store_name:(str) name of the store
        :param product_name: (str) name of the product that is adding to the inventory of the store
        :param base_price: (float) base price for the new product
        :param quantity:(int) quantity of that product to add to the store
        :param brand:(str) brand of the product
        :param categories:(list of str) categories the product is fit in
        :param description:(str) description of the product
        :return: Result object with info on the process
        """
        if not TypeChecker.check_for_non_empty_strings([store_name, product_name]) or type(description) != str:
            return Result(False, user_id, "store name need to be of type string and cannot be empty", None)
        elif not TypeChecker.check_for_positive_number([user_id, base_price, quantity]):
            return Result(False, user_id if type(user_id) == int else -1,
                          "base price and quantity must be a positive number", None)
        elif type(brand) != str:
            return Result(False, user_id, "invalid brand name", None)
        elif categories is not None and (not isinstance(categories, TypedList) or not categories.check_types(
                str) or not TypeChecker.check_for_non_empty_strings(categories)):
            return Result(False, user_id, "invalid categories list", None)
        else:
            return self._store_administrator.add_existing_in_inventory_product_to_store(user_id, store_name.strip(),
                                                                                        product_name.strip(),
                                                                                        base_price, quantity, brand,
                                                                                        categories, description)

    def remove_product_from_store(self, user_id: int, store_name: str, product_name: str):
        """
        removing existing product from store
        :param user_id: (int) id of the user that is adding new product
        :param store_name:(str) name of the store
        :param product_name: (str) name of the product that is adding to the inventory of the store
        :return: True if succeeded, False otherwise
        """
        if not TypeChecker.check_for_positive_number([user_id]):
            return Result(False, user_id if type(user_id) == int else -1, "wrong types", None)
        if not TypeChecker.check_for_non_empty_strings([store_name, product_name]):
            return Result(False, user_id, "wrong types", None)
        else:
            return self._store_administrator.remove_product_from_store(user_id, store_name=store_name,
                                                                       product_name=product_name)

    def edit_existing_product_in_store(self, user_id: int, store_name: str, product_name: str, brand: str,
                                       new_price: float, quantity: int,
                                       categories: TypedList = None, description: str = ""):
        """
        editing an existing product in store
        :param user_id: (int) username of the user that want to edit the product
        :param store_name: (str) store that the user want to edit in
        :param brand: (str) brand of the product to edit
        :param product_name:(str) name of the product to edit
        :param new_price:(float) new base price for the product
        :param categories:(list of str) list of new categories to edit by
        :param description: (str) new description of the product
        :return:  Result object with info on the process
        """
        if categories is None:
            categories = TypedList(str)
        return self._store_administrator.edit_existing_product_in_store(user_id, store_name, product_name, brand,
                                                                        new_price, quantity,
                                                                        categories, description)

    def add_admin(self, requesting_user_id: int, requested_user: str):
        """
        adds a new admin to the system
        :param requesting_user_id: id of an existing admin
        :param requested_user: name of the user to turn to admin
        :return: Result with info on the process
        """
        if not TypeChecker.check_for_positive_number(
                [requesting_user_id]) or not TypeChecker.check_for_non_empty_strings([requested_user]):
            return Result(False, requesting_user_id if type(requested_user) == int else -1,
                          " expected 1 int id, and 1 string as username", None)
        else:
            return self._admin_handler.add_admin(requesting_user_id, requested_user)

    def renew_session(self):
        self._dal.renew_session()

    def drop_session(self):
        self._dal.drop_session()

    def adding_new_owner_to_store(self, username_adding_id: int, username_added: str, store_name: str):
        """
        adding new owner to existing store
        :param username_adding_id: (id) id that of the user who is exist in the given store as owner
        :param username_added: (str) username to add as owner to the given store
        :param store_name: (str) name of the store to add owner
        :return:  Result object with info on the process
        """
        if not TypeChecker.check_for_non_empty_strings(
                [username_added, store_name]) or not TypeChecker.check_for_positive_number(
            [username_adding_id]):
            return Result(False, username_adding_id if type(username_adding_id) == int else -1,
                          " expected 1 int, 2 strings", None)
        else:
            # return self._store_administrator.adding_new_owner_to_store(username_adding_id, username_added, store_name)
            return self._store_administrator.propose_new_owner_to_store(username_adding_id, username_added, store_name)

    def adding_new_manager_to_store(self, username_adding_id: int, username_added: str, store_name: str):
        """
        adding new owner to existing store
        :param username_adding_id: (id) id that of the user who is exist in the given store as owner
        :param username_added: (str) username to add as manager to the given store
        :param store_name: (str) name of the store to add owner
        :return: Result object with info on the process
        """
        if not TypeChecker.check_for_non_empty_strings(
                [username_added, store_name]) or not TypeChecker.check_for_positive_number(
            [username_adding_id]):
            return Result(False, username_adding_id if type(username_adding_id) == int else -1,
                          "all types must be non empty strings", None)
        else:
            return self._store_administrator.adding_new_manager_to_store(username_adding_id, username_added,
                                                                         store_name)

    def editing_permissions_to_store_manager(self, username_editing_id: int, username_edited: str, store_name: str,
                                             can_manage_inventory: bool = False, appoint_new_store_owner: bool = False,
                                             appoint_new_store_manager: bool = False,
                                             watch_purchase_history: bool = False,
                                             open_and_close_store: bool = False,
                                             can_manage_discount: bool = False):
        """
        edit a given manager permission for a certain store
        :param username_editing_id:(id) id of the user that requesting to edit the given user
        :param username_edited:(str) username that is being edited as manager
        :param store_name:(str) name of the store the permissions belong to
        :param can_manage_inventory: (bool) is permitted to edit inventory
        :param appoint_new_store_owner: (bool) is permitted to add new owner
        :param appoint_new_store_manager: (bool) is permitted to add new manager
        :param watch_purchase_history: (bool) is permitted to watch purchase history from the store
        :param open_and_close_store: (bool) is permitted to open and close store
        :param can_manage_discount: (bool) is permitted to edit discount
        :return: Result with info on the process
        """
        return self._store_administrator.editing_permissions_to_store_member(username_editing_id, username_edited,
                                                                             store_name,
                                                                             can_manage_inventory,
                                                                             appoint_new_store_owner,
                                                                             appoint_new_store_manager,
                                                                             watch_purchase_history,
                                                                             open_and_close_store, can_manage_discount)

    def propose_new_owner_to_store(self, proposer_id: int, candidate_name: str, store_name: str):
        return self._store_administrator.propose_new_owner_to_store(proposer_id, candidate_name, store_name)

    def respond_new_owner_to_store(self, responder_id: int, candidate_name: str, store_name: str, response):
        return self._store_administrator.respond_new_owner_to_store(responder_id, candidate_name, store_name, response)

    def fetch_awaiting_approvals(self, user_id: int, store_name: str):
        return self._store_administrator.fetch_awaiting_approvals(user_id, store_name)

    def removing_store_manager(self, username_removing_id: int, username_removed: str, store_name: str):
        """
        :param username_removing_id: (int) id of the user who removes the another owner
        :param username_removed: (str) username of the user that needs to be removed
        :param store_name: (str) name of the store to remove user from as owner
        :return: Result with info on the process
        """
        if not TypeChecker.check_for_non_empty_strings(
                [username_removed, store_name]) or not TypeChecker.check_for_positive_number(
            [username_removing_id]):
            return Result(False, username_removing_id, "all types must be non empty strings", None)
        else:
            return self._store_administrator.removing_store_manager(username_removing_id, username_removed,
                                                                    store_name)

    def update_users_after_remove(self):
        self._store_administrator._data_handler.update_users_after_remove()

    def removing_store_owner(self, username_removing_id: int, username_removed: str, store_name: str):
        """
        :param username_removing_id: (int) id of the user who removes the another owner
        :param username_removed: (str) username of the user that needs to be removed
        :param store_name: (str) name of the store to remove user from as owner
        :return: Result with info on the process
        """
        if not TypeChecker.check_for_non_empty_strings(
                [username_removed, store_name]) or not TypeChecker.check_for_positive_number(
            [username_removing_id]):
            return Result(False, username_removing_id, "all types must be non empty strings", None)
        else:
            return self._store_administrator.removing_store_owner(username_removing_id, username_removed,
                                                                  store_name)

    def close_store(self, username_closing_id: int, store_name: str):
        """
        closing store as a store owner
        :param username_closing_id: (int) id of a user who is a store owner (or as store manager)
        :param store_name:(str) name of the store to close
        :return: Result with info on the process
        """
        res: Result = self._store_administrator.close_existing_store(username_closing_id, store_name)
        return res

    def add_policy(self, user_id, storename, min_basket_quantity, max_basket_quantity, product_name,
                   min_product_quantity, max_product_quantity, category,
                   min_category_quantity, max_category_quantity, day, policy_id: int = -1):
        return self.store_administrator.add_policy_to_store(user_id, storename, min_basket_quantity,
                                                            max_basket_quantity, product_name, min_product_quantity,
                                                            max_product_quantity, category, min_category_quantity,
                                                            max_category_quantity, day, policy_id)

    def remove_policy(self, user_id, storename, to_remove):
        return self.store_administrator.remove_policy_to_store(user_id, storename, to_remove)

    def fetch_policies(self, user_id, storename):
        return self.store_administrator.fetch_policies_for_store(user_id, storename)

    def add_discount(self, user_id: int, product_name: str, store_name: str, discount_type: int, percent: int,
                     category: str, free: int, per_x: int,
                     overall_product_price_dict: dict, overall_category_price_dict: dict,
                     overall_product_quantity_dict: dict,
                     overall_category_quantity_dict: dict, datetime_object: datetime, basket_size: int,
                     discount_id: int = -1):
        """
        add discount to the given store if the user have permission to do so
        :param user_id: (int) id of the given user
        :param product_name: (str) name of the product
        :param discount_type: (str) type of discount
        :param percent: (float) number of percent to give %
        :param category: category to give discount to
        :param free: how much items to get for free per x
        :param per_x: how much to buy to get free amount
        :param overall_product_price_dict: dict - product->wanted_price
        :param overall_category_price_dict: dict - category -> wanted_price
        :param overall_product_quantity_dict:dict - product -> quantity
        :param overall_category_quantity_dict:dict - quantity -> quantity
        :param datetime_object: datetime - date expired of the discount
        :param basket_size: int - minimum requirement over items in basket
        :param discount_id:(int) discount id to edit. if negative -> add a new discount
        :return: Result with process info
        """
        if percent is None or type(percent) != str or percent == "":
            percent = 0.0
        overall_category_price_dict = [{"category_name": k, "needed_price": v} for k, v in
                                       overall_category_price_dict.items()]
        overall_category_quantity_dict = [{"category_name": k, "needed_items": v} for k, v in
                                          overall_category_quantity_dict.items()]
        overall_product_price_dict = [{"product_name": k, "needed_price": v} for k, v in
                                      overall_product_price_dict.items()]
        overall_product_quantity_dict = [{"product_name": k, "needed_items": v} for k, v in
                                         overall_product_quantity_dict.items()]

        percent: float = float(float(percent) / 100.0)

        # simple product with percent
        if discount_type == "1":

            return self._store_administrator.add_simple_product_discount(user_id, store_name, datetime_object, percent,
                                                                         product_name, size_of_basket_cond=basket_size,
                                                                         over_all_price_category_cond=overall_category_price_dict,
                                                                         over_all_price_product_cond=overall_product_price_dict,
                                                                         product_list_cond=overall_product_quantity_dict,
                                                                         overall_category_quantity=overall_category_quantity_dict,
                                                                         discount_id=discount_id)
        # free per x product
        elif discount_type == "2":
            return self._store_administrator.add_free_per_x_product_discount_discount(user_id, store_name,
                                                                                      datetime_object, product_name,
                                                                                      free, per_x, is_duplicate=True,
                                                                                      size_of_basket_cond=basket_size,
                                                                                      over_all_price_category_cond=overall_category_price_dict,
                                                                                      over_all_price_product_cond=overall_product_price_dict,
                                                                                      product_list_cond=overall_product_quantity_dict,
                                                                                      overall_category_quantity=overall_category_quantity_dict,
                                                                                      discount_id=discount_id)
        # simple category with with percent
        elif discount_type == "3":
            return self._store_administrator.add_simple_category_discount(user_id, store_name,
                                                                          datetime_object, percent, category,
                                                                          size_of_basket_cond=basket_size,
                                                                          over_all_price_category_cond=overall_category_price_dict,
                                                                          over_all_price_product_cond=overall_product_price_dict,
                                                                          product_list_cond=overall_product_quantity_dict,
                                                                          overall_category_quantity=overall_category_quantity_dict,
                                                                          discount_id=discount_id)

        # free per x product
        elif discount_type == "4":
            return self._store_administrator.add_free_per_x_category_discount(user_id, store_name,
                                                                              datetime_object, category,
                                                                              free, per_x, is_duplicate=True,
                                                                              size_of_basket_cond=basket_size,
                                                                              over_all_price_category_cond=overall_category_price_dict,
                                                                              over_all_price_product_cond=overall_product_price_dict,
                                                                              product_list_cond=overall_product_quantity_dict,
                                                                              overall_category_quantity=overall_category_quantity_dict,
                                                                              discount_id=discount_id)
        elif discount_type == "5":
            return self._store_administrator.add_basket_discount(user_id, store_name, datetime_object, percent,
                                                                 size_of_basket_cond=basket_size,
                                                                 over_all_price_category_cond=overall_category_price_dict,
                                                                 over_all_price_product_cond=overall_product_price_dict,
                                                                 product_list_cond=overall_product_quantity_dict,
                                                                 overall_category_quantity=overall_category_quantity_dict,
                                                                 discount_id=discount_id)
        else:
            return Result(False, user_id, "Invalid discount type", None)

    def combine_policies_for_store(self, requesting_user_id: int, store_name: str, policies_id_list: list,
                                   operator: str):
        return self._store_administrator.combine_policies_for_store(requesting_user_id, store_name, policies_id_list,
                                                                    operator)

    def get_all_discounts(self, user_id: int, store_name: str):
        return self._store_administrator.get_all_discount_in_store(user_id, store_name)

    def remove_discount(self, user_id: int, store_name: str, discount_id: int):
        """
        removing discount from a given store if possible
        :param user_id: user_id
        :param store_name:
        :param discount_id:
        :return: Result with info on process
        """
        return self._store_administrator.remove_discount(user_id, store_name, discount_id)

    def purchase_items(self, user_id: int, credit_card_number: int, country: str, city: str,
                       street: str, house_number: int, expiry_date: str,  ccv: str, holder: str, holder_id: str, apartment: str = "0",
                       floor: int = 0):
        """
        purchasing all the items in the shopping cart
        :param expiry_date:
        :param user_id:(int) id of the purchasing user
        :param credit_card_number: (int) credit card number to pay with
        :param country: country to send to
        :param city: city in country to send to
        :param street: street in city to send to
        :param house_number: house number in street
        :param holder_id:
        :param holder:
        :param ccv: 3 numbers behind the credit card
        :param apartment: apartment identifier in house
        :param floor: floor of the apartment
        :return: Result object for purchasing result
        """
        return self._shopping_handler.make_purchase_of_all_shopping_cart(user_id, credit_card_number, country, city,
                                                                         street, house_number, expiry_date, ccv, holder, holder_id,
                                                                         apartment, floor)

    def get_user_by_id(self, user_id: int):
        return self._users_handler.get_user_by_id(user_id)

    def get_user_by_id_if_guest_create_one(self, user_id: int):
        return self._users_handler.get_user_by_id_if_guest_create_one(user_id)

    def is_admin(self, username: str):
        return

    def watch_store_purchase(self, requesting_user_id: int, store_name: str):
        """
        Returns specific store purchases history
        :param requesting_user_id:(int) Should be a manager / store owner or someone else with valid permissions
        :param store_name: The user, that his/she purchases is requested
        :return: Result object containing a list of requested purchases
        """
        return self._store_administrator.watch_store_purchase_history(requesting_user_id, store_name)

    def watch_all_purchases(self, requesting_user: int):
        """
        Returns all purchases
        :param requesting_user: Should be a an admin or other authorized user
        :return: Result object containing a list of requested purchases
        """
        return self._admin_handler.watch_all_purchases(requesting_user)

    def watch_user_purchases(self, requesting_user: int, requested_user: str):
        """
        Returns specific user purchases history
        :param requesting_user: The user who requests this view(some manager or the user itself)
        :param requested_user: The user, that his/she purchases is requested
        :return: Result object containing a list of requested purchases
        """
        # User requesting to see its own purchases
        if len(requested_user) == 0:
            return self._shopping_handler.watch_user_purchases(requesting_user)

        # is_guest = "#" in requested_user
        #
        # # Admin requesting a guest user
        # if is_guest:
        #     try:
        #         guest_id = int(requested_user.split('#')[1])
        #     except:
        #         return Result(False, requesting_user, f"Guest id format invalid, got {requested_user}", None)
        #     return self._shopping_handler.watch_user_purchases(requesting_user, guest_id)

        else:
            # Admin requesting a registered user
            # ret = self._users_handler.get_id_by_name(requested_user)
            # if ret == -1:
            #     return Result(False, requesting_user, f"'{requested_user}' not found", None)
            return self._shopping_handler.watch_user_purchases(requesting_user, requested_user)

    def get_all_sub_staff_of_user(self, user_id, store_name):
        """
        get all sub managers and all sub owners of the given user id with the given store, if possible
        :param user_id: (int) user to get sub stuff to
        :param store_name:(str) name of the store
        :return: list of all sub stuff of that user. if the user is not part of the staff of the store -> will return error
        """
        return self._store_administrator.get_all_sub_staff_of_user(user_id, store_name)

    @property
    def users_handler(self):
        return self._users_handler

    @property
    def store_administrator(self):
        return self._store_administrator


    def update_stats_counter_for_user(self, counter_change: int, username: str, role: int):
        return self._users_handler.update_stats_counter_for_user(counter_change, username, role)
