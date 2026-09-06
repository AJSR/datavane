from datavane.models import FieldInfo


def test_field_info_initial_state():
    field = FieldInfo(name="age")

    assert field.name == "age"
    assert field.types == set()
    assert field.example is None
    assert field.appearances == 0
    assert field.null_count == 0
    assert field.context_count == 0

def test_update_value():
    field = FieldInfo(name="age")

    field.update(25, "int")

    assert field.types == {"int"}
    assert field.appearances == 1
    assert field.null_count == 0
    assert field.example == 25

def test_update_none():
    field = FieldInfo(name="nickname")

    field.update(None, "null")

    assert field.types == {"null"}
    assert field.appearances == 1
    assert field.null_count == 1
    assert field.example is None

def test_update_keeps_first_example():
    field = FieldInfo(name="age")

    field.update(25, "int")
    field.update(30, "int")

    assert field.types == {"int"}
    assert field.appearances == 2
    assert field.null_count == 0
    assert field.example == 25

def test_update_uses_first_non_null_example():
    field = FieldInfo(name="nickname")

    field.update(None, "null")
    field.update("Tony", "str")
    field.update("Juan", "str")

    assert field.types == {"null", "str"}
    assert field.appearances == 3
    assert field.null_count == 1
    assert field.example == "Tony"

def test_update_collects_types():
    field = FieldInfo(name="age")

    field.update(10, "int")
    field.update("10", "str")
    field.update(10.5, "float")

    assert field.types == {"float", "int", "str"}
    assert field.appearances == 3
    assert field.null_count == 0

