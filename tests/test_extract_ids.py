import pytest

from utils.extract_ids import extract_ids, get_all_ids, get_unique_ids


def test_extract_ids_basic():
    data = {
        "a": {"id": 1, "nested": {"id": 2}},
        "items": [{"id": "x"}, {"id": "y", "other": {"id": "z"}}],
    }

    pairs = extract_ids(data)
    # convert to dict for easier assertions (path -> value)
    d = {p: v for p, v in pairs}

    assert d["a.id"] == 1
    assert d["a.nested.id"] == 2
    assert d["items.[0].id"] == "x"
    assert d["items.[1].other.id"] == "z"


def test_get_all_and_unique():
    data = {"list": [{"id": 1}, {"id": 1}, {"id": 2}], "id": 3}
    all_ids = get_all_ids(data)
    assert all_ids == [1, 1, 2, 3]

    uniques = get_unique_ids(data)
    assert uniques == [1, 2, 3]
