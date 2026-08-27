"""NPC 需求系统（V0.15.1）。

需求随时间自然增长；活动（由 behavior 决定）反过来满足需求。
规则驱动，用简单的 per-hour 漂移，0=满足，100=迫切。
"""

from __future__ import annotations

from .models import NPCNeeds, NPCState

# 每小时需求增长（0-100 满格）
HOURLY_DRIFT = {
    "hunger": 2.2,   # 不吃东西约 45 小时到 100
    "rest": 1.6,     # 不睡约 60 小时到 100
    "social": 0.8,   # 不社交约 5 天到 100
    "safety": 0.4,   # 安全需求低增长
}

# 活动对需求/状态的修正（activity 每执行一小时）
ACTIVITY_EFFECTS = {
    "sleep": {"needs": {"rest": -18, "hunger": 0.5}, "state": {"fatigue": -25, "health": 2}},
    "eat": {"needs": {"hunger": -60}, "state": {}},
    "work": {"needs": {"rest": 1.5, "hunger": 0.5}, "state": {"fatigue": 8, "stress": 2}},
    "rest": {"needs": {"rest": -16, "social": 1}, "state": {"fatigue": -12, "stress": -3}},
    "go_home": {"needs": {}, "state": {}},
    "shop": {"needs": {"hunger": -8}, "state": {"money": -3.0}},
    "socialize": {"needs": {"social": -30, "hunger": 1}, "state": {"stress": -4, "mood": 3}},
    "wander": {"needs": {"social": -10, "rest": 0.5}, "state": {"stress": -2}},
    "stay_home": {"needs": {}, "state": {"stress": -1}},
    "work_out": {"needs": {"rest": 4}, "state": {"fatigue": 10, "stress": -5}},
    "visit": {"needs": {"social": -20}, "state": {"mood": 2}},
    "pray": {"needs": {"safety": -15}, "state": {"stress": -3}},
    "seek_help": {"needs": {"safety": -20}, "state": {}},
    "breakfast": {"needs": {"hunger": -45}, "state": {}},
    "lunch": {"needs": {"hunger": -55}, "state": {}},
    "dinner": {"needs": {"hunger": -50}, "state": {}},
}


def drift_needs(needs: NPCNeeds, hours: float) -> None:
    """需求随时间增长（整数化，保证存档往返一致）。"""
    for key, rate in HOURLY_DRIFT.items():
        new_value = round(getattr(needs, key) + rate * hours)
        setattr(needs, key, min(100, max(0, new_value)))


def apply_activity(
    needs: NPCNeeds, state: NPCState | None, activity: str, hours: float = 1.0
) -> None:
    """执行活动：满足需求、影响状态（整数化）。

    state 可为 None：只更新需求（V0.15.1 日程满足用），
    状态层面的体力/健康变化留给 V0.15.3 行为系统统一处理。
    """
    effect = ACTIVITY_EFFECTS.get(activity)
    if effect is None:
        return
    for key, delta in effect.get("needs", {}).items():
        new_value = round(getattr(needs, key) + delta * hours)
        setattr(needs, key, max(0, min(100, new_value)))
    if state is not None:
        for key, delta in effect.get("state", {}).items():
            new_value = round(getattr(state, key) + delta * hours)
            setattr(
                state,
                key,
                max(0, new_value) if key == "money" else max(0, min(100, new_value)),
            )
    needs.clamp()
    if state is not None:
        state.clamp()


def financial_stability(hours: float = 1.0) -> None:
    pass  # 预留：与 economy 联动时扩展