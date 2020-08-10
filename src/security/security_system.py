import re

from passlib.hash import pbkdf2_sha256

from src.protocol_classes.classes_utils import TypeChecker


# The following class uses the pbkdf2_sha256 class

class Encrypter:

    @staticmethod
    def hash_password(password):
        """
        The function hash the input password.
        :param password: given password that need to be hashed.
        :return: hashed password.
        """
        if TypeChecker.check_for_non_empty_strings([password]):
            return pbkdf2_sha256.hash(password)
        raise TypeError(f"expected string, instead got {type(password)}")

    @staticmethod
    def verify_password(provided_password, stored_password):
        """
        The function checks user input against an existing hash.
        :param provided_password: password of user.
        :param stored_password: an existing hash password.
        :return: True - the user password is correct and matched to the hash password.
                False - the user password is incorrect.
        """
        if TypeChecker.check_for_non_empty_strings([provided_password, stored_password]):
            return pbkdf2_sha256.verify(provided_password, stored_password)

    @staticmethod
    def password_check(password):
        """
        The function verify the strength of 'password'.
        :param password:
        :return: returns a dict indicating the wrong criteria
        A password is considered strong if:
            8 characters length or more
            1 digit or more
            1 symbol or more
            1 uppercase letter or more
            1 lowercase letter or more
        """
        if TypeChecker.check_for_non_empty_strings([password]):
            MINIMUM_LENGTH = 8
            DIGITS_REG_EXP = r"\d"
            UPPERCASE_REG_EXP = r"[A-Z]"
            LOWERCASE_REG_EXP = r"[a-z]"
            SYMBOLS_REF_EXP = r"[ !@#$%&'()*+,-./[\\\]^_`{|}~" + r'"]'
            # calculating the length
            length_error = len(password) < MINIMUM_LENGTH

            # searching for digits
            digit_error = re.search(DIGITS_REG_EXP, password) is None

            # searching for uppercase
            uppercase_error = re.search(UPPERCASE_REG_EXP, password) is None

            # searching for lowercase
            lowercase_error = re.search(LOWERCASE_REG_EXP, password) is None

            # searching for symbols
            symbol_error = re.search(SYMBOLS_REF_EXP, password) is None

            # overall result
            password_ok = not (length_error or digit_error or uppercase_error or lowercase_error or symbol_error)

            return {
                'password_ok': password_ok,
                'length_error': length_error,
                'digit_error': digit_error,
                'uppercase_error': uppercase_error,
                'lowercase_error': lowercase_error,
                'symbol_error': symbol_error,
            }
