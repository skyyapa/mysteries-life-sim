"""NPC 行为结果与效果层（V0.15.3）。

规格：NPC 行为 → NPCActionResult → Effects → 世界状态。
核心是"可调试"：能回答"汤姆为什么多了 £2.5？他为什么在酒馆？"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import NPCNeeds, NPCState
from .needs import ACTIVITY_EFFECTS


@dataclass
class NPCActionResult:
    """一次行为的完整结果（行为 → 位置 → 状态/需求/金钱/地点影响 → 事件）。"""

    npc_id: str
    action: str
    from_location: str | None = None
    to_location: str | None = None
    money_delta: float = 0.0
    fatigue_delta: int = 0
    needs_delta: dict[str, int] = field(default_factory=dict)
    location_activity_delta: int = 0
    emitted_events: list[str] = field(default_factory=list)

    def __repr__(self) -> str:
        return (
            f"{self.npc_id}:{self.action} "
            f"{self.from_location}->{self.to_location} "
            f"£{self.money_delta:+.1f} 疲{self.fatigue_delta:+d} "
            f"{self.emitted_events}"
        )


def resolve_location(npc: Any, action: str, loc_map: dict[str, str]) -> str | None:
    """根据行为决定目标位置（home/workplace/地点类型）。"""
    loc_type = loc_map.get(action)
    if loc_type == "home":
        return npc.home
    if loc_type == "workplace":
        return npc.job_location or npc.home
    return None  # 由调用方用类型映射兜底


def build_result(
    npc: Any,
    action: str,
    *,
    prev_location: str | None,
    hours: float = 1.0,
    loc_type_map: dict[str, str] | None = None,
    loc_name_map: dict[str, str] | None = None,
) -> NPCActionResult:
    """生成一次行为的结果（不直接改世界，供 EffectSystem 消费）。"""
    loc_type_map = loc_type_map or {}
    loc_name_map = loc_name_map or {}

    to_loc = resolve_location(npc, action, loc_type_map)
    if to_loc is None:
        loc_type = loc_type_map.get(action)
        to_loc = loc_name_map.get(loc_type) if loc_type else None

    result = NPCActionResult(
        npc_id=npc.id,
        action=action,
        from_location=prev_location,
        to_location=to_loc or npc.location,
    )

    effect = ACTIVITY_EFFECTS.get(action)
    if effect:
        for key, delta in effect.get("needs", {}).items():
            result.needs_delta[key] = round(delta * hours)
        for key, delta in effect.get("state", {}).items():
            if key == "money":
                result.money_delta = delta * hours
            elif key == "fatigue":
                result.fatigue_delta = round(delta * hours)

    # 事件钩子（V0.15.3 基础，完整 EventSystem 监听在 V0.15.6）
    if action == "work":
        result.emitted_events.append("NPC_WORKED")
        # V0.15.4：工作赚日薪（按职业）
        from ..economy.system import npc_wage

        result.money_delta += npc_wage(npc.job)
    if action == "seek_help":
        result.emitted_events.append("NPC_SEEK_HELP")
    if action == "sleep" and prev_location and prev_location != (npc.home or ""):
        result.emitted_events.append("NPC_WENT_HOME")

    return result


def apply_result(world: Any, npc: Any, result: NPCActionResult) -> None:
    """把 ActionResult 应用到世界状态（EffectSystem 的轻量实现）。"""
    if result.to_location and result.to_location != npc.location:
        npc.location = result.to_location

    if result.money_delta:
        npc.state.money = max(0.0, npc.state.money + result.money_delta)
    npc.state.fatigue = max(0, min(100, npc.state.fatigue + result.fatigue_delta))
    if npc.needs is not None:
        for key, delta in result.needs_delta.items():
            setattr(
                npc.needs, key, max(0, min(100, getattr(npc.needs, key) + delta))
            )
    npc.money = int(npc.state.money)
    npc.fatigue = npc.state.fatigue

    # 地点活跃度：有人工作→地点活跃上升
    if result.location_activity_delta and world is not None:
        loc_state = world.world.locations.get(result.to_location or "")
        if loc_state:
            loc_state["activity"] = max(
                0, min(100, loc_state["activity"] + result.location_activity_delta)
            )