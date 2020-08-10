import os

import pytest

from src.domain.system.data_handler import DataHandler
from tests.acceptance.bridge.proxy_bridge import AcceptanceTestError
from tests.acceptance.bridge.real_bridge import RealBridge
from tests.acceptance.test_suites.test_data.acceptance_test_data_object import AcceptanceTestDataObject
from tests.db_config_tests import test_flask

file_name = os.path.splitext(os.path.basename(__file__))[0]
# data_obj = AcceptanceTestDataObject(file_name)
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


# AT 6.4.1 add admin
# @pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("6.4.1"))
def test_6_4_1():
    with test_flask.app_context():
        try:
            bridge.register(-1, "root@gmail.com", "aviel", "passworD1$")
            uid = bridge.login("root_user", "passworD1$", -1)
            assert bridge.add_admin(uid, "aviel")
            assert bridge.is_admin("aviel")
        except AcceptanceTestError as e:
            pytest.fail(str(e))


# AT 6.4.2  add admin who is already an admin
# @pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("6.4.2"))
def test_6_4_2():
    with test_flask.app_context():
        try:
            bridge.register(-1, "root@gmail.com", "aviel", "passworD1$")
            uid = bridge.login("root_user", "passworD1$", -1)
            assert not bridge.add_admin(uid, "aviel")
            assert bridge.is_admin("aviel")
        except AcceptanceTestError as e:
            pass
