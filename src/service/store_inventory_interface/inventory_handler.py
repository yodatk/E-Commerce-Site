import re
from datetime import datetime

from src.domain.system.system_facade import SystemFacade
from src.logger.log import Log
from src.protocol_classes.classes_utils import Result, TypedList


class InventoryHandler:
    def __init__(self):
        self.logger = Log.get_instance().get_logger()
        self.sys: SystemFacade = SystemFacade.get_instance()

    def get_all_stores_of_user(self, username: str):
        """
        get all the stores that the current user have administration permission in
        :param user_id: (int) id of the user
        :return: list of stores that the current user is managing or owning
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.get_all_stores_of_user(username)
            if res.succeed:
                self.logger.info(f'User({username}) got all the stores that he manage. total stores: {len(res.data)}')
            else:
                self.logger.info(f"User({username}) failed to get all it's stores. msg: {res.msg}")
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong', None)

    def get_all_products_of_store(self, user_id: int, store_name: str):
        """
        get all the products of the current store
        :param user_id: (int) id of the user
        :param store_name: (str) name of store
        :return: list of products of the current store
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.get_all_products_of_store(user_id, store_name)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(f'User({user_id}) got all the products of store. total products: {len(res.data)}')
            else:
                self.logger.info(f"User({user_id}) failed to get all store's products. msg: {res.msg}")
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong', None)

    def opening_a_new_store(self, user_id: int, store_name: str):
        """
        opening a new store by a registered user
        :param user_id:(int) username of the user who wants to open a store
        :param store_name: (str) name of the store to open
        :return:True if successful, False otherwise
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.opening_a_new_store(user_id, store_name)
            if res.succeed:
                self.logger.info(f'New Store({store_name}) added with Owner({user_id})')
            else:
                self.logger.info(f'Store creation failed: Attempted by User({user_id}) with Reason({res.msg})')
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def add_product_to_store(self, user_id: int, store_name: str, product_name: str, base_price: float, quantity: int,
                             brand: str, categories: list, description: str = ""):
        """
        adding new product to store
        :param user_id: (int) username of the user that is adding new product
        :param store_name:(str) name of the store
        :param product_name: (str) name of the product that is adding to the inventory of the store
        :param base_price: (float) base price for the new product
        :param quantity:(int) quantity of that product to add to the store
        :param description:(str) description of the product
        :return: True if succeeded, False otherwise
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.add_product_to_store(user_id, store_name, product_name, base_price, quantity, brand,
                                                        TypedList(str, categories if type(categories) == list else []),
                                                        description)
            if res.succeed:
                self.logger.info(
                    f'Added Product({product_name}) to Store({store_name}) by User({user_id}) with Price({base_price})')

            else:
                self.logger.info(
                    f'Failed adding Product({product_name}) to Store({store_name}) by User({user_id}) with Price({base_price})')
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def remove_product_to_store(self, user_id: int, store_name: str, product_name: str):
        """
        removing existing product from store
        :param user_id: (int) username of the user that is adding new product
        :param store_name:(str) name of the store
        :param product_name: (str) name of the product that is adding to the inventory of the store
        :return: True if succeeded, False otherwise
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.remove_product_from_store(user_id, store_name, product_name)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(f'Removed Product({product_name}) to Store({store_name}) by User({user_id})')
            else:
                self.logger.info(f'Failed removing Product({product_name}) to Store({store_name}) by User({user_id})')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def edit_existing_product_in_store(self, user_id: int, store_name: str, product_name: str, brand: str,
                                       new_price: float, quantity: int,
                                       categories: list = None, description: str = ""):
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
        try:
            self.sys.renew_session()
            res: Result = self.sys.edit_existing_product_in_store(user_id, store_name, product_name, brand, new_price,
                                                                  quantity,
                                                                  TypedList(str,
                                                                            categories) if categories is not None else None,
                                                                  description)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(f'Editing Product({product_name}) to Store({store_name}) by User({user_id}))')
            else:
                self.logger.info(f'Editing failed: Product({product_name}) to Store({store_name}) by User({user_id})')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def adding_new_owner_to_store(self, user_id: int, username_added: str, store_name: str):
        """
        Adding new owner to existing store
        :param user_id: (int) username that of the user who is exist in the given store as owner
        :param username_added: (str) username to add as owner to the given store
        :param store_name: (str) name of the store to add owner
        :return: True if successful, False otherwise
        """
        self.sys.renew_session()
        try:

            res: Result = self.sys.adding_new_owner_to_store(user_id, username_added, store_name)
            if res.succeed:
                self.logger.info(f'Adding Owner({username_added}) to Store({store_name}) by ({user_id})')
            else:
                self.logger.info(

                    f'Adding Owner failed: Owner({username_added}) to Store({store_name}) by ({user_id})')
            self.sys.drop_session()

            return res
        except Exception as e:
            self.logger.error(f'ERROR: {str(e)}')
            self.sys.drop_session()
            return Result(False, -2, 'Something went wrong...', None)

    def adding_new_manager_to_store(self, user_id: int, username_added: str, store_name: str):
        """
        Adding new manager to existing store
        :param user_id: (int) username that of the user who is exist in the given store as owner
        :param username_added: (str) username to add as manager to the given store
        :param store_name: (str) name of the store to add owner
        :return: True if successful, False otherwise
        """
        self.sys.renew_session()
        try:
            res: Result = self.sys.adding_new_manager_to_store(user_id, username_added, store_name)
            if res.succeed:
                self.sys.update_stats_counter_for_user(1, username_added, 4)
                self.logger.info(f'Adding Manager({username_added}) to Store({store_name}) by ({user_id})')
            else:
                self.logger.info(

                    f'Adding Manager failed: Manager({username_added}) to Store({store_name}) by ({user_id})')
            self.sys.drop_session()

            return res
        except Exception as e:
            self.logger.error(f'ERROR: {str(e)}')
            self.sys.drop_session()
            return Result(False, -2, 'Something went wrong...', None)

    def editing_permissions_to_store_manager(self, user_id: int, username_edited: str, store_name: str,
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
        try:
            self.sys.renew_session()

            res: Result = self.sys.editing_permissions_to_store_manager(user_id, username_edited,
                                                                        store_name,
                                                                        can_manage_inventory,
                                                                        appoint_new_store_owner,
                                                                        appoint_new_store_manager,
                                                                        watch_purchase_history,
                                                                        open_and_close_store, can_manage_discount)
            if res.succeed:
                self.logger.info(
                    f'Edit of User({username_edited}) Permissions by User({user_id}) succeeded')
            else:
                self.logger.info(
                    f'Edit of User({username_edited}) Permissions by User({user_id}) failed')
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def remove_discount(self, user_id: int, discount_id: int, store_name: str) -> Result:
        try:

            self.sys.renew_session()
            res: Result = self.sys.remove_discount(user_id, store_name, discount_id)
            if res.succeed:
                self.logger.info(f"removing discount #{discount_id} was successful")
            else:
                self.logger.info(f"removing discount #{discount_id} failed: {res.msg}")
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def edit_discount(self, user_id, discount_id, store_name, product_name, discount_type, percent, category,
                      free_per_x, overall_product_price,
                      overall_category_price, overall_product_quantity, overall_category_quantity,
                      up_to_date, basket_size) -> Result:
        self.sys.renew_session()
        res: Result = self._add_or_edit_discount(user_id, store_name, product_name, discount_type, percent, category,
                                                 free_per_x,
                                                 overall_product_price, overall_category_price,
                                                 overall_product_quantity,
                                                 overall_category_quantity,
                                                 up_to_date, basket_size, discount_id)
        self.sys.drop_session()
        return res

    def combine_discount(self, user_id: int, store_name: str, discounts_id_list: list, operator: str):
        """
        combine several discount to one complex discount
        :param user_id: (int) user id of the user that want to edit the quantity
        :param store_name: (str) store name where the product belong
        :param discounts_id_list: list of discount id to combine
        :param operator: chosen operator - XOR, AND or OR
        :return: Result with info of the process
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.combine_discounts(user_id, store_name, discounts_id_list, operator)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(f"combining discount was successful, and reaplaced by id #{res.data}")
            else:
                self.logger.info(f"combining discount failed: {res.msg}")
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def _add_or_edit_discount(self, user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                              overall_product_price, overall_category_price, overall_product_quantity,
                              overall_category_quantity,
                              up_to_date, basket_size, discount_id: int = -1) -> Result:
        try:
            if len(basket_size) > 0:
                try:
                    basket_size = int(basket_size)
                    if basket_size < 0:
                        raise Exception("Expected none negative")
                except:
                    return Result(False, user_id, "Expected basket size to be a none negative integer")
            else:
                basket_size = None

            if len(store_name) == 0:
                return Result(False, user_id, "Storename was empty", None)

            try:
                user_id = int(user_id)
            except:
                return Result(False, user_id, 'Error, expected user_id to be int', None)

            if len(up_to_date) == 0:
                return Result(False, user_id, 'Up to date is mandatory', None)

            if discount_type not in ["1", "2", "3", "4", "5"]:
                return Result(False, user_id, 'Unknown discount type', None)

            # Validate required fields per discount type
            if discount_type == "1":  # Product , %
                if len(percent) == 0:
                    return Result(False, user_id, 'Percent is missing', None)
                if len(product_name) == 0:
                    return Result(False, user_id, 'Product name is missing', None)
            elif discount_type == "2":  # Product, FreePerX
                if len(free_per_x) == 0:
                    return Result(False, user_id, 'free_per_x is missing', None)
                if len(product_name) == 0:
                    print("Product name is missing")
            elif discount_type == "3":  # Category , %
                if len(percent) == 0:
                    return Result(False, user_id, 'Percent is missing', None)
                if len(category) == 0:
                    return Result(False, user_id, 'Category is missing', None)
            elif discount_type == "4":  # Category, FreePerX
                if len(free_per_x) == 0:
                    return Result(False, user_id, 'free_per_x is missing', None)
                if len(category) == 0:
                    return Result(False, user_id, 'Category is missing', None)
            else:  # Basket discount
                if len(percent) == 0:
                    return Result(False, user_id, 'Percent is missing', None)

            if discount_type == "5":  # Basket , %
                if len(percent) == 0:
                    return Result(False, user_id, 'Percent is missing', None)

            # Validate the date which is required by all types
            try:
                datetime_object = datetime.strptime(up_to_date, '%d/%m/%Y')
            except:
                return Result(False, user_id, 'Invalid up_to_date format', None)

            # For 2 and 4 types I need to validate the ratio numerator/denominator
            free = None
            per_x = None
            if discount_type == "2" or discount_type == "4":
                try:
                    free_per_x = free_per_x.split('/')
                    free = int(free_per_x[0])
                    per_x = int(free_per_x[1])
                    if free >= per_x:
                        return Result(False, user_id, 'Invalid free_per_x format', None)
                except:
                    return Result(False, user_id, 'Invalid free_per_x', None)
            else:
                free = None
                per_x = None

            name_number_regexp = "^((([a-zA-Z0-9]+):([1-9][0-9]*)),?)+$"
            overall_category_price_dict = {}
            overall_category_quantity_dict = {}
            overall_product_quantity_dict = {}
            overall_product_price_dict = {}
            if len(overall_category_price) > 0:
                match = re.search(name_number_regexp, overall_category_price)
                try:
                    if match:
                        overall_category_price_dict = {item[0]: int(item[1]) for item in
                                                       map(lambda m: m.split(':'), overall_category_price.split(','))}
                    else:
                        return Result(False, user_id, "No match for overall_category_price", None)
                except:
                    return Result(False, user_id, 'Invalid overall_category_price', None)

            if len(overall_category_quantity) > 0:
                match = re.search(name_number_regexp, overall_category_quantity)
                try:
                    if match:
                        overall_category_quantity_dict = {item[0]: int(item[1]) for item in
                                                          map(lambda m: m.split(':'),
                                                              overall_category_quantity.split(','))}
                    else:
                        return Result(False, user_id, 'Invalid overall_category_quantity', None)
                except:
                    return Result(False, user_id, 'Invalid overall_category_quantity', None)

            if len(overall_product_quantity) > 0:
                match = re.search(name_number_regexp, overall_product_quantity)
                try:
                    if match:
                        overall_product_quantity_dict = {item[0]: int(item[1]) for item in
                                                         map(lambda m: m.split(':'),
                                                             overall_product_quantity.split(','))}
                    else:
                        return Result(False, user_id, 'Invalid overall_product_quantity', None)
                except:
                    return Result(False, user_id, 'Invalid overall_product_quantity', None)

            if len(overall_product_price) > 0:
                match = re.search(name_number_regexp, overall_product_price)
                try:
                    if match:
                        overall_product_price_dict = {item[0]: int(item[1]) for item in
                                                      map(lambda m: m.split(':'), overall_product_price.split(','))}
                    else:
                        return Result(False, user_id, 'Invalid overall_product_price', None)
                except:
                    return Result(False, user_id, 'Invalid overall_product_price', None)
            if datetime_object <= datetime.now():
                return Result(False, user_id, "expiration date must be a future date", None)
            # free - the part that is given free, per_x - amount must buy for discount,
            return self.sys.add_discount(user_id, product_name, store_name, discount_type, percent, category, free,
                                         per_x,
                                         overall_product_price_dict, overall_category_price_dict,
                                         overall_product_quantity_dict, overall_category_quantity_dict, datetime_object,
                                         basket_size, discount_id)
        except Exception as e:
            return Result(False, user_id, f'Error in add_discount: {str(e)}', None)

    def add_discount(self, user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                     overall_product_price, overall_category_price, overall_product_quantity, overall_category_quantity,
                     up_to_date, basket_size) -> Result:

        self.sys.renew_session()
        res: Result = self._add_or_edit_discount(user_id, store_name, product_name, discount_type, percent, category,
                                                 free_per_x,
                                                 overall_product_price, overall_category_price,
                                                 overall_product_quantity,
                                                 overall_category_quantity,
                                                 up_to_date, basket_size)
        self.sys.drop_session()
        return res

    def combine_policies_for_store(self, user_id: int, store_name: str, discounts_list_id: list, operator: str):
        """
        combine several discount to one complex discount
        :param user_id: (int) user id of the user that want to edit the quantity
        :param store_name: (str) store name where the product belong
        :param discounts_list_id: list of discount id to combine
        :param operator: chosen operator - XOR, AND or OR
        :return: Result with info of the process
        """
        self.sys.renew_session()
        res: Result = self.sys.combine_policies_for_store(user_id, store_name, discounts_list_id, operator)
        self.sys.drop_session()
        return res

    def add_policy(self, user_id, storename, min_basket_quantity, max_basket_quantity, product_name,
                   min_product_quantity,
                   max_product_quantity, category, min_category_quantity, max_category_quantity, day,
                   policy_id: int = -1):

        try:
            try:
                user_id = int(user_id)
            except:
                return Result(False, user_id, 'Error, expected user_id to be int', None)

            # # Validate the date which is required by all types
            # try:
            #     datetime_object = datetime.strptime(time, '%d/%m/%Y')
            # except:
            #     return Result(False, user_id, 'Invalid up_to_date format', None)

            if min_basket_quantity != "":
                try:
                    min_basket_quantity = int(min_basket_quantity)
                except:
                    return Result(False, user_id, 'Error, expected min_basket_quantity to be int', None)
            else:
                min_basket_quantity = None
            if max_basket_quantity != "":
                try:
                    max_basket_quantity = int(max_basket_quantity)
                except:
                    return Result(False, user_id, 'Error, expected max_basket_quantity to be int', None)
            else:
                max_basket_quantity = None
            if min_product_quantity != "":
                try:
                    min_product_quantity = int(min_product_quantity)
                except:
                    return Result(False, user_id, 'Error, expected min_product_quantity to be int', None)
            else:
                min_product_quantity = None
            if max_product_quantity != "":
                try:
                    max_product_quantity = int(max_product_quantity)
                except:
                    return Result(False, user_id, 'Error, expected max_product_quantity to be int', None)
            else:
                max_product_quantity = None
            if min_category_quantity != "":
                try:
                    min_category_quantity = int(min_category_quantity)
                except:
                    return Result(False, user_id, 'Error, expected min_category_quantity to be int', None)
            else:
                min_category_quantity = None
            if max_category_quantity != "":
                try:
                    max_category_quantity = int(max_category_quantity)
                except:
                    return Result(False, user_id, 'Error, expected max_category_quantity to be int', None)
            else:
                max_category_quantity = None
        except:
            return Result(False, user_id, 'Unknown error in add_policy', None)
        if min_basket_quantity is not None and max_basket_quantity is not None:
            if max_basket_quantity < min_basket_quantity:
                return Result(False, user_id, 'Error, expected max basket quantity to '
                                              'be bigger than min basket quantity', None)
        if min_category_quantity is not None and max_category_quantity is not None:
            if max_category_quantity < min_category_quantity:
                return Result(False, user_id, 'Error, expected max category quantity to '
                                              'be bigger than min category quantity', None)
        if min_product_quantity is not None and max_product_quantity is not None:
            if max_product_quantity < min_product_quantity:
                return Result(False, user_id, 'Error, expected max product quantity to '
                                              'be bigger than min product quantity', None)

        self.sys.renew_session()
        res: Result = self.sys.add_policy(user_id, storename, min_basket_quantity, max_basket_quantity, product_name,
                                          min_product_quantity, max_product_quantity, category,
                                          min_category_quantity, max_category_quantity, day, policy_id)
        self.sys.drop_session()
        return res

    def remove_policy(self, user_id, storename, to_remove):
        try:
            user_id = int(user_id)
            to_remove = int(to_remove)
        except:
            return Result(False, user_id, 'Error, expected user_id or to_remove to be int', None)
        self.sys.renew_session()
        res: Result = self.sys.remove_policy(user_id, storename, to_remove)
        self.sys.drop_session()
        return res

    def edit_policy(self, user_id, storename, to_edit, min_basket_quantity, max_basket_quantity, product_name,
                    min_product_quantity, max_product_quantity, category, min_category_quantity,
                    max_category_quantity, day):
        try:
            res: Result = self.remove_policy(user_id, storename, to_edit)
            if res.succeed:
                res: Result = self.add_policy(user_id, storename, min_basket_quantity, max_basket_quantity,
                                              product_name,
                                              min_product_quantity, max_product_quantity, category,
                                              min_category_quantity, max_category_quantity, day)
                if res.succeed:
                    self.logger.info(f"editing policy #{to_edit} was successful, and replaced by id #{res.data}")
                else:
                    self.logger.info(f"editing policy #{to_edit} was Failed: {res.msg}")
                return res

            else:
                self.logger.info(f"editing policy #{to_edit} failed:  {res.msg}")
                return res
        except Exception as e:

            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def fetch_policies_from_store(self, user_id, storename):
        try:
            user_id = int(user_id)
        except:
            return Result(False, user_id, 'Error, expected user_id to be int', None)
        self.sys.renew_session()
        res: Result = self.sys.fetch_policies(user_id, storename)
        self.sys.drop_session()
        return res

    def removing_store_manager(self, user_id: int, removed_username: str, store_name: str):
        """
        :param user_id: (int) username of the user who removes the another owner
        :param username_removed: (str) username of the user that needs to be removed
        :param store_name: (str) name of the store to remove user from as owner
        :return: True if Successful, False otherwise
        """
        self.sys.renew_session()
        try:
            res: Result = self.sys.removing_store_manager(user_id, removed_username, store_name)
            if res.succeed:
                self.sys._dal.commit()
                self.sys.update_stats_counter_for_user(-1, removed_username, 4)
                self.sys.update_users_after_remove()
            if res.succeed:
                self.logger.info(
                    f'Removal of Manager({removed_username}) of Store({store_name}) by ({user_id}) was made')
            else:
                self.logger.info(
                    f'Removal of Manager({removed_username}) of Store({store_name}) by ({user_id}) was failed')
            self.sys.drop_session()
            return res
        except Exception as e:
            self.logger.error(f'ERROR: {str(e)}')
            self.sys.drop_session()
            return Result(False, -2, 'Something went wrong...', None)

    def removing_store_owner(self, user_id: int, removed_username: str, store_name: str):
        """
        :param username_removing: (int) username of the user who removes the another owner
        :param username_removed: (str) username of the user that needs to be removed
        :param store_name: (str) name of the store to remove user from as owner
        :return: True if Successful, False otherwise
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.removing_store_owner(user_id, removed_username, store_name)
            if res.succeed:
                self.sys._dal.commit()
                self.sys.update_stats_counter_for_user(-1, removed_username, 3)
                self.sys.update_users_after_remove()
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(
                    f'Removal of Owner({removed_username}) of Store({store_name}) by ({user_id}) was made')
            else:
                self.logger.info(
                    f'Removal of Owner({removed_username}) of Store({store_name}) by ({user_id}) was failed')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def close_store(self, user_id: int, store_name: str):
        """
        closing store as a store owner
        :param user_id: (int) username of a user who is a store owner (or as store manager)
        :param store_name:(str) name of the store to close
        :return: True if store is closed, False if something went wrong
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.close_store(user_id, store_name)
            self.sys.drop_session()

            if res.succeed:
                self.logger.info(
                    f'Closing Store({store_name}) by ({user_id})')
            else:
                self.logger.info(
                    f'Failed to close Store({store_name}) by ({user_id})')
            return res
        except Exception as e:
            self.sys.drop_session()

            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def open_existing_store(self, user_id: int, store_name: str):
        """
        opening an existing store as a store owner
        :param user_id: (int) username of a user who is a store owner (or as store manager)
        :param store_name:(str) name of the store to open
        :return: True if store is open, False if something went wrong
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.opening_existing_store(user_id, store_name)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(
                    f'Open Store({store_name}) by ({user_id})')
            else:
                self.logger.info(
                    f'Failed to open Store({store_name}) by ({user_id})')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def get_all_sub_staff_of_user(self, user_id, store_name):
        """
        get all sub managers and all sub owners of the given user id with the given store, if possible
        :param user_id: (int) user to get sub stuff to
        :param store_name:(str) name of the store
        :return: list of all sub stuff of that user. if the user is not part of the staff of the store -> will return error
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.get_all_sub_staff_of_user(user_id, store_name)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(res.msg)
            else:
                self.logger.info(
                    f'User({user_id}) Failed to get all sub members Store({store_name}) : {res.msg}')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def watch_store_purchase(self, requesting_user_id: int, store_name: str):
        """
        Returns specific store purchases history
        :param requesting_user_id:(int) Should be a manager / store owner or someone else with valid permissions
        :param store_name: The user, that his/she purchases is requested
        :return: List of Purchases a store had, empty list if there was an error or there were no purchases at all
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.watch_store_purchase(requesting_user_id, store_name)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(
                    f'getting list of Purchases for Store({store_name}) requested by User({requesting_user_id})')
            else:
                self.logger.info(
                    f'***Failed*** getting list of Purchases for Store({store_name}) requested by User({requesting_user_id})')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    #
    # def add_discount_to_all_products(self, user_id: int, store_name: str, percent: float,
    #                                  expiry_date: datetime):
    #     """
    #     adding discount to all the products in the store
    #     :param user_id: (int) id of the user who is requesting the discount
    #     :param store_name: (str) name of the store to edit
    #     :param percent: (float) the percent of discount to give
    #     :param expiry_date: (datetime) date of the discount expire
    #     :return: True if store is close, False if something went wrong
    #     """
    #     try:
    #         res: Result = self.sys.add_discount_to_all_products(user_id, store_name, percent, expiry_date)
    #         if res.succeed:
    #             self.logger.info(
    #                 f'Added discount to all products at Store({store_name}) by User({user_id})')
    #
    #         else:
    #             self.logger.info(
    #                 f'Failed add discount to all products at Store({store_name}) by User({user_id})')
    #         return res
    #     except Exception as e:
    #         self.logger.error(f'ERROR: {str(e)}')
    #         return Result(False, -2, 'Something went wrong...', None)
    #
    # def remove_discount_from_list_of_products(self, user_id: int, store_name: str, product_list: TypedList):
    #     """
    #     remove all prior discounts from the given products in the given store
    #     :param user_id:(int) id of the requesting user
    #     :param store_name:(str) name of the store to edit
    #     :param product_list: list of products to set their price back to their base price
    #     :return: True if store is close, False if something went wrong
    #     """
    #     try:
    #         res: Result = self.sys.remove_discount_from_list_of_products(user_id, store_name, product_list)
    #         if res.succeed:
    #             self.logger.info(
    #                 f'Removed discount to all products at Store({store_name}) by User({user_id})')
    #
    #         else:
    #             self.logger.info(
    #                 f'Failed add remove discount from all products at Store({store_name}) by User({user_id})')
    #         return res
    #     except Exception as e:
    #         self.logger.error(f'ERROR: {str(e)}')
    #         return Result(False, -2, 'Something went wrong...', None)
    #
    # def remove_discount_from_list_of_categories(self, user_id: int, store_name: str, categories_list: TypedList):
    #     """
    #     remove all prior discounts from the products that have one of the given categories in the given store
    #     :param user_id:(int) id of the requesting user
    #     :param store_name:(str) name of the store to edit
    #     :param categories_list:list of categories to set the products in those categories in their base price store by
    #     :return: True if store is close, False if something went wrong
    #     """
    #     try:
    #         res: Result = self.sys.remove_discount_from_list_of_categories(user_id, store_name, categories_list)
    #         if res.succeed:
    #             self.logger.info(
    #                 f'Removed discount to all list of categories({categories_list}) at Store({store_name}) by User({user_id})')
    #         else:
    #             self.logger.info(
    #                 f'Failed to remove discount from all categories({categories_list}) at Store({store_name}) by User({user_id})')
    #         return res
    #     except Exception as e:
    #         self.logger.error(f'ERROR: {str(e)}')
    #         return Result(False, -2, 'Something went wrong...', None)
    #
    # def remove_all_discounts_from_store(self, user_id: int, store_name: str):
    #     """
    #     remove all prior discounts from all products in the store
    #     :param user_id:(int) id of the requesting user
    #     :param store_name:(str) name of the store to edit
    #     :return: True if store is close, False if something went wrong
    #     """
    #     try:
    #         res: Result = self.sys.remove_all_discounts_from_store(user_id, store_name)
    #         if res.succeed:
    #             self.logger.info(
    #                 f'Removed all discounts at Store({store_name}) by User({user_id})')
    #         else:
    #             self.logger.info(
    #                 f'Failed to removed all discounts at Store({store_name}) by User({user_id})')
    #         return res
    #     except Exception as e:
    #         self.logger.error(f'ERROR: {str(e)}')
    #         return Result(False, -2, 'Something went wrong...', None)
    def get_discounts(self, user_id, store_name):
        try:
            self.sys.renew_session()
            res: Result = self.sys.get_all_discounts(user_id, store_name)
            self.sys.drop_session()
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)
        return res
