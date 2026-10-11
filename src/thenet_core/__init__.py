"""Core domain primitives for theNet-2.0."""

from .agent_state import AgentState, create_agent_state
from .genesis import Genesis, create_genesis
from .relation import Relation, create_relation
from .structure import Structure, create_structure

__all__ = [
    "AgentState",
    "Genesis",
    "Relation",
    "Structure",
    "create_agent_state",
    "create_genesis",
    "create_relation",
    "create_structure",
]
