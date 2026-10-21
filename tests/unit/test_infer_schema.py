import json
from pathlib import Path

from datavane.inference.schema import infer_schema
from datavane.models import InferredStructure, InferredType

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_fixture(filename: str):
    path = FIXTURES_DIR / filename

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def test_infer_schema_single_record():
    data = [{"id": 1, "name": "Tony"}]

    result = infer_schema(data)

    assert set(result) == {"id", "name"}

    assert result["id"].types == {InferredType.INT}
    assert result["id"].appearances == 1
    assert result["id"].null_count == 0
    assert result["id"].example == 1

    assert result["name"].types == {InferredType.STR}
    assert result["name"].appearances == 1
    assert result["name"].null_count == 0
    assert result["name"].example == "Tony"


def test_infer_schema_multiple_records():
    data = [
        {
            "id": 1,
            "name": "Tony",
        },
        {
            "id": 2,
            "name": "Juan",
        },
        {
            "id": 3,
            "name": "Pedro",
        },
    ]

    result = infer_schema(data)

    assert result["id"].types == {InferredType.INT}
    assert result["id"].appearances == 3
    assert result["id"].null_count == 0
    assert result["id"].example == 1

    assert result["name"].types == {InferredType.STR}
    assert result["name"].appearances == 3
    assert result["name"].null_count == 0
    assert result["name"].example == "Tony"


def test_infer_schema_optional_field():
    data = [
        {
            "id": 1,
            "name": "Tony",
        },
        {
            "id": 2,
        },
        {
            "id": 3,
            "name": "Tony",
        },
    ]

    result = infer_schema(data)

    assert result["id"].types == {InferredType.INT}
    assert result["id"].appearances == 3
    assert result["id"].null_count == 0
    assert result["id"].example == 1

    assert result["name"].types == {InferredType.STR}
    assert result["name"].appearances == 2
    assert result["name"].null_count == 0
    assert result["name"].example == "Tony"


def test_infer_schema_null_field():
    data = [
        {
            "id": 1,
            "name": "Tony",
        },
        {
            "id": 2,
            "name": None,
        },
        {
            "id": 3,
            "name": "Tony",
        },
    ]

    result = infer_schema(data)

    assert result["id"].types == {InferredType.INT}
    assert result["id"].appearances == 3
    assert result["id"].null_count == 0
    assert result["id"].example == 1

    assert result["name"].types == {InferredType.STR}
    assert result["name"].appearances == 3
    assert result["name"].null_count == 1
    assert result["name"].example == "Tony"


def test_infer_schema_nested():
    data = [
        {
            "id": 1,
            "country": {
                "id": 34,
                "name": "Spain",
            },
        }
    ]

    result = infer_schema(data)

    assert result["country"].structures == {InferredStructure.OBJECT}
    assert result["country"].appearances == 1

    assert result["country.id"].types == {InferredType.INT}
    assert result["country.id"].appearances == 1
    assert result["country.id"].example == 34

    assert result["country.name"].types == {InferredType.STR}
    assert result["country.name"].appearances == 1
    assert result["country.name"].example == "Spain"


def test_infer_schema_lost_of_dicts():
    data = [
        {
            "lineup": [
                {
                    "player_id": 10,
                    "player_name": "Player 1",
                },
                {
                    "player_id": 20,
                    "player_name": "Player 2",
                },
            ]
        }
    ]

    result = infer_schema(data)

    assert set(result) == {"lineup", "lineup[].player_id", "lineup[].player_name"}

    assert result["lineup"].structures == {InferredStructure.ARRAY}
    assert result["lineup"].appearances == 1

    assert result["lineup[].player_id"].types == {InferredType.INT}
    assert result["lineup[].player_id"].appearances == 2
    assert result["lineup[].player_id"].example == 10

    assert result["lineup[].player_name"].types == {InferredType.STR}
    assert result["lineup[].player_name"].appearances == 2
    assert result["lineup[].player_name"].example == "Player 1"


def test_infer_schema_empty_list():
    data = [{"cards": []}]

    result = infer_schema(data)

    assert set(result) == {"cards"}

    assert result["cards"].structures == {InferredStructure.ARRAY}
    assert result["cards"].appearances == 1


def test_infer_schema_multiple_nested_dict_multiple_records():
    data = [
        {
            "country": {
                "id": 34,
                "name": "Spain",
            }
        },
        {
            "country": {
                "id": 33,
                "name": "France",
            }
        },
    ]

    result = infer_schema(data)

    assert result["country"].appearances == 2

    assert result["country.id"].appearances == 2
    assert result["country.id"].example == 34

    assert result["country.name"].appearances == 2
    assert result["country.name"].example == "Spain"


def test_infer_schema_nested_list_with_null():
    data = [
        {
            "lineup": [
                {
                    "player_id": 1,
                    "player_nickname": "Player 1",
                },
                {
                    "player_id": 2,
                    "player_nickname": None,
                },
                {
                    "player_id": 3,
                    "player_nickname": "Player 3",
                },
            ]
        }
    ]

    result = infer_schema(data)

    nickname = result["lineup[].player_nickname"]

    assert nickname.types == {InferredType.STR}
    assert nickname.appearances == 3
    assert nickname.null_count == 1
    assert nickname.example == "Player 1"


def test_infer_schema_missing_field_in_list():
    data = [
        {
            "lineup": [
                {
                    "player_id": 1,
                    "nickname": "Player 1",
                },
                {
                    "player_id": 2,
                },
                {
                    "player_id": 3,
                    "nickname": "Player 3",
                },
            ]
        }
    ]

    result = infer_schema(data)

    nickname = result["lineup[].nickname"]

    assert nickname.types == {InferredType.STR}
    assert nickname.appearances == 2
    assert nickname.null_count == 0
    assert nickname.example == "Player 1"


def test_infer_schema_deeply_nested():
    data = [
        {
            "players": [
                {
                    "id": 1,
                    "country": {
                        "id": 34,
                        "name": "Spain",
                    },
                },
                {
                    "id": 2,
                    "country": {
                        "id": 33,
                        "name": "France",
                    },
                },
            ]
        }
    ]

    result = infer_schema(data)

    assert result["players"].structures == {InferredStructure.ARRAY}
    assert result["players"].appearances == 1

    assert result["players[].id"].appearances == 2

    assert result["players[].country"].structures == {InferredStructure.OBJECT}
    assert result["players[].country"].appearances == 2

    assert result["players[].country.id"].appearances == 2
    assert result["players[].country.id"].example == 34

    assert result["players[].country.name"].appearances == 2
    assert result["players[].country.name"].example == "Spain"


def test_infer_schema_nested_complex_structure():
    data = [
        {
            "order_id": 1001,
            "customer": {
                "id": 42,
                "name": "Alice",
            },
            "items": [
                {
                    "product_id": 10,
                    "product_name": "Keyboard",
                    "tags": [
                        {"name": "electronics"},
                    ],
                },
                {
                    "product_id": 20,
                    "product_name": "Mouse",
                    "tags": [],
                },
            ],
        },
        {
            "order_id": 1002,
            "customer": {
                "id": 84,
                "name": "Bob",
            },
            "items": [
                {
                    "product_id": 30,
                    "product_name": "Monitor",
                    "tags": [
                        {"name": "electronics"},
                        {"name": "display"},
                    ],
                },
            ],
        },
    ]

    result = infer_schema(data)

    assert "order_id" in result
    assert "customer" in result
    assert "customer.id" in result
    assert "customer.name" in result
    assert "items" in result
    assert "items[].product_id" in result
    assert "items[].product_name" in result
    assert "items[].tags" in result
    assert "items[].tags[].name" in result

    assert result["order_id"].appearances == 2
    assert result["order_id"].types == {InferredType.INT}

    assert result["customer"].appearances == 2
    assert result["customer.id"].appearances == 2
    assert result["customer.id"].types == {InferredType.INT}
    assert result["customer.id"].example == 42

    assert result["customer.name"].appearances == 2
    assert result["customer.name"].types == {InferredType.STR}
    assert result["customer.name"].example == "Alice"

    assert result["items"].appearances == 2

    assert result["items[].product_id"].appearances == 3
    assert result["items[].product_id"].types == {InferredType.INT}
    assert result["items[].product_id"].example == 10

    assert result["items[].product_name"].appearances == 3
    assert result["items[].product_name"].types == {InferredType.STR}
    assert result["items[].product_name"].example == "Keyboard"

    assert result["items[].tags"].appearances == 3

    assert result["items[].tags[].name"].appearances == 3
    assert result["items[].tags[].name"].types == {InferredType.STR}
    assert result["items[].tags[].name"].example == "electronics"


def test_context_count_for_optional_field():
    data = [
        {"name": "Tony", "age": 25},
        {"name": "Juan"},
        {"name": "Pedro", "age": 30},
    ]

    fields = infer_schema(data)

    print(fields["name"])
    print(fields["age"])

    assert fields["name"].appearances == 3
    assert fields["name"].context_count == 3

    assert fields["age"].appearances == 2
    assert fields["age"].context_count == 3


def test_infer_schema_detects_object_structure():
    data = [
        {
            "customer": {
                "id": 1,
                "name": "Alice",
            }
        }
    ]

    result = infer_schema(data)

    assert result["customer"].structures == {InferredStructure.OBJECT}
    assert result["customer"].structural_candidates == {
        InferredStructure.OBJECT: {"native"}
    }


def test_infer_schema_detects_array_structure():
    data = [
        {
            "items": [
                {"id": 1},
                {"id": 2},
            ]
        }
    ]

    result = infer_schema(data)

    assert result["items"].structures == {InferredStructure.ARRAY}
    assert result["items"].structural_candidates == {
        InferredStructure.ARRAY: {"native"}
    }


def test_infer_schema_detects_empty_array_structure():
    data = [
        {
            "items": [],
        }
    ]

    result = infer_schema(data)

    assert result["items"].structures == {InferredStructure.ARRAY}
    assert result["items"].structural_candidates == {
        InferredStructure.ARRAY: {"native"}
    }


def test_infer_schema_detects_nested_structures():
    data = [
        {
            "customer": {
                "id": 1,
                "addresses": [
                    {
                        "city": "Madrid",
                    }
                ],
            }
        }
    ]

    result = infer_schema(data)

    assert result["customer"].structures == {InferredStructure.OBJECT}

    assert result["customer.addresses"].structures == {InferredStructure.ARRAY}

    assert result["customer.addresses[].city"].types == {InferredType.STR}


def test_infer_schema_nested_list_context_count():
    data = [
        {
            "items": [
                {"id": 1},
                {"id": 2},
            ]
        },
        {
            "items": [
                {"id": 3},
            ]
        },
    ]

    result = infer_schema(data)

    assert result["items"].appearances == 2
    assert result["items"].context_count == 2

    assert result["items[].id"].appearances == 3
    assert result["items[].id"].context_count == 3


def test_infer_schema_nested_list_context_count_with_missing_field():
    data = [
        {
            "items": [
                {"id": 1},
                {"name": "Mouse"},
                {"id": 3},
            ]
        }
    ]

    result = infer_schema(data)

    assert result["items[].id"].appearances == 2
    assert result["items[].id"].context_count == 3


def test_infer_schema_deeply_nested_context_count():
    data = [
        {
            "orders": [
                {
                    "customer": {
                        "id": 1,
                    }
                },
                {
                    "customer": {
                        "id": 2,
                    }
                },
            ]
        }
    ]

    result = infer_schema(data)

    assert result["orders"].appearances == 1
    assert result["orders"].context_count == 1

    assert result["orders[].customer"].appearances == 2
    assert result["orders[].customer"].context_count == 2

    assert result["orders[].customer.id"].appearances == 2
    assert result["orders[].customer.id"].context_count == 2
