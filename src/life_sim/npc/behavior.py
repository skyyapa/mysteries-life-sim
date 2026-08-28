"""NPC 行为候选系统（V0.15.3）。

不再是"日程说什么就做什么"，而是：
    生成候选（日程行为 + 需求/状态/目标触发的可能行为）
        ↓
    给每个候选打分
        ↓
    选择最高分执行

评分公式（规格原文）：
    score = schedule_weight + need_weight + goal_weight + world_weight + random_variation

这样避免一堆 if-else，且未来 AI/Lisien 只需影响 candidate score，不直接控制 NPC。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import NPCNeeds, NPCState


@dataclass
class BehaviorCandidate:
    action_id: str
    score: float = 0
    reasons: list[str] = field(default_factory=list)

    def __repr__(self) -> str:  # 便于调试面板
        return f"{self.action_id}({self.score:.0f}:{','.join(self.reasons[:3])})"


# 基准分：日程安排的行为天然优先
SCHEDULE_BASE = 50
# 日常行为候选池（无日程时也会被需求触发）
ALL_ACTIONS = [
    "work", "eat", "rest", "sleep", "travel", "go_home",
    "shop", "socialize", "wander", "visit", "seek_help", "stay_home",
]


def _goal_weight(npc: Any, action_id: str) -> int:
    """目标加成：不同目标偏向不同行为。"""
    goal = (npc.goal or "").lower() if hasattr(npc, "goal") else ""
    money_goal = any(k in goal for k in ("钱", "赚", "收入", "生计", "活", "生意"))
    if action_id == "work":
        if money_goal:
            return 15
        if "教" in goal or "安稳" in goal:
            return 10
    if action_id == "stay_home":
        if "教" in goal or "安稳" in goal:
            return 8
    if action_id == "socialize":
        if "朋友" in goal or "街坊" in goal or "关系" in goal:
            return 10
    if action_id == "pray" and ("教" in goal or "神" in goal):
        return 12
    # V0.21：非凡途径加成（有 pathway 的对象，如玩家角色）
    pathway = getattr(npc, "pathway", None)
    if pathway:
        from ..mysticism.pathways import pathway_behavior_bonus

        bonus = pathway_behavior_bonus(pathway, action_id)
        if bonus:
            return bonus
    return 0


def _need_weight(needs: NPCNeeds, state: NPCState, action_id: str) -> int:
    """需求权重：迫切需求驱动行为，且能盖过日程计划。"""
    w = 0
    if needs.hunger >= 70 and action_id == "eat":
        w += 35
    if needs.hunger >= 85 and action_id == "eat":
        w += 45  # 饿到极限一定要吃
    if needs.rest >= 70 and action_id in ("rest", "sleep"):
        w += 35
    if needs.rest >= 85 and action_id == "sleep":
        w += 25
    if needs.social >= 60 and action_id == "socialize":
        w += 25
    if needs.social >= 80 and action_id == "visit":
        w += 12
    if needs.safety >= 55 and action_id == "stay_home":
        w += 25
    if state.fatigue >= 65 and action_id in ("rest", "sleep"):
        w += 30
    if state.fatigue >= 85 and action_id == "rest":
        w += 25
    # 生病/受伤：不该出门工作，倾向待家或求助
    if state.sick and action_id == "stay_home":
        w += 40
    if state.sick and action_id == "work":
        w -= 50
    if state.injured and action_id == "work":
        w -= 35
    if state.sick and action_id == "seek_help":
        w += 30
    # 没钱倾向工作/不购物
    if state.money < 5 and action_id == "work":
        w += 40
    if state.money < 5 and action_id == "shop":
        w -= 25
    if state.money < 2 and action_id == "shop":
        w -= 35
    # 饥肠辘辘还强行工作/闲逛会扣分（撑不住）
    if needs.hunger >= 90 and action_id in ("work", "wander", "socialize"):
        w -= 15
    # 疲惫不堪还工作/社交也会扣分
    if state.fatigue >= 85 and action_id in ("work", "socialize"):
        w -= 20
    return w


def _world_weight(is_night: bool, city_tension: int, action_id: str) -> int:
    """世界权重：昼夜/紧张度。"""
    w = 0
    if is_night:
        if action_id in ("sleep", "go_home", "stay_home"):
            w += 55  # 深夜就该回家/休息，能压过日程
        if action_id in ("wander", "shop", "work", "visit"):
            w -= 30
    if city_tension >= 60:
        if action_id == "stay_home":
            w += 10
        if action_id in ("wander", "socialize"):
            w -= 8
    return w


def generate_candidates(
    npc: Any,
    *,
    schedule_action: str | None,
    needs: NPCNeeds,
    state: NPCState,
    is_night: bool,
    city_tension: int,
    day_index: int,
) -> list[BehaviorCandidate]:
    """生成候选并打分。

    候选 = 日程计划行为（高基准）+ 需求/状态/目标/世界触发的可能行为（零基准但加分）。
    random_variation：每人每天有 ±10 的随机波动，避免完全可预测。
    """
    import random

    rng = random.Random(hash((npc.id, day_index)) % (2**32))
    candidates: list[BehaviorCandidate] = []

    def add(action_id: str, base: int, reason: str | None = None):
        goal = _goal_weight(npc, action_id)
        need = _need_weight(needs, state, action_id)
        world = _world_weight(is_night, city_tension, action_id)
        variation = rng.randint(-10, 10)
        score = base + goal + need + world + variation
        reasons = []
        if reason:
            reasons.append(reason)
        if need > 0:
            reasons.append("need")
        if goal > 0:
            reasons.append("goal")
        candidates.append(
            BehaviorCandidate(action_id=action_id, score=score, reasons=reasons)
        )

    # 日程计划的行为：基准 50
    if schedule_action:
        add(schedule_action, SCHEDULE_BASE, "schedule")

    # 潜在行为：零基准，靠需求/目标/世界加分胜出
    for action_id in ALL_ACTIONS:
        if action_id != schedule_action:
            add(action_id, 0)

    return candidates


def select(candidates: list[BehaviorCandidate]) -> BehaviorCandidate | None:
    if not candidates:
        return None
    return max(candidates, key=lambda c: c.score)


def decide_behavior(
    npc: Any,
    *,
    schedule_action: str | None,
    needs: NPCNeeds,
    state: NPCState,
    is_night: bool,
    city_tension: int,
    day_index: int,
) -> tuple[str, list[BehaviorCandidate]]:
    """生成→打分→选择，返回 (选中的行为 id, 完整候选列表用于调试)。"""
    candidates = generate_candidates(
        npc,
        schedule_action=schedule_action,
        needs=needs,
        state=state,
        is_night=is_night,
        city_tension=city_tension,
        day_index=day_index,
    )
    chosen = select(candidates)
    return (chosen.action_id if chosen else "stay_home", candidates)