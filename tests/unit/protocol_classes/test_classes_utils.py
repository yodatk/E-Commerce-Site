import pytest
from src.protocol_classes.classes_utils import TypedList, TypedDict, TypeChecker, Result


def test_typed_list():
    # type check
    lst = TypedList(str)
    with pytest.raises(TypeError):
        lst.append(5)
    lst.append("5")
    assert "5" in lst
    assert 5 not in lst
    assert lst.check_types(str)
    assert not lst.check_types(TypedList)
    # type check with initial list
    with pytest.raises(TypeError):
        lst = TypedList(str, ['1', '2', 5])

    lst = TypedList(str, ['1', '2', '3'])
    # test check_types
    assert lst.check_types(str)
    assert not lst.check_types(int)

    # testing filtering empty string
    assert len(lst) == 3
    assert all(i in lst for i in ['1', '2', '3'])
    lst.append("  ")
    lst.append("")
    lst = lst.filtering_empty_str()
    assert len(lst) == 3
    assert all(i in lst for i in ['1', '2', '3'])
    lst = lst.filtering_empty_str()
    assert len(lst) == 3
    assert all(i in lst for i in ['1', '2', '3'])
    # testing copy
    new_lst: TypedList = lst.copy()
    assert len(new_lst) == 3
    assert all(i in new_lst for i in ['1', '2', '3'])
    assert all(i in ['1', '2', '3'] for i in new_lst)


def test_typed_dict():
    dic = TypedDict(str, int)
    assert dic.check_types(str, int)
    assert not dic.check_types(int, str)
    assert not dic.check_types(TypedDict, int)
    with pytest.raises(TypeError):
        dic[5] = 'hey'
    with pytest.raises(TypeError):
        dic['5'] = 'hey'
    with pytest.raises(TypeError):
        dic['5'] = TypedList(int)
    dic['5'] = 5
    assert '5' in dic.keys()
    assert 5 in dic.values()
    dic = TypedDict(str, int, {'a': 1, 'b': 2, 'c': 3})
    checks_equal_dictionaries(dic, {'a': 1, 'b': 2, 'c': 3})

    # check type
    assert dic.check_types(str, int)
    assert not dic.check_types(str, str)
    assert not dic.check_types(int, str)
    assert not dic.check_types(int, int)
    # copy
    new_dic = dic.copy()
    checks_equal_dictionaries(new_dic, {'a': 1, 'b': 2, 'c': 3})


@pytest.mark.parametrize("succeed,requesting_id,msg",
                         [(1, 1, "1"), (True, "1", "1"),
                          (True, 1, 1)])
def test_result_types_fail(succeed, requesting_id, msg):
    with pytest.raises(TypeError):
        Result(succeed, requesting_id, msg)


@pytest.mark.parametrize("succeed,requesting_id,msg,data",
                         [(False, 1, "hey", None), (True, -1, "1", False),
                          (True, 1, '2', {"hey": "you"})])
def test_result_type_success(succeed, requesting_id, msg, data):
    Result(succeed, requesting_id, msg, data)


def checks_equal_dictionaries(dic, to_compare_to):
    assert len(dic) == 3
    assert all(k in dic.keys() for k in to_compare_to.keys())
    assert all(v in dic.values() for v in to_compare_to.values())


@pytest.mark.parametrize("test_input,output",
                         [(['1', '2', '3'], True), ([], True), ([' '], False), (['1', '  ', '2'], False),
                          ([None, '1'], False)])
def test_type_checker_check_for_non_empty_strings(test_input, output):
    assert TypeChecker.check_for_non_empty_strings(test_input) == output


@pytest.mark.parametrize("test_input,output",
                         [([1, 2, 3], True), ([0], True), ([], True), ([1.1, 1], True), ([-1], False),
                          ([1, None], False), ([-1.2], False)])
def test_type_checker_check_for_positive_number(test_input, output):
    assert TypeChecker.check_for_positive_number(test_input) == output


@pytest.mark.parametrize("test_input,output",
                         [([True], True), ([], True), ([True, False], True), ([True, None], False), ([None], False)])
def test_type_checker_check_for_list_of_bool(test_input, output):
    assert TypeChecker.check_for_list_of_bool(test_input) == output
