from src.communication.notification_handler import Category, StatManager
from src.domain.system.DAL import DAL
from src.domain.system.data_handler import DataHandler
from src.domain.system.users_classes import User, LoggedInUser
from src.protocol_classes.classes_utils import Result


class SystemAdmin:
    """
    Class for performing administration actions in general
    """

    def __init__(self, data_handler: DataHandler):
        self._data_handler: DataHandler = data_handler
        self._dal: DAL = DAL.get_instance()

    def _get_and_check_login_user(self, user_id: int):
        """
        retrieve a registered in user from data handler.
        :param user_id:(int) id of the wanted user
        :return: logged in user by with that id. if the user does not exists or it's not registered, return None
        """
        user: User = self._data_handler.get_user_by_id(user_id)
        if user is None or user.user_state is None:  # if not exists or not registered
            return None
        self._dal.add(user.user_state, add_only=True)
        return user

    def watch_all_purchases(self, requesting_user: int):
        """
        Returns specific user purchases history
        :param requesting_user: The user who requests this view(some manager or the user itself)
        :return: Result object containing a list of requested purchases
        """
        user: User = self._get_and_check_login_user(requesting_user)
        if user is None:
            return Result(False, requesting_user, "requesting user must be logged in", None)
        elif user.is_admin():
            output = self._dal.get_all_purchases()
            for p in output:
                self._dal.add(p, add_only=True)
            return Result(True, requesting_user, "Purchases retrieved",
                          [p.to_dictionary() for p in output])
        else:
            return Result(False, requesting_user, "only admins have permission for such action", None)

    def add_admin(self, requesting_user_id: int, requested_user: str):
        """
        adds a new admin to the system
        :param requesting_user_id: id of an existing admin
        :param requested_user: name of the user to turn to admin
        :return: Result with info on the process
        """
        from src.domain.system.users_classes import User
        user: User = self._get_and_check_login_user(requesting_user_id)
        if user is None:
            return Result(False, requesting_user_id, "requesting user must be registered user, and logged in", None)
        elif not user.is_admin():
            return Result(False, requesting_user_id, "only admins have permission for such action", None)
        to_promote: LoggedInUser = self._data_handler.get_user_by_username(requested_user)
        self._dal.add(to_promote, add_only=True)
        if to_promote is None:
            return Result(False, requesting_user_id, "requested user was not found", None)
        else:
            from src.domain.system.permission_classes import Permission, Role
            # perm: Permission = Permission.define_permissions_for_init(Role.system_manager, requested_user, None, None)
            # self._dal.add(perm, add_only=True)
            to_promote._admin_counter = 1

            # to_promote.add_permission(perm)
            # self._dal.add_all([perm, to_promote.user_state, to_promote])
            StatManager.get_instance().transition(Category.system_manager.to_string(), to_promote.get_category())
            return Result(True, requesting_user_id, f"'{requested_user}' is now an admin", None)
