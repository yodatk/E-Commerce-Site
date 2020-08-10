import enum
import re
from datetime import datetime
from time import sleep

from src.communication.notification_handler import StatManager, Category, DailyStat, NotificationHandler
from src.domain.system.system_facade import SystemFacade
from src.domain.system.users_classes import User, LoggedInUser
from src.logger.log import Log
from src.protocol_classes.classes_utils import Result, TypeChecker
from src.security.security_system import Encrypter


class RegistrationErrors(enum.Enum):
    length_should_be_above_8 = 1
    missing_lowercase_letter_uppercase_letter_or_digit = 2
    email_is_not_valid = 3
    space_in_name = 4
    user_already_exist = 5


class UserHandler:
    def __init__(self, notification_handler: NotificationHandler):
        self.logger = Log.get_instance().get_logger()
        self.sys: SystemFacade = SystemFacade.get_instance()
        self.notification_handler = notification_handler

    def user_state_is_none(self, user_id: int):
        self.sys.renew_session()

        res: Result = self.sys.user_state_is_none(user_id)
        self.sys.drop_session()
        return res

    def get_store_by_name(self, storename: str):
        self.sys.renew_session()

        res: Result = self.sys.get_store_by_name(storename)
        self.sys.drop_session()
        return res

    def get_user_by_id_if_guest_create_one(self, user_id: int, user_name=None):
        self.sys.renew_session()
        res = self.sys.get_user_by_id_if_guest_create_one(user_id)
        self.sys.drop_session()
        return res

    def get_user_by_id(self, user_id: int):
        self.sys.renew_session()
        res: Result = self.sys.get_user_by_id(user_id)

        self.sys.drop_session()
        return res

    def get_user_by_username(self, username: str):
        self.sys.renew_session()
        res: Result = self.sys.get_user_by_username_as_result(username)

        self.sys.drop_session()
        return res

    def register(self, user_id: int, username: str, password: str, email: str):
        """
        registering a user if is not already in the system
        :param user_id: (int) user_id of the user to register
        :param username: (id) username of the user to register
        :param password: (str) encrypted password of the user to register
        :param email: (str) email of the user to register
        :return: Result object
        """
        try:
            self.sys.renew_session()
            if not (TypeChecker.check_for_non_empty_strings([username, password, email]) and type(user_id) is int):
                self.sys.drop_session()
                return Result(False, user_id, "One of the fields is empty", None)
                # initialise dictionary with possible reasons fot registration failure
            registration_errors = {RegistrationErrors.length_should_be_above_8: False,
                                   RegistrationErrors.missing_lowercase_letter_uppercase_letter_or_digit: False,
                                   RegistrationErrors.user_already_exist: False,
                                   RegistrationErrors.email_is_not_valid: False,
                                   RegistrationErrors.space_in_name: False}
            is_valid = True
            password_validation = Encrypter.password_check(password)
            if not password_validation['password_ok']:
                is_valid = False
                UserHandler.check_password_errors(password_validation, registration_errors)
            if not self.valid_email(email):
                is_valid = False
                registration_errors[RegistrationErrors.email_is_not_valid] = True
            for a in username:
                if a.isspace():
                    is_valid = False
                    registration_errors[RegistrationErrors.space_in_name] = True
            if self.sys.check_username_exist(username).succeed:
                is_valid = False
                registration_errors[RegistrationErrors.user_already_exist] = True
            if is_valid:
                password = Encrypter.hash_password(password)  # hash password
                try:
                    res: Result = self.sys.register(user_id, username, password, email)
                    if res.succeed:
                        self.logger.info(f'Registration succeeded: User({username})')
                        self.notification_handler.add_observer(username)
                        self.sys.drop_session()
                        return res
                    else:
                        self.logger.info(f'Registration failed: User({username})|Email({email}) with Reason({res.msg})')
                        self.sys.drop_session()
                        return res
                except Exception as e:
                    self.logger.error(f'ERROR: {str(e)}')
                    self.sys.drop_session()
                    return Result(False, -2, 'Something went wrong...', None)
        except Exception as e:
            self.logger.error(f'ERROR: {str(e)}')
            self.sys.drop_session()
            return Result(False, -2, 'Something went wrong...', None)

        else:
            output = ""
            for key, value in registration_errors.items():
                if value:
                    output += f"{key.name}|"
            output = output[:-1]
            self.logger.info(f"Register Failed: {output}")
            self.sys.drop_session()
            return Result(False, user_id, output, None)

    def login(self, user_id: int, username: str, password: str):
        """
        Logging a user if exists
        :param username: (str) username of the user to login
        :param password: (str) encrypted password of the user to login
        :return: Result object
        """
        try:
            self.sys.renew_session()
            if not (TypeChecker.check_for_non_empty_strings([username, password])):
                self.logger.info(f'Login Failed - "One of the fields is empty"')
                self.sys.drop_session()
                return Result(False, -1, "One of the fields is empty", None)
            if user_id == -1:
                user_id = self.sys.get_user_by_id_if_guest_create_one(user_id).data
            result: Result = self.sys.get_user_by_username_as_result(username)
            if result.data is None:
                self.logger.info(
                    f"Login failed: User({username}) with Reason - user was not found")
                self.sys.drop_session()
                return Result(False, -1, "Login Failed", None)
            user: LoggedInUser = result.data
            if result.succeed and Encrypter.verify_password(password, user.password):
                final_user_id = user_id if result.requesting_id == -1 else result.requesting_id
                res: Result = self.sys.login(final_user_id, user)
                if res.succeed:
                    self.logger.info(f'Login succeeded: User({username})')
                    is_admin = user.is_admin()
                    self.sys._dal.commit()
                    new_categ = user.get_category()
                    StatManager.get_instance().transition(new_categ, Category.guest.to_string())
                    self.sys.drop_session()
                    return Result(True, final_user_id, "Login successfully", is_admin)
                else:
                    self.sys.drop_session()
                    self.logger.info(
                        f"Login failed: User({username}) with Reason - cannot fine matching user for user id")
                    return Result(False, -1, " Username/Password mismatch", None)
            else:
                self.sys.drop_session()
                self.logger.info(f"Login failed: User({username}) with Reason - Username/Password mismatch")
                return Result(False, -1, "Login Failed", None)
        except Exception as e:
            self.sys.drop_session()
            self.logger.error(f"ERROR -> {str(e)}")
            return Result(False, -2, f"{str(e)}", None)

    def logout(self, user_id: int):
        """
        logging out the given username
        :param user_id: (int) user id of the user that wants to logout.
        :return: Result object with info on the process
        """
        self.sys.renew_session()
        if not (type(user_id) is int):
            msg = f"Logout Failed: The fields is empty"
            self.logger.info(msg)
            self.sys.drop_session()
            return Result(False, user_id, msg, None)
        if user_id == -1:
            msg = f"Logout Failed: logout method is enable only for registered user"
            self.logger.info(msg)
            self.sys.drop_session()
            return Result(False, user_id, msg, None)
        try:
            res: Result = self.sys.logout(user_id)
            if res.succeed:
                self.logger.info(f'Logout succeeded: User({user_id})')
                StatManager.get_instance().transition(Category.guest.to_string(), None)
                self.sys.drop_session()
                # username = self.get_user_by_id(user_id).data
                # self.notification_handler.disconnect(user_name)

                return Result(True, user_id, "logout succeeded", None)
            else:
                self.logger.info(f'Logout failed: User({user_id}) with Reason({res.msg})')
                self.sys.drop_session()
                return Result(False, user_id, "logout failed", None)
        except Exception as e:
            self.logger.error(f'ERROR: {str(e)}')
            self.sys.drop_session()
            return Result(False, -2, 'Something went wrong...', None)

    def is_admin(self, user_name: str):
        try:
            self.sys.renew_session()
            result: Result = self.sys.get_user_by_username_as_result(user_name)
            if result.succeed:
                is_admin = result.data.is_admin()
            else:
                is_admin = False
            self.sys.drop_session()
            return Result(True, -1, "answer in data", is_admin)
        except Exception as e:
            self.logger.error(f'ERROR: {str(e)}')
            self.sys.drop_session()
            return Result(False, -2, 'Something went wrong...', None)

    @staticmethod
    def check_password_errors(password_validation, registration_errors):
        """
        :param password_validation: result of check_password function
        :param registration_errors: dictionary with registration errors.
        :return: the function checks the errors occurs in user's password.
        """
        if password_validation['length_error']:
            registration_errors[RegistrationErrors.length_should_be_above_8] = True
        if (password_validation['digit_error'] or password_validation['uppercase_error']
                or password_validation['lowercase_error'] or password_validation['symbol_error']):
            registration_errors[RegistrationErrors.missing_lowercase_letter_uppercase_letter_or_digit] = True

    @staticmethod
    def valid_email(email: str):
        """
        The function checks that email is valid.
        :param email:
        :return: True - email is valid, otherwise, False
        """
        reg_exp_for_email = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        return re.search(reg_exp_for_email, email)


    def add_to_guest_counter(self):
        self.sys.renew_session()
        StatManager.get_instance().resume_after_init()
        StatManager.get_instance().transition(Category.guest.to_string())
        self.sys.drop_session()

    def init_counters(self, date, admin_counter, owner_counter, manager_counter, logged_in_counter, guest_counter):
        # return Result(True, -1, "", None)
        self.sys.renew_session()
        date = datetime.strptime(date, '%Y-%m-%d').date()
        new_day = DailyStat(date, admin_counter, owner_counter, manager_counter, logged_in_counter, guest_counter)
        self.sys._dal.add(new_day, add_only=True)
        self.sys.drop_session()
        return Result(True, -1, "", None)