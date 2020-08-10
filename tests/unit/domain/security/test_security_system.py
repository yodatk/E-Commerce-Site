import pytest

# hash_password
from src.security.security_system import Encrypter


@pytest.mark.parametrize("password_to_hash, output", [("password", True)])
def test_hash_password(password_to_hash, output):
    hash_1 = Encrypter.hash_password(password_to_hash)
    assert Encrypter.verify_password(password_to_hash, hash_1) == output, "test failed"


@pytest.mark.parametrize("password_to_hash_1, password_to_hash_2, output", [("password", "password", False)])
def test_hash_password_same_password_different_encrypt(password_to_hash_1, password_to_hash_2, output):
    hash_1 = Encrypter.hash_password(password_to_hash_1)
    hash_2 = Encrypter.hash_password(password_to_hash_2)
    assert (hash_1 == hash_2) == output, "test failed"


# verify password
@pytest.mark.parametrize("password_to_hash_1, password_to_hash_2, output", [("password", "password", True),
                                                                            ("password", "pass", False)])
def test_verify_password(password_to_hash_1, password_to_hash_2, output):
    hash_1 = Encrypter.hash_password(password_to_hash_1)
    assert Encrypter.verify_password(password_to_hash_2, hash_1) == output, "test failed"


# password_check
@pytest.mark.parametrize("password, is_pass_ok, upper_case, lower_case", [("12345678", False, True, True)])
def test_password_check_only_numbers(password, is_pass_ok, upper_case, lower_case):
    dict_pass = Encrypter.password_check(password)
    assert dict_pass['password_ok'] == is_pass_ok and dict_pass['lowercase_error'] == lower_case \
           and dict_pass['uppercase_error'] == upper_case, "test failed"


@pytest.mark.parametrize("password, is_pass_ok, length_case", [("12345678", False, False), ("1678", False, True)])
def test_password_check_length(password, is_pass_ok, length_case):
    dict_pass = Encrypter.password_check(password)
    assert dict_pass['password_ok'] == is_pass_ok and dict_pass['length_error'] == length_case, "test failed"


@pytest.mark.parametrize("password, is_pass_ok, upper_case, lower_case",
                         [("dsjskcmks", False, True, False), ("dsjsADFmkJs", False, False, False),
                          ("ADMLMGFL", False, False, True)])
def test_password_check_only_letters(password, is_pass_ok, upper_case, lower_case):
    dict_pass = Encrypter.password_check(password)
    assert dict_pass['password_ok'] == is_pass_ok and dict_pass['lowercase_error'] == lower_case \
           and dict_pass['uppercase_error'] == upper_case, "test failed"


@pytest.mark.parametrize("password, is_pass_ok, symbol_case", [("!,fldms", False, False), ("dfkldsm", False, True)])
def test_password_no_symbol(password, is_pass_ok, symbol_case):
    dict_pass = Encrypter.password_check(password)
    assert dict_pass['password_ok'] == is_pass_ok and dict_pass['symbol_error'] == symbol_case, "test failed"


@pytest.mark.parametrize("password, is_pass_ok", [("!,fldmAd12s", True), ("dfkldsm", False)])
def test_password_correct(password, is_pass_ok):
    dict_pass = Encrypter.password_check(password)
    assert dict_pass['password_ok'] == is_pass_ok, "test failed"
