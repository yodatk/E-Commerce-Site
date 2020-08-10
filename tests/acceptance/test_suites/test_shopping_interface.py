import ast
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

example_username_1 = "avib1"
example_username_2 = "avib2"
example_username_3 = "avib3"
example_username_4 = "avib4"
example_password = "passworD1$"
example_email = "email@email.com"
cc_good = 4444444444444444
cc_bad = 1

expecteds_search = [
    [{'store': 'store1',
      'details': {'item_name': 'kariyot', 'category': 'cereal', 'brand': 'talma', 'price': 12.99, 'quantity': 1}},
     {'store': 'store3',
      'details': {'item_name': 'kariyot', 'category': 'cereal', 'brand': 'osem', 'price': 8.99, 'quantity': 40}}],
    [{'store': 'store1',
      'details': {'item_name': 'chicken', 'category': 'meat', 'brand': 'maxs', 'price': 9.99, 'quantity': 50}}],
    []
]

# PURCHASE DICTIONERIES
purchase_info_data = [
    {
        "credit_card_number": 1111111111111111, "country": "Israel", "city": "Beer Sheva",
        "street": "koko1", "house_number": 1, "expiry_date": "12/23", "ccv": "123", "holder": "koko shtern",
        "holder_id": "111111111",
        "apartment": "0",
        "floor": 0
    },
    {
        "credit_card_number": 2222222222222222, "country": "Israel", "city": "Beer Sheva",
        "street": "koko2", "house_number": 1, "expiry_date": "12/23", "ccv": "123", "holder": "koko shtern",
        "holder_id": "222222222",
        "apartment": "0",
        "floor": 0
    },
    {
        "credit_card_number": 3333333333333333, "country": "Israel", "city": "Beer Sheva",
        "street": "koko3", "house_number": 1, "expiry_date": "12/23", "ccv": "123", "holder": "koko shtern",
        "holder_id": "333333333",
        "apartment": "0",
        "floor": 0
    },
    {
        "credit_card_number": 4444444444444444, "country": "Israel", "city": "Beer Sheva",
        "street": "koko4", "house_number": 1, "expiry_date": "12/23", "ccv": "123", "holder": "koko shtern",
        "holder_id": "444444444",
        "apartment": "0",
        "floor": 0
    },
]


def setup_example_user():
    bridge.register(-1, example_email, example_username_1, example_password)
    bridge.register(-1, example_email, example_username_2, example_password)
    bridge.register(-1, example_email, example_username_3, example_password)
    bridge.register(-1, example_email, example_username_4, example_password)


@pytest.fixture(scope="session", autouse=True)
def set_up_test(request):
    with test_flask.app_context():
        try:
            os.remove('db_test.db')
            print("Removed DB")
        except:
            print("Removed db failed")
        bridge.data_handler.create_all(lambda dbi: dbi.init_app(test_flask))
        bridge.setup_shopping(data_obj.set_up_shopping_data)
        setup_example_user()


# setup_example_user()


# AT 2.4.1.1 user view's item (success)
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.4.1.1"))
def test_2_4_1_1(test_id, test_input, expected):
    user_id = -1
    try:
        _, item_found = bridge.view_item(user_id, *test_input)
        item_expected = get_item_from_inventory(*test_input)
        assert items_are_equal(item_expected, item_found)
    except AcceptanceTestError as e:
        pytest.fail(str(e))


# AT 2.4.1.2 view item (fail) since item doesn't exist
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.4.1.2"))
def test_2_4_1_2(test_id, test_input, expected):
    user_id = -1
    with pytest.raises(AcceptanceTestError):
        bridge.view_item(user_id, *test_input)


# AT 2.4.2.1 view store (success)
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.4.2.1"))
def test_2_4_2_1(test_id, test_input, expected):
    user_id = -1
    try:
        _, store_found = bridge.view_store("", *test_input)
        store_expected = get_store_from_data(*test_input)
        are_equal = stores_are_equal(store_expected, store_found)
        assert are_equal
    except AcceptanceTestError as e:
        pytest.fail(str(e))


# AT 2.4.2.2 view store (fail) since store does not exist
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.4.2.2"))
def test_2_4_2_2(test_id, test_input, expected):
    with pytest.raises(AcceptanceTestError):
        bridge.view_store("", *test_input)


# AT 2.5.1 search items (success)
# consists of 2.5.1/2
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.5.1"))
def test_2_5_1(test_id, test_input, expected):
    criteria = row_to_criteria(test_input)
    expected_converted = expecteds_search[expected]

    _, items_found = bridge.search_for_items(-1, *criteria)

    assert lists_are_equal(expected_converted, items_found, viewable_items_equal)


# AT 2.5.3 search items (fail)
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.5.3"))
def test_2_5_3(test_id, test_input, expected):
    criteria = row_to_criteria(test_input)
    with pytest.raises(AcceptanceTestError):
        bridge.search_for_items(-1, *criteria)


# AT 2.6.1, 2.7.2, 2.7.2.1, 2.7.2.2, 2.7.2.3, SUCCESS: add item to cart
def test_2_6_1():
    item1 = {"store_name": "store1", "item_name": "tuna", "category": "fish", "brand": "sunfish", "price": 10.99,
             "quantity": 3}

    user_id = -1
    try:
        # --------VIEW EMPTY CART---------#
        user_id, res = bridge.view_cart(user_id)
        if res != "your cart is Empty":
            pytest.fail()
        # --------ADD ITEM---------#
        user_id = bridge.add_item_to_cart(user_id, item1["store_name"], item1["item_name"], item1["quantity"])
        # --------VIEW CART---------#
        user_id, res = bridge.view_cart(user_id)

        if not all([
            res['baskets'][0]['store'] == item1['store_name'],
            res['baskets'][0]['basket'][0]['product']['name'] == item1["item_name"],
            res['baskets'][0]['basket'][0]['quantity'] == item1["quantity"]
        ]):
            pytest.fail()

        # --------EDIT ITEM (addition)---------#
        item1["quantity"] = 4
        user_id = bridge.edit_item_in_cart(user_id, item1["store_name"], item1["item_name"], item1["quantity"])
        # --------VIEW CART---------#
        user_id, res = bridge.view_cart(user_id)
        if not all([
            res['baskets'][0]['store'] == item1['store_name'],
            res['baskets'][0]['basket'][0]['product']['name'] == item1["item_name"],
            res['baskets'][0]['basket'][0]['quantity'] == item1["quantity"]
        ]):
            pytest.fail()
        # user_id, password = bridge.register_login_user_just_name(user_id, "user_2.6.1_combined")
        # --------EDIT ITEM (reduction)---------#
        item1["quantity"] = 1
        user_id = bridge.edit_item_in_cart(user_id, item1["store_name"], item1["item_name"], item1["quantity"])
        # --------VIEW CART---------#
        user_id, res = bridge.view_cart(user_id)
        if not all([
            res['baskets'][0]['store'] == item1['store_name'],
            res['baskets'][0]['basket'][0]['product']['name'] == item1["item_name"],
            res['baskets'][0]['basket'][0]['quantity'] == item1["quantity"]
        ]):
            pytest.fail()

        # --------VIEW CART AFTER LOGIN---------#
        user_id, res = bridge.view_cart(user_id)
        if not all([
            res['baskets'][0]['store'] == item1['store_name'],
            res['baskets'][0]['basket'][0]['product']['name'] == item1["item_name"],
            res['baskets'][0]['basket'][0]['quantity'] == item1["quantity"]
        ]):
            pytest.fail()
        # --------EDIT ITEM (remove)---------#
        item1["quantity"] = 0
        user_id = bridge.edit_item_in_cart(user_id, item1["store_name"], item1["item_name"], item1["quantity"])
        # --------VIEW EMPTY CART---------#
        user_id, res = bridge.view_cart(user_id)
        if res != "your cart is Empty":
            pytest.fail()
        pass
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        pass
        # bridge.logout(user_id)


# AT 2.6.2 Saving product to shopping cart . FAIL: item does not exist in inventory
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.6.2"))
def test_2_6_2(test_id, test_input, expected):
    item1 = {"store_name": "store1", "item_name": "jalapeno", "category": "fish", "brand": "sunfish", "price": 10.99,
             "quantity": 3}

    with pytest.raises(AcceptanceTestError):
        bridge.add_item_to_cart(-1, item1["store_name"], item1["item_name"], item1["quantity"])


# AT 2.6.3: Saving product to shopping cart. FAIL: quantity must be greater than zero
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.6.3"))
def test_2_6_3(test_id, test_input, expected):
    item1 = {"store_name": "store1", "item_name": "tuna", "category": "fish", "brand": "sunfish", "price": 10.99,
             "quantity": -1}
    with pytest.raises(AcceptanceTestError):
        bridge.add_item_to_cart(-1, item1["store_name"], item1["item_name"], item1["quantity"])


# AT 2.7.2.4 - edit cart, FAIL: quantity must be greater than zero
@pytest.mark.parametrize("test_id, test_input,expected", data_obj.get_case_data("2.7.2.4"))
def test_2_7_2_4(test_id, test_input, expected):
    user_id = -1
    item1 = {"store_name": "store1", "item_name": "tuna", "category": "fish", "brand": "sunfish", "price": 10.99,
             "quantity": 3}
    bridge.add_item_to_cart(user_id, item1["store_name"], item1["item_name"], item1["quantity"])
    item1["quantity"] = -1
    with pytest.raises(AcceptanceTestError):
        bridge.edit_item_in_cart(user_id, item1["store_name"], item1["item_name"], item1["quantity"])


item1 = {"store_name": "store1", "item_name": "tuna", "category": "fish", "brand": "sunfish", "price": 0.99,
         "quantity": 3}
item2 = {"store_name": "store2", "item_name": "yogurt", "category": "dairy", "brand": "yotvata", "price": 0.99,
         "quantity": 7}
item3 = {"store_name": "store3", "item_name": "tomato", "category": "vegetable", "brand": "totzeret", "price": 5.99,
         "quantity": 7}


# 2.8.1.1 - purchase SUCCESS (no cancel):
#       1) first person succeeds and purchases (3)
#       2) second person succeeds and purchases (3)

# covers 2.8.1.1, 2.8.1.2, 2.8.1.4, 2.8.2.1
def test_2_8_1_1():
    user_id_2 = bridge.login(example_username_2, example_password)
    bridge.add_item_to_cart(user_id_2, item1["store_name"], item1["item_name"], item1["quantity"])
    item1["quantity"] = 1
    user_id_3 = bridge.login(example_username_3, example_password)
    bridge.add_item_to_cart(user_id_3, item1["store_name"], item1["item_name"], item1["quantity"])
    # Notice this is ok
    bridge.purchase(user_id_2, cc_good, purchase_info_data[1])  # , item1, 3)
    try:
        bridge.purchase(user_id_3, cc_good, purchase_info_data[2])  # , item1, 1)
        pass
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id_2, example_username_2)
        bridge.logout(user_id_3, example_username_3)


# 2.8.1.2 - PURCHASE SUCCESS (with cancel)
#       1) first person succeeds and purchases (7)
#       2) second person now can't buy full cart (because first one)
#       3) second person cancels
#       4) third person purchases what is possible (3)

# covers 2.8.1.1, 2.8.1.2, 2.8.1.4, 2.8.2.1
def test_2_8_1_2():
    user_id_2 = bridge.login(example_username_2, example_password)
    user_id_3 = bridge.login(example_username_3, example_password)
    bridge.add_item_to_cart(user_id_2, item2["store_name"], item2["item_name"], item2["quantity"])
    item2["quantity"] = 4
    bridge.add_item_to_cart(user_id_3, item2["store_name"], item2["item_name"], item2["quantity"])
    # notice this is ok
    bridge.purchase(user_id_2, cc_good, purchase_info_data[1])
    try:
        bridge.purchase(user_id_2, cc_good, purchase_info_data[1])
        pytest.fail("Should not be to purchase")
    except:
        pass

    user_id_4 = bridge.login(example_username_4, example_password)
    item2["quantity"] = 3
    try:
        bridge.add_item_to_cart(user_id_4, item2["store_name"], item2["item_name"], item2["quantity"])
        bridge.purchase(user_id_4, cc_good, purchase_info_data[3])
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id_2, example_username_2)
        bridge.logout(user_id_3, example_username_3)
        bridge.logout(user_id_4, example_username_4)


# 2.8.2_2 - FAIL: purchase because cc info bad
def test_2_8_2_2():
    user_id_3 = bridge.login(example_username_3, example_password)
    bridge.add_item_to_cart(user_id_3, item3["store_name"], item3["item_name"], item3["quantity"])
    try:
        bridge.purchase(user_id_3, cc_bad, purchase_info_data[2])  # , item3, item3["quantity"])
    except AcceptanceTestError:
        pass
    finally:
        bridge.logout(user_id_3, example_username_3)


# user views purchases - SUCCESS
def test_3_7_1():
    user_id_3 = bridge.login(example_username_3, example_password)
    try:
        purchase_list_found = bridge.view_user_purchases(user_id_3)
        assert len(purchase_list_found) == 1
        product_that_bought = purchase_list_found[0]['basket']['basket'][0]
        assert product_that_bought['product']['store_name'] == 'store1'
        assert product_that_bought['product']['name'] == 'tuna'

        assert product_that_bought['total_price'] == 0.99
        assert product_that_bought['quantity'] == 1
        # assert
        # 'name': 'tuna', 'brand': 'sunfish', 'categories': ['fish']
        # num_purchases = 0
        # contains = False
        # for entry in data_obj.set_up_shopping_data["Purchases"]:
        #     contains = False
        #     if entry["user_id"] == user_id_3:
        #         num_purchases = num_purchases + 1
        #         for entry_sys in purchase_list_found:
        #             if purchases_are_equal(entry, entry_sys):
        #                 contains = True
        #                 break
        #         if not contains:
        #             pytest.fail("purchase list does not include all of user's purchases")
        # if num_purchases != len(purchase_list_found):
        #     pytest.fail("purchase list inclusdes too many purchases")
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id_3, example_username_3)


# user views purchases - FAIL (not logged in)
def test_3_7_2():
    with pytest.raises(AcceptanceTestError):
        bridge.view_user_purchases(-1)


# store owner views purchases - SUCCESS
def test_4_10_1():
    user_id_1 = bridge.login("user1", "passworD134%")
    try:

        purchase_list_found = bridge.view_store_purchases(user_id_1, "store1")
        product_that_bought1 = purchase_list_found[0]['basket']['basket'][0]
        product_that_bought2 = purchase_list_found[1]['basket']['basket'][0]
        assert product_that_bought1['product']['store_name'] == 'store1'
        assert product_that_bought1['product']['name'] == 'tuna'

        assert product_that_bought1['total_price'] == 2.97
        assert product_that_bought1['quantity'] == 3

        assert product_that_bought2['product']['store_name'] == 'store1'
        assert product_that_bought2['product']['name'] == 'tuna'

        assert product_that_bought2['total_price'] == 0.99
        assert product_that_bought2['quantity'] == 1

        # num_purchases = 0
        # for entry in data_obj.set_up_shopping_data["Purchases"]:
        #     contains = False
        #     if entry['details']["store_name"] == "store1":
        #         num_purchases = num_purchases + 1
        #         for entry_sys in purchase_list_found:
        #             if purchases_are_equal(entry, entry_sys):
        #                 contains = True
        #                 break
        #         if not contains:
        #             pytest.fail("purchase list does not include all of user's purchases")
        # if num_purchases != len(purchase_list_found):
        #     pytest.fail("purchase list inclusdes too many purchases")
    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id_1, example_username_1)


# store owner views purchases - FAIL (not logged in)
def test_4_10_2():
    with pytest.raises(AcceptanceTestError):
        bridge.view_store_purchases(-1, "store1")


# 6.4_1 SUCCESS: look at purchase history -- system admin
def test_6_4_1():
    user_id = bridge.login("user1", "passworD134%")
    try:
        purchase_list_found = bridge.view_system_purchases(user_id)

        purchase1 = purchase_list_found[0]
        assert purchase1["user_name"] == "avib2"
        assert purchase1["basket"]["total_price"] == 2.97
        purchase1 = purchase1['basket']['basket']
        product1 = purchase1[0]['product']
        assert product1['store_name'] == 'store1'
        assert product1['name'] == 'tuna'

        purchase2 = purchase_list_found[1]
        assert purchase2["user_name"] == "avib3"
        assert purchase2["basket"]["total_price"] == 0.99
        purchase2 = purchase2['basket']['basket']
        product2 = purchase2[0]['product']
        assert product2['store_name'] == 'store1'
        assert product2['name'] == 'tuna'

        purchase3 = purchase_list_found[2]
        assert purchase3["user_name"] == "avib2"
        assert purchase3["basket"]["total_price"] == 6.93
        purchase3 = purchase3['basket']['basket']
        product3 = purchase3[0]['product']
        assert product3['store_name'] == 'store2'
        assert product3['name'] == 'yogurt'

        purchase4 = purchase_list_found[3]
        assert purchase4["user_name"] == "avib4"
        assert purchase4["basket"]["total_price"] == 2.97
        purchase4 = purchase4['basket']['basket']
        product4 = purchase4[0]['product']
        assert product4['store_name'] == 'store2'
        assert product4['name'] == 'yogurt'

    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id, "root_user")


# 6.4_1_2 watching at all purcheses when not logged in
def test_6_4_1_2():
    with pytest.raises(AcceptanceTestError):
        bridge.view_system_purchases(-1)


# 6.4_2_1 SUCCESS: look at purchase history of user -- system admin
def test_6_4_2_1():
    user_id = bridge.login("user1", "passworD134%")
    try:
        purchase_list_found = bridge.view_as_admin_user_purchases(user_id, "avib2")
        assert len(purchase_list_found) == 2
        purchase1 = purchase_list_found[0]
        assert purchase1["user_name"] == "avib2"
        assert purchase1["basket"]["total_price"] == 2.97
        purchase1 = purchase1['basket']['basket']
        product1 = purchase1[0]['product']
        assert product1['store_name'] == 'store1'
        assert product1['name'] == 'tuna'

        purchase3 = purchase_list_found[1]
        assert purchase3["user_name"] == "avib2"
        assert purchase3["basket"]["total_price"] == 6.93
        purchase3 = purchase3['basket']['basket']
        product3 = purchase3[0]['product']
        assert product3['store_name'] == 'store2'
        assert product3['name'] == 'yogurt'

    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id, "root_user")


# 6.4_2_2 Fail user does not exists:
def test_6_4_2_2():
    user_id = bridge.login("user1", "passworD134%")
    try:
        with pytest.raises(AcceptanceTestError):
            purchase_list_found = bridge.view_as_admin_user_purchases(user_id, "avibbibibibi2")
    finally:
        bridge.logout(user_id, "root_user")


# 6.4_3_1 get all purchases of a store
def test_6_4_3_1():
    user_id = bridge.login("user1", "passworD134%")
    try:
        purchase_list_found = bridge.view_as_admin_store_purchases(user_id, "store1")
        assert len(purchase_list_found) == 2
        purchase1 = purchase_list_found[0]
        assert purchase1["user_name"] == "avib2"
        assert purchase1["basket"]["total_price"] == 2.97
        purchase1 = purchase1['basket']['basket']
        product1 = purchase1[0]['product']
        assert product1['store_name'] == 'store1'
        assert product1['name'] == 'tuna'

        purchase2 = purchase_list_found[1]
        assert purchase2["user_name"] == "avib3"
        assert purchase2["basket"]["total_price"] == 0.99
        purchase2 = purchase2['basket']['basket']
        product2 = purchase2[0]['product']
        assert product2['store_name'] == 'store1'
        assert product2['name'] == 'tuna'

    except AcceptanceTestError as e:
        pytest.fail(str(e))
    finally:
        bridge.logout(user_id, "root_user")


# 6.4_3_2 Fail store does not exists:
def test_6_4_3_2():
    user_id = bridge.login("user1", "passworD134%")
    try:
        with pytest.raises(AcceptanceTestError):
            purchase_list_found = bridge.view_as_admin_user_purchases(user_id, "avibbibibibi2")
    finally:
        bridge.logout(user_id, "root_user")


# SUCCESS -> buying 3 getting one for free
def test_10_0_0_0():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "10_0_0_0_0")
    user_id = bridge.login(store_owner, owner_password)
    bridge.add_item_to_store(user_id, store_name, "tuna", "food", "", 1.0, 100)
    user_id_2 = bridge.login(example_username_2, example_password)
    bridge.add_item_to_cart(user_id_2, store_name, "tuna", 4)
    res = bridge.purchase(user_id_2, cc_good, purchase_info_data[1]).data
    assert res["purchases"][0]["basket"]["total_price"] == 4.0
    product_name = "tuna"
    discount_type = "2"
    percent = ""
    category = ""
    free_per_x = "1/3"
    overall_product_price = ""
    overall_category_price = ""
    overall_product_quantity = ""
    overall_category_quantity = ""
    up_to_date = "14/06/2021"
    basket_size = ""
    discount_id = bridge.add_discount(user_id, store_name, product_name, discount_type, percent, category, free_per_x,
                                      overall_product_price, overall_category_price, overall_product_quantity,
                                      overall_category_quantity,
                                      up_to_date, basket_size)

    bridge.add_item_to_cart(user_id_2, store_name, "tuna", 4)
    res = bridge.purchase(user_id_2, cc_good, purchase_info_data[1]).data
    assert res["purchases"][0]["basket"]["total_price"] == 3.0


# SUCCESS -> buying 1 tuna without basket policy, then adding policy of 2 , trying to buy again and fail, trying to buy again with two and succeed
def test_10_0_1_0():
    user_id = -1
    store_name, store_owner, owner_password = bridge.setup_anonymous_store(user_id, "10_0_0_1_0")
    user_id = bridge.login(store_owner, owner_password)
    bridge.add_item_to_store(user_id, store_name, "tuna", "food", "", 1.0, 100)
    user_id_2 = bridge.login(example_username_2, example_password)
    bridge.add_item_to_cart(user_id_2, store_name, "tuna", 1)
    res = bridge.purchase(user_id_2, cc_good, purchase_info_data[1])
    if not res.succeed:
        pytest.fail(str(res.msg))
    min_basket_quantity = 2
    max_basket_quantity = 100
    policy = bridge.add_policy(user_id, store_name, min_basket_quantity, max_basket_quantity, "", "", "", "", "",
                               "", "")

    bridge.add_item_to_cart(user_id_2, store_name, "tuna", 1)
    try:
        res = bridge.purchase(user_id_2, cc_good, purchase_info_data[1])
    except AcceptanceTestError as e:
        pass
    bridge.add_item_to_cart(user_id_2, store_name, "tuna", 1)
    res = bridge.purchase(user_id_2, cc_good, purchase_info_data[1])
    if not res.succeed:
        pytest.fail(str("should succeed"))


##HELPER FUNCTIONS


def purchases_are_equal(purch_test, purch_sys):
    return all(
        [purch_test["user_id"] == purch_sys["user_id"],
         # purch_test["details"]["price"] == purch_sys["price"],
         purch_test["details"]["store_name"] == purch_sys['basket']['store'],
         purch_test["details"]["quantity"] == purch_sys['basket']['basket'][0]['product']["quantity"],
         purch_test["details"]["item_name"] == purch_sys['basket']['basket'][0]['product']['product']['name'],
         purch_sys["purchase_type"] == "Immediate"]
    )


def items_are_equal(test_item, sys_item):
    a1 = test_item["item_name"]
    a2 = sys_item["product"]["name"]
    b1 = test_item["category"]
    b2 = sys_item["product"]["categories"][0]
    c1 = test_item["brand"]
    c2 = sys_item["product"]["brand"]
    d1 = test_item["price"]
    d2 = sys_item["after_discount"]
    e1 = test_item["quantity"]
    e2 = sys_item["quantity"]
    return all(
        [
            a1 == a2,
            b1 == b2,
            c1 == c2,
            d1 == d2,
            e1 == e2,
        ]
    )


def viewable_items_equal(viewable_test_item, viewable_sys_item):
    return all(
        [
            viewable_test_item["store"] == viewable_sys_item["store_name"],
            items_are_equal(viewable_test_item["details"], viewable_sys_item["product"])
        ]
    )


def stores_are_equal(test_store, sys_store):
    a1 = test_store["store_name"]
    a2 = sys_store["name"]
    b1 = test_store["owner"]
    b2 = sys_store["initial_owner"]
    # c = lists_are_equal(test_store["inventory"], sys_store["inventory"], items_are_equal)
    return all(
        [
            a1 == a2,
            b1 == b2,
        ]
    )


def list_contains(item, list, comparison_func):
    for x in list:
        if comparison_func(item, x):
            return True
    return False


def lists_are_equal(lst1, lst2, comparison_func):
    # ls1 subset lst2
    if len(lst1) == len(lst2) == 0:
        return True
    for ls1 in lst1:
        if not list_contains(ls1, lst2, comparison_func):
            return False
    return len(lst1) == len(lst2)


def get_item_from_inventory(store_name, item_name):
    items = data_obj.set_up_shopping_data["Inventory"]
    for item in items:
        if item["store_name"] == store_name and item["item_name"] == item_name:
            return item


def get_store_from_data(store_name):
    stores = data_obj.set_up_shopping_data["Stores"]
    s_inventory = list(filter(lambda x: x["store_name"] == store_name, data_obj.set_up_shopping_data["Inventory"]))
    for store in stores:
        if store["store_name"] == store_name:
            return {"store_name": store["store_name"], "owner": store["owner"], "inventory": s_inventory}


def row_to_criteria(row):
    item_name = row[0]
    store_names = None if row[1] == "" else ast.literal_eval(row[1])
    categories = None if row[2] == "" else ast.literal_eval(row[2])
    brands = None if row[3] == "" else ast.literal_eval(row[3])
    min_price = None if row[4] == "" else float(row[4])
    max_price = None if row[5] == "" else float(row[5])
    return [item_name, store_names, categories, brands, min_price, max_price]
