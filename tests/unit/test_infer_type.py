import pytest

from datavane.inference import infer_type


@pytest.mark.parametrize(
    ("value, expected"),
    [
        pytest.param(None, "null", id="none"),
        pytest.param(10, "int", id="integer"),
        pytest.param(3.14, "float", id="float"),
        pytest.param("hello", "str", id="string"),
       pytest.param({"id": 1, "name": "Antonio"}, "dict", id="dictionary"),
        pytest.param(True, "bool", id="boolean")
    ],
)
def test_infer_type(value, expected):
    assert infer_type(value) == expected

@pytest.mark.parametrize(
    ("value", "expected"),
    [
        pytest.param([], "list", id="empty list"),
        pytest.param([1, 2, 3], "list[int]", id="list of integers"),
        pytest.param(["a", "b", "c"], "list[str]", id="list of strings"),
        pytest.param([1, "a"], "list[int, str]", id="list of integers and strings")
    ],
)
def test_infer_type_list(value, expected):
    assert infer_type(value) == expected
