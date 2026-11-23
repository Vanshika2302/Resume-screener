import pytest
from screener import parse_json


def test_plain_json():
    assert parse_json('{"a": 1}') == {"a": 1}


def test_fenced_json():
    assert parse_json('```json\n{"name": "Asha"}\n```') == {"name": "Asha"}


def test_text_around_json():
    assert parse_json('Here you go: {"x": 2} hope it helps')["x"] == 2


def test_no_json_raises():
    with pytest.raises(ValueError):
        parse_json("sorry, no data")
