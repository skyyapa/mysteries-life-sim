"""非凡系统：途径（克制版）、灵性、序列。"""

from .pathways import PATHWAYS, apply_pathway_bonus, pathway_behavior_bonus
from .sequences import (
    SEQUENCES,
    can_consume,
    consume_potion,
    next_sequence,
    seq_name,
)

__all__ = [
    "PATHWAYS",
    "apply_pathway_bonus",
    "pathway_behavior_bonus",
    "SEQUENCES",
    "can_consume",
    "consume_potion",
    "next_sequence",
    "seq_name",
]