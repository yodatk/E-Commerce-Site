import os

import pytest

from src.domain.system.data_handler import DataHandler
from tests.acceptance.bridge.proxy_bridge import AcceptanceTestError
from tests.acceptance.bridge.real_bridge import RealBridge
from tests.acceptance.test_suites.test_data.acceptance_test_data_object import AcceptanceTestDataObject
from tests.db_config_tests import test_flask

file_name = os.path.splitext(os.path.basename(__file__))[0]
data_obj = AcceptanceTestDataObject(file_name)
# bridge = ProxyBridge()  # change line for implementation
bridge = RealBridge()
data_handler = DataHandler.get_instance()


@pytest.fixture(scope="session", autouse=True)
def set_up_test(request):
    with test_flask.app_context():
        try:
            os.remove('db_test.db')
            print("Removed DB")
        except:
            print("Removed db failed")
        bridge.data_handler.create_all(lambda dbi: dbi.init_app(test_flask))
        bridge.register(-1, "root@gmail.com", "root_user", "passworD1$")


# @pytest.fixture(scope="session", autouse=True)
# def set_up_test(request):
#     with test_flask.app_context():
#         data_handler.create_all(lambda dbi: dbi.init_app(test_flask))

# check what is called and whats not
# def test_a():
#     data_handler.insert_some_fun()
#     assert True
#
# # check what is called and whats not
# def test_b():
#     data_handler.insert_some_fun()
#     assert True


# AT 2.2.1 SUCCESSFUL: successful register
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.2.1"))
def test_2_2_1(test_id, test_input, expected):
    user_id = -1
    try:
        bridge.register(user_id, *test_input)
    except AcceptanceTestError as e:
        pytest.fail(str(e))


# AT 2.2.2  FAIL: user tries registering with one or more fields empty
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.2.2"))
def test_2_2_2(test_id, test_input, expected):
    user_id = -1
    with pytest.raises(AcceptanceTestError):
        bridge.register(user_id, *test_input)


# AT 2.2.3 FAIL: user tries registering with one or more incorrect fields
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.2.3"))
def test_2_2_3(test_id, test_input, expected):
    user_id = -1
    with pytest.raises(AcceptanceTestError):
        bridge.register(user_id, *test_input)


# AT 2.2.4 FAIL: user tries registering with info of an already registered user
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.2.4"))
def test_2_2_4(test_id, test_input, expected):
    user_id = -1
    user_id = bridge.register(user_id, *test_input)
    with pytest.raises(AcceptanceTestError):
        bridge.register(user_id, *test_input)


# AT 2.3.1 SUCCESSFUL: successful login
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.3.1"))
def test_2_3_1(test_id, test_input, expected):
    user_id = -1
    email = "email@gmail.com"
    user_id = bridge.register(user_id, email, *test_input)
    try:
        bridge.login(*test_input, user_id)
    except AcceptanceTestError as e:
        pytest.fail(str(e))


# AT 2.3.2 FAIL: user tries logging in with one field empty
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.3.2"))
def test_2_3_2(test_id, test_input, expected):
    user_id = -1
    email = "email@gmail.com"
    user = "user_{test_case}".format(test_case=test_id) if test_input[0] == "" else test_input[0]
    password = "passworD123456&" if test_input[1] == "" else test_input[1]
    user_id = bridge.register(user_id, email, user, password)
    with pytest.raises(AcceptanceTestError):
        bridge.login(*test_input, user_id)


# AT 2.3.3 FAIL: user tries logging in with all fields empty
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.3.3"))
def test_2_3_3(test_id, test_input, expected):
    user_id = -1
    email = "email@gmail.com"
    user = "user_{test_case}".format(test_case=test_id)
    password = "passworD123456&"
    user_id = bridge.register(user_id, email, user, password)
    with pytest.raises(AcceptanceTestError):
        bridge.login(*test_input, user_id)


# AT 2.3.4 FAIL: user tries logging in but is not registered
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.3.4"))
def test_2_3_4(test_id, test_input, expected):
    with pytest.raises(AcceptanceTestError):
        bridge.login(*test_input)


# AT 3.1.1: SUCCESSFUL: successful logout
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("3.1.1"))
def test_3_1_1(test_id, test_input, expected):
    user_id = -1
    email = "email@gmail.com"
    username = test_input[0]
    bridge.register(user_id, email, *test_input)
    user_id = bridge.login(*test_input)
    assert bridge.logout(user_id, username)


# AT 3.1.2: FAIL: logout failed because user was not logged in in the first place
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("3.1.2"))
def test_3_1_2(test_id, test_input, expected):
    user_id = -1
    email = "email@gmail.com"
    username = test_input[0]
    user_id = bridge.register(user_id, email, *test_input)
    assert bridge.logout(user_id, username) == -1
