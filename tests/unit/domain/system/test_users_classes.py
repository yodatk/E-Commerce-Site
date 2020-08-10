import os

import pytest

from src.domain.system.users_classes import UserSystemHandler, LoggedInUser, User
from src.domain.system.data_handler import DataHandler
from tests.db_config_tests import test_flask


data_handler: DataHandler = None
user_handler: UserSystemHandler = None


@pytest.fixture(scope="session", autouse=True)
def set_up_test(request):
    # setting db in debug mode
    global data_handler
    with test_flask.app_context():
        try:
            os.remove('db_test.db')
            print("Removed DB")
        except:
            print("Removed db failed")
        data_handler = DataHandler()
        data_handler.create_all(lambda dbi: dbi.init_app(test_flask))
        # data_handler.register(-1, "root@gmail.com", "root_user", "passworD1$")
        set_up()
        tear_down()


def set_up():
    global user_handler, data_handler
    data_handler = DataHandler()
    user_handler = UserSystemHandler(data_handler)


def tear_down():
    data_handler.users.clear()


# LoggedInUser tests:

def test_check_input_type_logged_in_user():
    """
    checks the constructor type-checking
    """
    with pytest.raises(TypeError):
        LoggedInUser(5, "password", "mail")
        LoggedInUser("qwe", 5, "mail")
        LoggedInUser("qwe", "twet", 7)
        LoggedInUser("user", "user@mail.com", "qweqw")


# User tests:

@pytest.mark.parametrize("test_input, output", [(User(1), False)])
def test_is_registered_negative(test_input, output):
    assert test_input.is_registered() == output


def test_is_registered_positive():
    user = User(1)
    user.register("user", "Parker51!", "user@mail.com")
    assert user.is_registered()


@pytest.mark.parametrize("user_id, output", [(3, False)])
def test_logout_unregistered_user(user_id, output):
    user = User(user_id)
    assert user.logout() == output


@pytest.mark.parametrize("user_id, output", [(50, True)])
def test_logout_success(user_id, output):
    user = User(user_id)
    user.register("user2", "Parker51!", "user2@mail.com")
    user.login()
    assert user.logout() == output


# @pytest.mark.parametrize("user_id, output", [(2, False)])
# def test_logout_already_not_connected(user_id, output):
#     user = User(user_id)
#     user.register("user23", "Parker51!", "user23@mail.com")
#     assert user.logout() == output
