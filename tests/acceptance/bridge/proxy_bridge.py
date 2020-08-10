class AcceptanceTestError(Exception):
    pass


class ProxyBridge:
    # --------------------------------------user handler------------------------------------

    """ :param id- auto-generated
        :param email- given by user
        :param username- given by user 
        :param password - given by user
        :returns void. raises exception if unsuccessful
    """

    def login(self, username: str, password: str):
        return False

    """ :param username- given by user 
        :param password - given by user
        :returns- void. raises exception if unsuccessful
    """

    """ :param username- given by user 
        :returns- void. raises exception if unsuccessful
    """

    def logout(self, user_id: int, username: str):
        return True

    # -------------------------------Shopping interface-----------------------------------

    """ :param 1) item name 2) store name 
        :returns tuple (name, store, category, price) on success 
                and raises AcceptanceTestException on fail
    """

    def view_item(self, user_id: int, store_name: str, item_name: str):
        return False

    """ :param: store name- given by user 
        :returns- if success: tuple (store name,initial_owner, inventory)
                    inventory= list of items (item name, category, price)
                  else raises "AcceptanceTestException" with message 
    """

    def view_store(self, user_id: int, store_name: str):
        return ("", "", "")

    """ :param- item name, stores_names, categories , brands ,min_price ,max_price
            *important: unused criteria will contain empty string
        : returns- number of hits
            raises "AcceptanceTestException" with message if failure
    """

    def search_for_items(self, user_id: int, item_name: str, stores_names, categories, brands, min_price: float,
                         max_price: float):
        return False

    """ :param- user_name, item name, store name and quantity
        :returns - true if added successfully and false otherwise
    """

    def add_item_to_cart(self, user_id: int, item_name: str, store_name: str, quantity: int):
        return False

    def view_cart(self, user_id: int):
        return False

    # ------------------------------Inventory--------------------------------
    """ :params- 1) name of store to open 2) owner's username 
        ::returns- void. raises exception if unsuccessful
    """

    def open_store(self, user_id: int, store_name: str):
        return False

    """ :params- all item's fields
        :returns- void. raises exception if unsuccessful
    """

    def add_item_to_store(self, user_id: int, store_name: str, item_name: str, category: str, brand: str, price: float,
                          quantity: int):
        return False

    """ :params- store name , item name
        :returns- void. raises exception if unsuccessful
    """

    def remove_item_from_store(self, user_id: int, store_name: str, item_name: str):
        return False

    """ :param- all item's fields (where no update was done there is an empty string)
        :returns- void. raises exception if unsuccessful
    """

    def update_item_in_store(self, user_id: int, store_name: str, item_name: str, category: str, brand: str,
                             price: float, quantity: int):
        return False

    """ :param- 1) store name, 2) current store owner 3) username of person to appoint to owner
        :returns- void. raises exception if unsuccessful
    """

    def appoint_store_owner(self, store_owner_id: int, store_name: str, to_appoint_username: str):
        return False

    """ :param- 1) store name, 2) current store owner 3) username of person to appoint to manager
        :returns- void. raises exception if unsuccessful
    """

    def appoint_store_manager(self, store_name: str, store_owner_user_id: int, to_appoint_username: str):
        return True

    def change_manager_permissions(self, store_name: str, store_owner_id: int, store_manager_name: str,
                                   can_manage_inventory: bool, appoint_new_store_owner: bool,
                                   appoint_new_store_manager: bool,
                                   edit_management_options_for_appoints: bool,
                                   remove_appointee_store_manager: bool, watch_purchase_history: bool,
                                   open_and_close_store: bool, can_manage_discounts: bool):
        return False

    """ :param- 1) store name, 2) current store owner 3) username of manager to remove 
        :returns - true if removed successfully and false otherwise 
    """

    def view_user_purchases(self, user_id: int):
        return False

    def view_store_purchases(self, user_id: int, store_name: str):
        return False

    def edit_item_in_cart(self, user_id: int, store_name: str, item_name: str, quantity: int):
        return False

    # def purchase(self, user_id: int, credit_card_number: int, data_dict, purchase_entry, quantity):
    def purchase(self, user_id: int, credit_card_number: int, data_dict):
        return False

    def cancel_pre_purchase(self, user_id):
        return False

    def view_system_purchases(self, user_id):
        return False

    def remove_store_manager(self, store_name: str, store_owner_id: int, store_manager_name: str):
        return False

    def remove_store_owner(self, store_name: str, store_owner_id: int, store_manager_name: str):
        pass

    def watch_purchase_history(self):
        return False

    def close_store(self, owner_id: int, store_name: str):
        return False

    # ------------------ ADMIN --------------------------------
    def add_admin(self, user_id: int, to_add: str):
        return False

    def is_admin(self, username: str):
        return False

    def view_as_admin_user_purchases(self, user_id, username):
        return False

    def view_as_admin_store_purchases(self, user_id, username):
        return False
