# import pytest
#
# from src.domain.system.data_handler import DataHandler
# from tests.db_config_tests import test_flask
#
# data_handler = DataHandler.get_instance()
# '''
# If got time, improvements here:
# - https://stackoverflow.com/questions/33848151/flask-sqlalchemy-pytest-not-rolling-back-my-session
#
# '''
# @pytest.fixture(scope="session", autouse=True)
# def set_up_test(request):
#     with test_flask.app_context():
#         data_handler.create_all(lambda dbi: dbi.init_app(test_flask))
#
# # check what is called and whats not
# def test_a():
#     data_handler.insert_some_fun()
#     assert True
#
# # check what is called and whats not
# def test_b():
#     data_handler.insert_some_fun()
#     assert True