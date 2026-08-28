"""NPC 子系统：状态、需求、日程、行为、效果、互动。"""

from .behavior import BehaviorCandidate, decide_behavior
from .effects import NPCActionResult, apply_result, build_result
from .interaction import NPCSocialInteraction, interact, scan_and_interact
from .models import NPCNeeds, NPCRelationship, NPCState, migrate_relationship

__all__ = [
    "NPCState",
    "NPCNeeds",
    "NPCRelationship",
    "migrate_relationship",
    "BehaviorCandidate",
    "decide_behavior",
    "NPCActionResult",
    "build_result",
    "apply_result",
    "NPCSocialInteraction",
    "interact",
    "scan_and_interact",
]