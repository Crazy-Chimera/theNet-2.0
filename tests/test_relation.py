from dataclasses import FrozenInstanceError

import pytest

from thenet_core import create_relation


STAMP = "2026-10-11T00:00:00Z"
BASE = ("agent:a", "agent:b", "trust", STAMP)


def test_relation_is_directed_and_versioned():
    relation = create_relation(*BASE)
    assert relation.source_id == "agent:a"
    assert relation.target_id == "agent:b"
    assert relation.kind == "trust"
    assert relation.version == 1
    assert len(relation.id) == 64
    assert relation == create_relation(*BASE)
    assert relation.id != create_relation("agent:b", "agent:a", "trust", STAMP).id


@pytest.mark.parametrize("index", range(4))
def test_relation_rejects_blank_required_fields(index):
    values = list(BASE)
    values[index] = " "
    with pytest.raises(ValueError):
        create_relation(*values)


def test_relation_rejects_non_string_field():
    with pytest.raises(ValueError):
        create_relation("agent:a", None, "trust", STAMP)


def test_relation_kind_is_part_of_identity():
    assert create_relation(*BASE).id != create_relation("agent:a", "agent:b", "observation", STAMP).id


def test_relation_is_immutable():
    item = create_relation(*BASE)
    with pytest.raises(FrozenInstanceError):
        item.kind = "other"
