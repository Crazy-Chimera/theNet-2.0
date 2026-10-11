from dataclasses import FrozenInstanceError

import pytest

from thenet_core import create_genesis


BASE = ("theNet-2.0", "2026-10-11T00:00:00Z")


def test_genesis_has_stable_sha256_identity():
    item = create_genesis(*BASE)
    assert item.origin_id == BASE[0]
    assert item.created_at == BASE[1]
    assert item.version == 1
    assert len(item.id) == 64
    assert create_genesis(*BASE) == item


@pytest.mark.parametrize("index", range(2))
def test_genesis_rejects_blank_required_fields(index):
    values = list(BASE)
    values[index] = "   "
    with pytest.raises(ValueError):
        create_genesis(*values)


def test_genesis_rejects_non_string_fields():
    with pytest.raises(ValueError):
        create_genesis(None, BASE[1])


def test_genesis_is_immutable():
    item = create_genesis(*BASE)
    with pytest.raises(FrozenInstanceError):
        item.origin_id = "mutated"


def test_origin_or_timestamp_changes_identity():
    assert create_genesis("origin-a", BASE[1]).id != create_genesis("origin-b", BASE[1]).id
    assert create_genesis(BASE[0], BASE[1]).id != create_genesis(BASE[0], "2026-10-12T00:00:00Z").id
