import json
import threading

from src.communication.notification_handler import NotificationHandler
from src.service.shopping_interface.shopping_handler import ShoppingHandler
from src.service.store_inventory_interface.inventory_handler import InventoryHandler
from src.service.system_adminstration.sys_admin_handler import SysAdminHandler
from src.service.user_handler.user_handler import UserHandler
from src.logger.log import Log

PATH_TO_CONFIG_FILE = "init_config_story1.json"


class Initializer(threading.Thread):
    def __init__(self, thread_id, name, user_handler: UserHandler, inventory_handler: InventoryHandler,
                 shopping_handler: ShoppingHandler, admin_handler: SysAdminHandler, context,
                 notification_handler: NotificationHandler):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.name = name
        self.is_done = False
        self.user_handler: UserHandler = user_handler
        self.inventory_handler: InventoryHandler = inventory_handler
        self.shopping_handler: ShoppingHandler = shopping_handler
        self.admin_handler: SysAdminHandler = admin_handler
        self.context = context
        self.notification_handler: NotificationHandler = notification_handler

    def run(self):
        self.__init__app__()

    def activate_func_with_args(self, counter: int, function, function_name: str, args):
        res = function(**args)
        if not res.succeed:
            self.is_done = True
            log: Log = Log.get_instance()
            log.get_logger().error(
                f"ERROR IN INIT-> function number #{counter}, function name '{function_name}': {res.msg}")
            return False
        return True

    def __init__app__(self):
        with self.context:
            num_of_users: int = self.user_handler.sys._dal.get_num_of_registered_users()
            if num_of_users > 0:
                # TODO data base is already initialize -> ADD REGISTERED USERS TO APPEND MESSAGES, AND OBSERVERS AND SHIT
                self.notification_handler.init_notification_handler()
                exit()
            else:

                counter = 0
                res = True
                try:
                    with open(PATH_TO_CONFIG_FILE) as json_file:
                        data = json.load(json_file)
                    user_id = self.user_handler.get_user_by_id_if_guest_create_one(1).data
                    function_list = data['init_flow']
                    for function in function_list:
                        counter += 1
                        function_name = function["func"]
                        args = function["args"]
                        func = None
                        if 'user_id' in dict(args):
                            args['user_id'] = user_id

                        if function_name == "register":
                            func = self.user_handler.register

                        elif function_name == "login":
                            func = self.user_handler.login

                        elif function_name == "logout":
                            func = self.user_handler.logout

                        elif function_name == "new_store":
                            func = self.inventory_handler.opening_a_new_store

                        elif function_name == "close_store":
                            func = self.inventory_handler.close_store

                        elif function_name == "open_store":
                            func = self.inventory_handler.open_existing_store

                        elif function_name == "add_store_owner":
                            func = self.inventory_handler.adding_new_owner_to_store

                        elif function_name == "approve_new_owner":
                            func = self.shopping_handler.respond_new_owner_to_store

                        elif function_name == "deny_new_owner":
                            func = self.shopping_handler.respond_new_owner_to_store

                        elif function_name == "add_store_manager":
                            func = self.inventory_handler.adding_new_manager_to_store

                        elif function_name == "delete_owner_from_store":
                            func = self.inventory_handler.removing_store_owner

                        elif function_name == "delete_manager_from_store":
                            func = self.inventory_handler.removing_store_manager

                        elif function_name == "edit_permissions":
                            func = self.inventory_handler.editing_permissions_to_store_manager

                        elif function_name == "add_product_to_store":
                            func = self.inventory_handler.add_product_to_store

                        elif function_name == "edit_product":
                            func = self.inventory_handler.edit_existing_product_in_store

                        elif function_name == "remove_product":
                            func = self.inventory_handler.remove_product_to_store

                        elif function_name == "remove_discount":
                            func = self.inventory_handler.remove_discount

                        elif function_name == "new_discount":
                            func = self.inventory_handler.add_discount

                        elif function_name == "edit_discount":
                            func = self.inventory_handler.edit_discount

                        elif function_name == "combine_discount":
                            func = self.inventory_handler.combine_discount

                        elif function_name == "add_policies":
                            func = self.inventory_handler.add_policy

                        elif function_name == "remove_policy":
                            func = self.inventory_handler.remove_policy

                        elif function_name == "edit_policy":
                            func = self.inventory_handler.edit_policy

                        elif function_name == "combine_policies":
                            func = self.inventory_handler.combine_policies_for_store

                        elif function_name == "add_item_to_shopping_cart":
                            func = self.shopping_handler.saving_product_to_shopping_cart
                        elif function_name == "delete_item_from_shopping_cart":
                            func = self.shopping_handler.removing_item_from_shopping_cart
                        elif function_name == "update_item_from_shopping_cart":
                            func = self.shopping_handler.editing_quantity_shopping_cart_item
                        else:
                            log: Log = Log.get_instance()
                            log.get_logger().error(
                                f"INIT WENT WRONG ->in function #{counter} -> invalid function: {function_name}")
                            exit(-1)
                        res = self.activate_func_with_args(counter, func, function_name, args)
                        if not res:
                            self.is_done = True
                            break
                    if res:
                        log: Log = Log.get_instance()
                        log.get_logger().info(
                            f"### INIT IS DONE ###")
                        self.is_done = True
                    exit()

                    # todo
                    # only now can opening port in router
                    # todo

                except Exception as e:
                    log: Log = Log.get_instance()
                    log.get_logger().error(
                        f"INIT WENT WRONG -> {f'in function #{counter}' if counter > 0 else 'something wrong with file format:'} {str(e)}")
                    exit(-1)
