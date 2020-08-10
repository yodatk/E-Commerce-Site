from src.logger.log import Log
from src.protocol_classes.classes_utils import Result
from src.domain.system.system_facade import SystemFacade
from src.domain.system.DAL import DAL


class ShoppingHandler:
    def __init__(self):
        self.logger = Log.get_instance().get_logger()
        self.sys: SystemFacade = SystemFacade.get_instance()
        self._dal: DAL = DAL.get_instance()

    def get_user_by_username(self, username: str):
        try:
            self.sys.renew_session()
            res: Result = self.sys.get_user_by_username_as_result(username)
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def watch_info_on_store(self, username: str, store_name: str):
        """
        watch information on specific store
        :param store_name: (str) the store name
        :return: Store info
        """
        # guest
        if username == "":
            self.sys.renew_session()
            res: Result = self.sys.watch_info_on_store(username, store_name)
            self.sys.drop_session()
            if res.succeed:
                store_info = res.data
                send = {'name': store_info['name'], 'initial_owner': store_info['initial_owner'],
                        'open': store_info['open'],
                        'creation_date': store_info['creation_date'], 'permissions': None}

                return Result(res.succeed, -1, res.msg, send)
            else:
                return res
        res: Result = self.get_user_by_username(username)
        if res.succeed:
            try:
                self.sys.renew_session()
                from src.domain.system.users_classes import LoggedInUser
                user: LoggedInUser = res.data
                if user is not None:
                    self.sys._dal.add(user, add_only=True)
                res: Result = self.sys.watch_info_on_store(username, store_name)
                if res.succeed:
                    store_info = res.data
                    send = {'name': store_info['name'], 'initial_owner': store_info['initial_owner'],
                            'open': store_info['open'],
                            'creation_date': store_info['creation_date'], 'permissions': None}
                    if user is not None and user.user_name in store_info['permissions']:
                        perm = store_info['permissions'][user.user_name]
                        send['permissions'] = {
                            'can_manage_inventory': perm.can_manage_inventory,
                            'can_appoint_new_store_owner': perm.appoint_new_store_owner,
                            'can_watch_purchase_history': perm.watch_purchase_history,
                            'can_open_close_store': perm.open_and_close_store,
                            'can_appoint_new_store_manager': perm.appoint_new_store_manager,
                            'can_manage_discount': perm.can_manage_discount
                        }
                    self.sys.drop_session()
                    return Result(res.succeed, res.requesting_id, res.msg, send)
                self.sys.drop_session()
                return Result(res.succeed, res.requesting_id, res.msg, None)

            except Exception as e:
                self.sys.drop_session()
                self.logger.error(f'ERROR: {str(e)}')
                return Result(False, -2, 'Something went wrong...', None)

    def watch_info_on_product(self, user_id: int, store_name: str, product_name: str):
        """
        watch information on specific store
        :param store_name: (str) the store name
        :param user_id: (int) the store name
        :param store_name: (str) the store name
        :param product_name: (str) the product name
        :return: product info from store
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.watch_info_on_product(user_id, store_name, product_name)
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def search_stores(self, user_id: int, store_search_name: str):
        """
        searching all stores that contains the given name
        :param user_id:(int) user searching
        :param store_search_name:(str) name to search
        :return: all the stores that contains this prefix as dictionaries
        """
        try:
            self.sys.renew_session()
            # todo check if this is ok- this doesnt currently check db
            res: Result = self.sys.search_stores(user_id, store_search_name)
            if res.succeed:
                self.logger.info(
                    f"user({user_id}) got {'all available stores' if store_search_name == '' else 'all stores with `' + store_search_name + '` in their name'}")
            else:
                self.logger.info(f"error in store search: {res.msg}")
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def search_products(self, user_id: int, product_name: str, stores_names: list = None, categories: list = None,
                        brands: list = None, min_price: float = None, max_price: float = None):
        """
        search in all stores for products that answers the search conditions
        :param product_name: (str) name of the products
        :param stores_names: (TypedList of str) name of wanted stores
        :param categories: (list of str) names of categories the products need to belong to (at least on of them)
        :param brands: (list of str) names of brands the product need to have (at least one)
        :param min_price: (float) minimum price for the product
        :param max_price: (float) maximum price for the product
        :return: list of Products that matching the desired the search conditions
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.search_products(user_id, product_name, stores_names, categories, brands, min_price,
                                                   max_price)
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def saving_product_to_shopping_cart(self, product_name: str, store_name: str,
                                        user_id: int, quantity: int):
        """
        saving the given product in shopping cart
        :param product_name: (str) name of the desired product
        :param store_name: (str) name of the store that have the product
        :param user_id: (id) username of the user who wants to add the item
        :param quantity: (int) quantity of the product
        :return: True if succeeded, False otherwise
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.saving_product_to_shopping_cart(product_name, store_name, user_id, quantity)
            if res.succeed:
                self.sys.drop_session()
                self.logger.info(
                    f'Saved Product({product_name})/Store({store_name})/'
                    f'Quantity({quantity}) to User({res.requesting_id}) shopping cart')
                return res
            else:
                self.logger.info(
                    f'Saved Product({product_name})/Store({store_name})/Quantity({quantity}) to User({res.requesting_id}) shopping cart failed')
                self.sys.drop_session()
                return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def watch_user_purchases(self, user_id: int):
        """
        Returns specific user purchases history
        :param user_id: (int) id of the user
        :return: List of Purchases done by the given user, empty list if there was an error or there were no purchases
                 at all
        """
        try:

            self.sys.renew_session()
            res: Result = self.sys.watch_user_purchases(user_id, "")
            if res.succeed:
                self.logger.info(
                    f"User({user_id}) requests to see its purchase history"
                )
            else:
                self.logger.info(
                    f'Failed getting list of all Purchases of User({user_id}), requested by User({user_id})')

            self.sys.drop_session()
            return res
        except Exception as e:

            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def propose_new_owner_to_store(self, user_id: int, candidate_name: str, store_name: str):
        err = f'Failed propose for Store({store_name}), requested by User({user_id})'
        try:
            self.sys.renew_session()
            res: Result = self.sys.propose_new_owner_to_store(user_id, candidate_name, store_name)
            if res.succeed:
                self.sys.drop_session()
                self.logger.info(
                    f'Proposed ({candidate_name}) for Store({store_name}), requested by User({user_id})')
                return res
            else:
                self.sys.drop_session()
                self.logger.info(res.msg)
                return res
        except:
            self.sys.drop_session()
            self.logger.info(err)
            return Result(False, -2, 'Something went wrong...', None)

    def respond_new_owner_to_store(self, user_id: int, candidate_name: str, store_name: str, response):
        err = f'Failed respond for Store({store_name}), requested by User({user_id})'
        try:

            self.sys.renew_session()
            res: Result = self.sys.respond_new_owner_to_store(user_id, candidate_name, store_name, response)
            if res.succeed:
                self.sys.drop_session()
                self.logger.info(
                    f'Respond ({candidate_name}) for Store({store_name}), requested by User({user_id})')
                return res
            else:

                self.sys.drop_session()
                self.logger.info(res.msg)
                return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.info(f"ERROR -> {str(e)}")
            return Result(False, -2, 'Something went wrong...', None)

    def fetch_awaiting_approvals(self, user_id: int, store_name: str):
        err = f'Failed getting list of all awaiting approvals of Store({store_name}), requested by User({user_id})'
        try:

            self.sys.renew_session()
            res: Result = self.sys.fetch_awaiting_approvals(user_id, store_name)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(f"Fetch all awaiting approvals of Store({store_name}) for User({user_id})")
                return res
            else:
                self.logger.info(res.msg)
                return res
        except:
            self.sys.drop_session()
            self.logger.info(err)
            return Result(False, -2, 'Something went wrong...', None)

    def watch_shopping_cart(self, user_id: int):
        """
        retrieve the shopping cart of the user
        :param user_id: (int) user id of the user to register
        :return: list of products in the shopping cart
        """
        try:

            self.sys.renew_session()
            res: Result = self.sys.watch_shopping_cart(user_id)
            self.sys.drop_session()
            if res.succeed:
                if res.succeed:
                    self.logger.info(
                        f"User({user_id}) requested to see it's shopping cart"
                    )
                else:
                    self.logger.info(
                        f"User({user_id}) failed to see it's shopping cart: {res.msg}"
                    )
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def removing_item_from_shopping_cart(self, product_name: str, store_name: str, user_id: int):
        """
        removing a given item from shopping item
        :param product_name: (str) name of product to remove
        :param store_name: (str) name of store
        :param user_id: (int) name of the user that want to remove the product
        :return: True if succeeded, False otherwise
        """
        try:

            self.sys.renew_session()
            res: Result = self.sys.removing_item_from_shopping_cart(product_name, store_name, user_id)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(
                    f'Removing  Product({product_name})/Store({store_name}) from User({user_id}) shopping cart')
            else:
                self.logger.info(
                    f'Removing Product({product_name})/Store({store_name}) from User({user_id}) shopping cart failed: {res.msg}')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def editing_quantity_shopping_cart_item(self, product_name: str, store_name: str, user_id: int, new_quantity: int):
        """
        editing quantity of item in shopping cart
        :param product_name: (str) product name to edit
        :param store_name: (str) store name where the product belong
        :param user_id: (id) username of the user that want to edit the quantity
        :param new_quantity:(int) new quantity of the product
        :return: True if succeeded, False otherwise
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.editing_quantity_shopping_cart_item(product_name, store_name, user_id, new_quantity)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(
                    f'Updated Product({product_name})/Store({store_name})/Quantity({new_quantity}) to User({user_id}) shopping cart')
            else:
                self.logger.info(
                    f'Updated Product({product_name})/Store({store_name})/Quantity({new_quantity}) to User({user_id}) shopping cart failed: {res.msg}')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def purchase_items(self, user_id: int, credit_card_number: int, country: str, city: str,
                       street: str, house_number: int, expiry_date: str, ccv: str, holder: str, holder_id: str,
                       apartment: str = "0",
                       floor: int = 0):
        """
        purchasing all the items in the shopping cart
        :param expiry_date:
        :param holder_id:
        :param ccv: 3 numbers behind the credit card
        :param holder:
        :param user_id:(int) id of the purchasing user
        :param credit_card_number: (int) credit card number to pay with
        :param country: country to send to
        :param city: city in country to send to
        :param street: street in city to send to
        :param house_number: house number in street
        :param apartment: apartment identifier in house
        :param floor: floor of the apartment
        :return: Result object for purchasing result
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.purchase_items(user_id, credit_card_number, country, city, street, house_number,
                                                  expiry_date, ccv, holder, holder_id,
                                                  apartment,
                                                  floor)

            self.sys.drop_session()
            return res
        except Exception as e:

            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)
