import os

import pytest

from tests.acceptance.bridge.proxy_bridge import AcceptanceTestError
from tests.acceptance.bridge.real_bridge import RealBridge
from tests.acceptance.test_suites.test_data.acceptance_test_data_object import AcceptanceTestDataObject
from tests.db_config_tests import test_flask

file_name = os.path.splitext(os.path.basename(__file__))[0]
data_obj = AcceptanceTestDataObject(file_name)
# bridge = ProxyBridge()  # change line for implementation
bridge = RealBridge()


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


# AT 3.2.1  SUCCESS: logged in user opens store
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("3.2.1"))
def test_3_2_1(test_id, test_input, expected):
    store_owner, owner_password = bridge.setup_anonymous_user(-1, test_id)
    user_id = bridge.login(store_owner, owner_password)
    try:
        bridge.open_store(user_id, *test_input)
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id, store_owner)


# AT 3.2.2  FAIL: user fails to open store since he is not logged in user
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("3.2.2"))
def test_3_2_2(test_id, test_input, expected):
    user_id = -1
    with pytest.raises(AcceptanceTestError):
        bridge.open_store(user_id, *test_input)


# AT 4.1.1.1  SUCCESS: store owner adds item to inventory
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.1.1.1"))
def test_4_1_1_1(test_id, test_input, expected):
    user_id = -1
    store_name, store_owner, password = bridge.setup_anonymous_store(user_id, test_id)
    user_id = bridge.login(store_owner, password)
    try:
        bridge.add_item_to_store(user_id, store_name, *test_input)
    except AcceptanceTestError as e:
        pytest.fail(str(e))


# AT 4.1.1.2  FAIL: store owner fails to add item to inventory since store doesn't exist
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.1.1.2"))
def test_4_1_1_2(test_id, test_input, expected):
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, test_id)
    user_id = bridge.login(store_owner, owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.add_item_to_store(user_id, "doesn't exist", *test_input)
        bridge.logout(user_id, store_owner)


# AT 4.1.2.1  SUCCESS: store owner removes item from store inventory
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.1.2.1"))
def test_4_1_2_1(test_id, test_input, expected):
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, test_id)
    user_id = bridge.login(store_owner, owner_password)
    bridge.add_item_to_store(user_id, store_name, *test_input)
    try:
        bridge.remove_item_from_store(user_id, store_name, test_input[0])
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id, store_owner)


# AT 4.1.2.2  FAIL: store owner fails to remove item from store inventory, since didn't exist in first place
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.1.2.2"))
def test_4_1_2_2(test_id, test_input, expected):
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, test_id)
    user_id = bridge.login(store_owner, owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.remove_item_from_store(user_id, store_name, test_input[0])
        bridge.logout(user_id, store_owner)


# AT 4.1.3.1  SUCCESS: store owner updates item in store
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.1.3.1"))
def test_4_1_3_1(test_id, test_input, expected):
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, test_id)
    user_id = bridge.login(store_owner, owner_password)
    bridge.add_item_to_store(user_id, store_name, *test_input, 50)
    try:
        bridge.update_item_in_store(user_id, store_name, *test_input, 50)
    except AcceptanceTestError:
        pytest.fail("Update item in inventory. Input: {}".format(str(test_input)))
    finally:
        bridge.logout(user_id, store_owner)


# AT 4.1.3.2  FAIL: user fails to update item in store to negative price
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.1.3.2"))
def test_4_1_3_2(test_id, test_input, expected):
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, test_id)
    user_id = bridge.login(store_owner, owner_password)
    to_add = list(test_input)
    to_add[3] = 5  ## making sure price is positive for addition
    bridge.add_item_to_store(user_id, store_name, *to_add, 50)
    with pytest.raises(AcceptanceTestError):
        bridge.update_item_in_store(user_id, store_name, *test_input, 50)
        bridge.logout(user_id, store_owner)


# AT 4.2.1.1.1  Succeed: user tries to add new discount policy to product that doesn't exist
def test_4_2_1_1_1():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.1.1.1")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    discount_type = "2"
    percent = ""
    category = ""
    free_per_x = "1/3"
    overall_product_price = "bissli:20"
    overall_category_price = ""
    overall_product_quantity = ""
    overall_category_quantity = ""
    up_to_date = "14/06/2021"
    basket_size = ""
    try:
        bridge.add_discount(user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                            overall_product_price, overall_category_price, overall_product_quantity,
                            overall_category_quantity,
                            up_to_date, basket_size)
    except AcceptanceTestError:
        pytest.fail("Add discount failed")
    finally:
        bridge.logout(user_id, store_owner)


# AT 4.2.1.1.2  FAIL: user tries to do free per x with invalid values
def test_4_2_1_1_2():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.1.1.2")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    discount_type = "2"
    percent = ""
    category = ""
    free_per_x = "3/1"
    overall_product_price = "bissli:20"
    overall_category_price = ""
    overall_product_quantity = ""
    overall_category_quantity = ""
    up_to_date = "14/06/2021"
    basket_size = ""
    with pytest.raises(AcceptanceTestError):
        bridge.add_discount(user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                            overall_product_price, overall_category_price, overall_product_quantity,
                            overall_category_quantity,
                            up_to_date, basket_size)
        up_to_date = "14/06/1993"
        bridge.add_discount(user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                            overall_product_price, overall_category_price, overall_product_quantity,
                            overall_category_quantity,
                            up_to_date, basket_size)


# AT 4.2.1.2.1  SUCCESS: user  edits discount policy
def test_4_2_1_2_1():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.1.2.1")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    discount_type = "2"
    percent = ""
    category = ""
    free_per_x = "1/3"
    overall_product_price = "bissli:20"
    overall_category_price = ""
    overall_product_quantity = ""
    overall_category_quantity = ""
    up_to_date = "14/06/2021"
    basket_size = ""
    discount_id = bridge.add_discount(user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                                      overall_product_price, overall_category_price, overall_product_quantity,
                                      overall_category_quantity,
                                      up_to_date, basket_size)
    try:
        free_per_x = "1/5"
        bridge.edit_discount(user_id, discount_id, store_name, product_name, discount_type, percent, category,
                             free_per_x, overall_product_price,
                             overall_category_price, overall_product_quantity, overall_category_quantity,
                             up_to_date, basket_size)


    except AcceptanceTestError:
        pytest.fail("Edit discount failed")
    finally:
        bridge.logout(user_id, store_owner)


# AT 4.2.1.2.2  FAIL: user tries to edit discount policy that doesn't exist (wrong discount id)
def test_4_2_1_2_2():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.1.2.2")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    discount_type = "2"
    percent = ""
    category = ""
    free_per_x = "1/3"
    overall_product_price = "bissli:20"
    overall_category_price = ""
    overall_product_quantity = ""
    overall_category_quantity = ""
    up_to_date = "14/06/2021"
    basket_size = ""
    bridge.add_discount(user_id, store_name, product_name, discount_type, percent, category,
                        free_per_x,
                        overall_product_price, overall_category_price, overall_product_quantity,
                        overall_category_quantity,
                        up_to_date, basket_size)

    with pytest.raises(AcceptanceTestError):
        free_per_x = "1/5"
        bridge.edit_discount(user_id, 100, store_name, product_name, discount_type, percent, category,
                             free_per_x, overall_product_price,
                             overall_category_price, overall_product_quantity, overall_category_quantity,
                             up_to_date, basket_size)
        bridge.logout(user_id, store_owner)


# AT 4.2.1.3.1  SUCCESS: user removes discount policy
def test_4_2_1_3_1():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.1.3.1")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    discount_type = "2"
    percent = ""
    category = ""
    free_per_x = "1/3"
    overall_product_price = "bissli:20"
    overall_category_price = ""
    overall_product_quantity = ""
    overall_category_quantity = ""
    up_to_date = "14/06/2021"
    basket_size = ""
    discount_id = bridge.add_discount(user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                                      overall_product_price, overall_category_price, overall_product_quantity,
                                      overall_category_quantity,
                                      up_to_date, basket_size)
    try:
        bridge.remove_discount(user_id, discount_id, store_name)
    except AcceptanceTestError:
        pytest.fail("Remove discount failed")
    finally:
        bridge.logout(user_id, store_owner)


# AT 4.2.1.3.2  FAIL: user tries to remove discount policy with id doesn't exist
def test_4_2_1_3_2():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.1.3.2")
    user_id = bridge.login(store_owner, owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.remove_discount(user_id, 10, store_name)


# AT 4.2.2.1.1  SUCCESS: user adds new purchase policy
def test_4_2_2_1_1():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.2.1.1")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    category = "snack"
    min_basket_quantity = 3
    max_basket_quantity = 6
    min_product_quantity = 5
    max_product_quantity = 20
    min_category_quantity = 1
    max_category_quantity = 3
    day = "14/06/2021"
    try:
        bridge.add_policy(user_id, store_name, min_basket_quantity, max_basket_quantity, product_name,
                          min_product_quantity,
                          max_product_quantity, category, min_category_quantity, max_category_quantity, day)
    except AcceptanceTestError:
        pytest.fail("Add purchase policy discount failed")
    finally:
        bridge.logout(user_id, store_owner)


# AT 4.2.2.1.2  FAIL: user tries to add new purchase policy without proper fields
def test_4_2_2_1_2():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.2.1.2")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    category = "snack"
    min_basket_quantity = 3
    max_basket_quantity = 6
    min_product_quantity = 5
    max_product_quantity = 20
    min_category_quantity = None
    max_category_quantity = None
    day = "14/06/2021"
    with pytest.raises(AcceptanceTestError):
        bridge.add_policy(user_id, store_name, min_basket_quantity, max_basket_quantity, product_name,
                          min_product_quantity,
                          max_product_quantity, category, min_category_quantity, max_category_quantity, day)


# AT 4.2.2.2.1  SUCCESS: user edits purchase policy
def test_4_2_2_2_1():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.2.2.1")
    user_id = bridge.login(store_owner, owner_password)
    product_name = "bissli"
    category = "snack"
    min_basket_quantity = 3
    max_basket_quantity = 6
    min_product_quantity = ""
    max_product_quantity = ""
    min_category_quantity = ""
    max_category_quantity = ""
    day = ""
    policy_id = bridge.add_policy(user_id, store_name, min_basket_quantity, max_basket_quantity, product_name,
                                  min_product_quantity,
                                  max_product_quantity, category, min_category_quantity, max_category_quantity, day)
    try:
        max_basket_quantity = 5
        bridge.edit_policy(user_id, store_name, policy_id, min_basket_quantity, max_basket_quantity, product_name,
                           min_product_quantity,
                           max_product_quantity, category, min_category_quantity, max_category_quantity, day)
    except AcceptanceTestError:
        pytest.fail("Add purchase policy discount failed")
    finally:
        bridge.logout(user_id, store_owner)


# AT 4.2.2.3.2  FAIL: user tries to remove purchase policy to product with wrong id
def test_4_2_2_3_2():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "4.2.2.3.2")
    user_id = bridge.login(store_owner, owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.remove_policy(user_id, store_name, 5)


# AT 4.3.1  SUCCESS: store owner appoints another store owner
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.3.1"))
def test_4_3_1(test_id, test_input, expected):
    appointed_id = store_owner_id = -1
    appointed, _ = bridge.setup_anonymous_user(appointed_id, f"{test_id}_appointed")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        bridge.appoint_store_owner(store_owner_id, store_name, appointed)
    except AcceptanceTestError:
        pytest.fail("Appoint store owner failed")
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_id, appointed)


# AT 4.3.2  FAIL: store owner fails to appoint another store owner because user doesn't exist
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.3.2"))
def test_4_3_2(test_id, test_input, expected):
    user_id = -1
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(user_id, test_id)
    user_id = bridge.login(store_owner, store_owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.appoint_store_owner(user_id, store_name, *test_input)
        bridge.logout(user_id, store_owner)


# AT 4.5.1  SUCCESS: store owner appoints store manager
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.5.1"))
def test_4_5_1(test_id, test_input, expected):
    appointed_id = store_owner_id = -1
    appointed_user, _ = bridge.setup_anonymous_user(appointed_id, f"{test_id}_appointed")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        bridge.appoint_store_manager(store_name, store_owner_id, appointed_user)
    except AcceptanceTestError:
        pytest.fail("Appoint store manager failed")
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_id, appointed_user)


# AT 4.5.2  FAIL: store owner fails to appoint store manager who is already a manager in the store
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.5.2"))
def test_4_5_2(test_id, test_input, expected):
    store_owner_id = -1
    store_name, store_owner, store_owner_password, manager_username, manager_password = \
        bridge.setup_store_with_manager_setup_anonymous(store_owner_id, test_id)
    store_owner_id = bridge.login(store_owner, store_owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.appoint_store_manager(store_name, store_owner_id, manager_username)
        bridge.logout(store_owner_id, store_owner)


# AT 4.6.1  SUCCESS: store owner changes store manager's permissions
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.6.1"))
def test_4_6_1(test_id, test_input, expected):
    owner_id = -1
    store_name, owner_username, owner_password, manager_username, manager_password = \
        bridge.setup_store_with_manager_setup_anonymous(owner_id, test_id)
    owner_id = bridge.login(owner_username, owner_password)
    manager_id = bridge.login(manager_username, manager_password)

    owner_appoint_username, _ = bridge.setup_anonymous_user(-1, test_id + "_owner_to_appoint")
    manager_appoint_username, _ = bridge.setup_anonymous_user(-1, test_id + "_manager_to_appoint")
    store_info_lst = [store_name, owner_id, manager_username]
    permission_list: list = [False] * 8
    try:
        bridge.change_manager_permissions(*store_info_lst, *permission_list)
        bridge.login(manager_username, manager_password)
        helper_for_permission(0, permission_list, store_info_lst, bridge.add_item_to_store,
                              [manager_id, store_name, "cornflakes", "cereal", "kellogs", 20.99, 20],
                              "manage inventory")

        helper_for_permission(2, permission_list, store_info_lst, bridge.appoint_store_manager,
                              [store_name, manager_id, manager_appoint_username], "appoint a store manager")

        helper_for_permission(6, permission_list, store_info_lst, bridge.close_store,
                              [manager_id, store_name], "open or close store")

        pass
    except AcceptanceTestError as e:
        pytest.fail(str(e))


def helper_for_permission(index, permission_list, store_info_lst, func, arg_list, msg):
    try:
        print("-------------TESTING '{msg}' PERMISSIONS--------------------".format(msg=msg))
        func(*arg_list)
        pytest.fail("FAIL: should not be allowed to {msg}".format(msg=msg))
    except AcceptanceTestError:
        try:
            permission_list[index] = True
            bridge.change_manager_permissions(*store_info_lst, *permission_list)
            func(*arg_list)
        except AcceptanceTestError:
            pytest.fail("FAIL: should be allowed to {msg}".format(msg=msg))


# AT 4.6.2  FAIL: store owner fails to change store manager's permissions for store that he doesn't own
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.6.2"))
def test_4_6_2(test_id, test_input, expected):
    user_id = -1
    store_name, owner_username, owner_password, manager_username, manager_password = \
        bridge.setup_store_with_manager_setup_anonymous(user_id, test_id)
    store_name_temp, store_owner_temp, store_owner_temp_pwd = bridge.setup_anonymous_store(user_id, f"{test_id}_other")
    permission_list: list = [True] * 8
    user_id = bridge.login(store_owner_temp, store_owner_temp_pwd)
    with pytest.raises(AcceptanceTestError):
        bridge.change_manager_permissions(store_name, user_id, manager_username, *permission_list)


# AT 4.7.1  SUCCESS: store owner removed store manager
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.7.1"))
def test_4_7_1(test_id, test_input, expected):
    user_id = -1
    store_name, owner_username, owner_password, manager_username, manager_password = \
        bridge.setup_store_with_manager_setup_anonymous(user_id, test_id)
    user_id = bridge.login(owner_username, owner_password)
    try:
        bridge.remove_store_manager(store_name, user_id, manager_username)
    except AcceptanceTestError:
        pytest.fail("Remove store manager failed")
    finally:
        bridge.logout(user_id, owner_username)


# AT 4.7.2  FAIL: store owner fails to remove store manager since he is not in owners store
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.7.2"))
def test_4_7_2(test_id, test_input, expected):
    store_name, owner_username, owner_password, _, _ = bridge.setup_store_with_manager_setup_anonymous(-1, test_id)
    _, _, _, manager_username, _ = bridge.setup_store_with_manager_setup_anonymous(-1, f"{test_id}_other")

    user_id = bridge.login(owner_username, owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.remove_store_manager(store_name, user_id, manager_username)


# AT 4.8.1  SUCCESS: store owner removed store owner
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.1"))
def test_4_8_1(test_id, test_input, expected):
    user_id = -1
    store_name, owner_username, owner_password, other_owner_username, other_owner_password = bridge.setup_store_with_other_owner_setup_anonymous(
        user_id, test_id)
    user_id = bridge.login(owner_username, owner_password)
    try:
        bridge.remove_store_owner(store_name, user_id, other_owner_username)
    except AcceptanceTestError:
        pytest.fail("Remove store manager failed")
    finally:
        bridge.logout(user_id, owner_username)


# AT 4.8.1.1  SUCCESS: Adding 3rd owner after other two agrees
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.1.1"))
def test_4_8_1_1(test_id, test_input, expected):
    appointed_first_id = appointed_second_id = store_owner_id = -1
    appointed_first, pass_first = bridge.setup_anonymous_user(appointed_first_id, f"{test_id}_appointed_first")
    appointed_second, pass_second = bridge.setup_anonymous_user(appointed_second_id, f"{test_id}_appointed_second")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_first)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_second)
        appointed_first_id = bridge.login(appointed_first, pass_first)
        res = bridge.approve_owner(appointed_first_id, appointed_second, store_name)
        appointed_second_id = bridge.login(appointed_second, pass_second)
        res = bridge.add_item_to_store(appointed_second_id, store_name, "temp_product", "Food", "Nike", 5.0, 1)
    except AcceptanceTestError as e:
        pytest.fail(f"Appoint store owner failed : {str(e)}")
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_first_id, appointed_first)
        bridge.logout(appointed_second_id, appointed_second)


# AT 4.8.1.1.1  Failed: trying to approve an owner that does not exists
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.1.1.1"))
def test_4_8_1_1_1(test_id, test_input, expected):
    appointed_first_id = appointed_second_id = store_owner_id = -1
    appointed_first, pass_first = bridge.setup_anonymous_user(appointed_first_id, f"{test_id}_appointed_first")
    appointed_second, pass_second = bridge.setup_anonymous_user(appointed_second_id, f"{test_id}_appointed_second")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_first)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_second)
        appointed_first_id = bridge.login(appointed_first, pass_first)
        with pytest.raises(AcceptanceTestError):
            res = bridge.approve_owner(appointed_first_id, "not_exists", store_name)
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_first_id, appointed_first)
        bridge.logout(appointed_second_id, appointed_second)


# AT 4.8.1.1.2  Failed: trying to approve an owner that is already an owner
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.1.1.2"))
def test_4_8_1_1_2(test_id, test_input, expected):
    appointed_first_id = appointed_second_id = store_owner_id = -1
    appointed_first, pass_first = bridge.setup_anonymous_user(appointed_first_id, f"{test_id}_appointed_first")
    appointed_second, pass_second = bridge.setup_anonymous_user(appointed_second_id, f"{test_id}_appointed_second")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_first)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_second)
        appointed_first_id = bridge.login(appointed_first, pass_first)
        with pytest.raises(AcceptanceTestError):
            res = bridge.approve_owner(appointed_first_id, store_owner, store_name)
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_first_id, appointed_first)
        bridge.logout(appointed_second_id, appointed_second)


# AT 4.8.1.2  SUCCESS: NOT adding an owner after one approoved, and one denial
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.1.2"))
def test_4_8_1_2(test_id, test_input, expected):
    appointed_first_id = appointed_second_id = store_owner_id = -1
    appointed_first, pass_first = bridge.setup_anonymous_user(appointed_first_id, f"{test_id}_appointed_first")
    appointed_second, pass_second = bridge.setup_anonymous_user(appointed_second_id, f"{test_id}_appointed_second")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_first)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_second)
        appointed_first_id = bridge.login(appointed_first, pass_first)
        res = bridge.deny_owner(appointed_first_id, appointed_second, store_name)
        appointed_second_id = bridge.login(appointed_second, pass_second)
        with pytest.raises(AcceptanceTestError):
            res = bridge.add_item_to_store(appointed_second_id, store_name, "temp_product", "Food", "Nike", 5.0, 1)
    except AcceptanceTestError as e:
        pytest.fail(f"denying store owner failed : {str(e)}")
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_first_id, appointed_first)
        bridge.logout(appointed_second_id, appointed_second)


# AT 4.8.1.2.1  Failed: trying to deny an owner that does not exists
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.1.2.1"))
def test_4_8_1_2_1(test_id, test_input, expected):
    appointed_first_id = appointed_second_id = store_owner_id = -1
    appointed_first, pass_first = bridge.setup_anonymous_user(appointed_first_id, f"{test_id}_appointed_first")
    appointed_second, pass_second = bridge.setup_anonymous_user(appointed_second_id, f"{test_id}_appointed_second")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_first)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_second)
        appointed_first_id = bridge.login(appointed_first, pass_first)
        with pytest.raises(AcceptanceTestError):
            res = bridge.deny_owner(appointed_first_id, "not_exists", store_name)
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_first_id, appointed_first)
        bridge.logout(appointed_second_id, appointed_second)


# AT 4.8.1.2.2  Failed: trying to deny an owner that is already an owner
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.1.2.2"))
def test_4_8_1_2_2(test_id, test_input, expected):
    appointed_first_id = appointed_second_id = store_owner_id = -1
    appointed_first, pass_first = bridge.setup_anonymous_user(appointed_first_id, f"{test_id}_appointed_first")
    appointed_second, pass_second = bridge.setup_anonymous_user(appointed_second_id, f"{test_id}_appointed_second")
    store_name, store_owner, store_owner_password = bridge.setup_anonymous_store(store_owner_id, test_id)
    try:
        store_owner_id = bridge.login(store_owner, store_owner_password)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_first)
        res = bridge.appoint_store_owner(store_owner_id, store_name, appointed_second)
        appointed_first_id = bridge.login(appointed_first, pass_first)
        with pytest.raises(AcceptanceTestError):
            res = bridge.deny_owner(appointed_first_id, store_owner, store_name)
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(store_owner_id, store_owner)
        bridge.logout(appointed_first_id, appointed_first)
        bridge.logout(appointed_second_id, appointed_second)


# AT 4.8.2  FAIL: store owner fails to remove store owner since he is not in owners store
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("4.8.2"))
def test_4_8_2(test_id, test_input, expected):
    store_name, owner_username, owner_password, _, _ = bridge.setup_store_with_manager_setup_anonymous(-1, test_id)
    _, _, _, other_owner_username, _ = bridge.setup_store_with_other_owner_setup_anonymous(-1, f"{test_id}_other")

    user_id = bridge.login(owner_username, owner_password)
    with pytest.raises(AcceptanceTestError):
        bridge.remove_store_owner(store_name, user_id, other_owner_username)
