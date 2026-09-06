import json
from pathlib import Path

from datavane.inference import infer_schema

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"

def load_fixture(filename: str):
    path = FIXTURES_DIR / filename

    with open(path, encoding="utf-8") as f:
        return json.load(f)

def test_infer_schema_single_record():
    data = [
        {
            "id": 1,
            "name": "Tony"
        }
    ]

    result = infer_schema(data)

    assert set(result) == {"id", "name"}

    assert result["id"].types == {"int"}
    assert result["id"].appearances == 1
    assert result["id"].null_count == 0
    assert result["id"].example == 1

    assert result["name"].types == {"str"}
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

    assert result["id"].types == {"int"}
    assert result["id"].appearances == 3
    assert result["id"].null_count == 0
    assert result["id"].example == 1

    assert result["name"].types == {"str"}
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

    assert result["id"].types == {"int"}
    assert result["id"].appearances == 3
    assert result["id"].null_count == 0
    assert result["id"].example == 1
    
    assert result["name"].types == {"str"}
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

    assert result["id"].types == {"int"}
    assert result["id"].appearances == 3
    assert result["id"].null_count == 0
    assert result["id"].example == 1
        
    assert result["name"].types == {"null", "str"}
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

    assert result["country"].types == {"dict"}
    assert result["country"].appearances == 1

    assert result["country.id"].types == {"int"}
    assert result["country.id"].appearances == 1
    assert result["country.id"].example == 34

    assert result["country.name"].types == {"str"}
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

    assert set(result) == {
        "lineup",
        "lineup[].player_id",
        "lineup[].player_name"
    }

    assert result["lineup"].types == {"list[dict]"}
    assert result["lineup"].appearances == 1

    assert result["lineup[].player_id"].types == {"int"}
    assert result["lineup[].player_id"].appearances == 2
    assert result["lineup[].player_id"].example == 10

    assert result["lineup[].player_name"].types == {"str"}
    assert result["lineup[].player_name"].appearances == 2
    assert result["lineup[].player_name"].example == "Player 1"

def test_infer_schema_empty_list():
    data = [
        {
            "cards": []
        }
    ]

    result = infer_schema(data)

    assert set(result) == {"cards"}

    assert result["cards"].types == {"list"}
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

    assert nickname.types == {"null", "str"}
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

    assert nickname.types == {"str"}
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
                    }
                },
                {
                    "id": 2,
                    "country": {
                        "id": 33,
                        "name": "France",
                    }
                },
            ]
        }
    ]

    result = infer_schema(data)

    assert result["players"].types == {"list[dict]"}
    assert result["players"].appearances == 1

    assert result["players[].id"].appearances == 2

    assert result["players[].country"].types == {"dict"}
    assert result["players[].country"].appearances == 2

    assert result["players[].country.id"].appearances == 2
    assert result["players[].country.id"].example == 34

    assert result["players[].country.name"].appearances == 2
    assert result["players[].country.name"].example == "Spain"

def test_infer_schema_statsbomb_lineup():
    data = load_fixture("lineup_sample.json")

    result = infer_schema(data)

    assert "team_id" in result
    assert "team_name" in result
    assert "lineup" in result
    assert "lineup[].player_id" in result
    assert "lineup[].player_name" in result
    assert "lineup[].player_nickname" in result
    assert "lineup[].country" in result
    assert "lineup[].country.id" in result
    assert "lineup[].country.name" in result
    assert "lineup[].cards" in result
    assert "lineup[].cards[].card_type" in result
    assert "lineup[].positions" in result
    assert "lineup[].positions[].position" in result

    assert result["lineup"].appearances == 1

    assert result["lineup[].player_id"].appearances == 3
    assert result["lineup[].player_id"].types == {"int"}

    assert result["lineup[].player_nickname"].appearances == 3
    assert result["lineup[].player_nickname"].null_count == 2
    assert result["lineup[].player_nickname"].types == {"null", "str"}

    assert result["lineup[].country"].appearances == 3
    assert result["lineup[].country"].types == {"dict"}

    assert result["lineup[].country.id"].appearances == 3
    assert result["lineup[].country.id"].types == {"int"}

    assert result["lineup[].cards"].appearances == 3
    assert result["lineup[].cards[].card_type"].appearances == 1

    assert result["lineup[].positions"].appearances == 3
    assert result["lineup[].positions[].position"].appearances == 3

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
