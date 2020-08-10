from src.logger.log import Log
from src.protocol_classes.classes_utils import Result
from src.domain.system.system_facade import SystemFacade


class SysAdminHandler:
    def __init__(self):
        self.logger = Log.get_instance().get_logger()
        self.sys = SystemFacade.get_instance()

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
                    f'list of Purchases for Store({store_name}) requested by User({requesting_user_id})')
            else:
                self.logger.info(
                    f'**Failed** getting list of Purchases for Store({store_name}) requested by User({requesting_user_id})')
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def watch_all_purchases(self, requesting_user_id: int):
        """
        Returns all purchases
        :param requesting_user_id:(int) Should be a an admin or other authorized user
        :return: List of all Purchases, empty list if there was an error or there were no purchases at all
        """
        try:

            self.sys.renew_session()
            res: Result = self.sys.watch_all_purchases(requesting_user_id)

            self.sys.drop_session()
            if res.succeed:
                self.logger.info(f'admin({requesting_user_id}) requested to se all purchases')
            else:
                self.logger.info(
                    f'**Failed** getting list of all Purchases, requested by User({requesting_user_id}): {res.msg}')
            return res
        except Exception as e:

            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def watch_user_purchases(self, requesting_user_id: int, requested_user: str):
        """
        Returns specific user purchases history
        :param requesting_user_id:(int) The user who requests this view(some manager or the user itself)
        :param requested_user:(str) The user, that his/she purchases is requested
        :return: List of Purchases done by the given user, empty list if there was an error or there were no purchases at all
        """
        try:
            self.sys.renew_session()
            res: Result = self.sys.watch_user_purchases(requesting_user_id, requested_user)
            self.sys.drop_session()
            if res.succeed:
                self.logger.info(
                    f'getting list of all Purchases of User({requesting_user_id}), requested by User({requested_user})')
            else:
                self.logger.info(
                    f'**Failed** getting list of all Purchases of User({requesting_user_id}), requested by User({requested_user})')
            return res
        except Exception as e:

            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def is_admin(self, username: str):
        try:
            self.sys.renew_session()
            res: Result = self.sys.is_admin(username)
            self.sys.drop_session()
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)

    def add_admin(self, requesting_user_id: int, requested_user: str):
        """
        adds a new admin to the system
        :param requesting_user_id: id of an existing admin
        :param requested_user: name of the user to turn to admin
        :return: Result with info on the process
        """
        try:

            self.sys.renew_session()
            res: Result = self.sys.add_admin(requesting_user_id, requested_user)

            self.sys.drop_session()
            if res.succeed:
                self.logger.info(f'{requested_user} is now an admin')
            else:
                self.logger.info(f"couldn't make {requested_user} to admin: {res.msg}")
            return res
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f'ERROR: {str(e)}')
            return Result(False, -2, 'Something went wrong...', None)
