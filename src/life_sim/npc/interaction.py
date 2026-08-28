"""NPC-NPC 轻量交互系统（V0.15.5）。

规格：不写真正对白，只模拟结果——
同地点两个 NPC：关系 > 阈值 且 社交需求 > 门槛 → 一次"社交互动"
效果：双方社交需求下降、友谊/熟悉度上升、情绪上升。记录可见结果。

设计：一个 NPC 对其他 NPC 的关系存在 social_links 里；
第一次接触会建立 links（familiarity 0→），后续互动加深。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# 社交互动门槛
MIN_FAMILIARITY_FOR_CHAT = 10   # 至少要有点熟（familiarity≥10）
MIN_SOCIAL_NEED = 35            # 社交需求 ≥35 才会想聊
INTERACTION_COOLDOWN_DAYS = 3   # 同对 NPC 互动冷却（天）

# 互动收益（轻量）
CHAT_GAINS = {
    "familiarity": 2,
    "affection": 1,
    "mood": 2,
    "social_need_relief": -18,
}
NEW_LINK_GAIN = {"familiarity": 4, "affection": 1, "mood": 1}


@dataclass
class NPCSocialInteraction:
    """一次 NPC 间互动的可调试记录。"""

    npc_a: str
    npc_b: str
    location: str
    kind: str = "chat"  # 当前只有 chat（未来 visit/help/fight）
    details: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"{self.npc_a} 与 {self.npc_b} 在{self.location}交谈"


def _link(npc_a: Any, npc_b: Any, key: str, delta: int) -> None:
    """修改 A→B 的 social_link 值（双向之间用各自方向）。"""
    link = npc_a.social_links.setdefault(
        npc_b.id, {"familiarity": 0, "affection": 0, "trust": 0, "fear": 0}
    )
    for k in link:
        if k == key:
            link[k] = max(0, min(100, link.get(k, 0) + delta))


def can_interact(npc_a: Any, npc_b: Any) -> bool:
    """判断两个 NPC 是否可能互动。"""
    if npc_a.disappeared or npc_b.disappeared or not npc_a.state.alive or not npc_b.state.alive:
        return False
    if npc_a.id == npc_b.id:
        return False
    if npc_a.needs is None or npc_b.needs is None:
        return False
    if npc_a.needs.social < MIN_SOCIAL_NEED and npc_b.needs.social < MIN_SOCIAL_NEED:
        return False
    # 至少要有一方想社交，且彼此有点熟（或首次见面建立联系）
    familiarity_a = npc_a.social_links.get(npc_b.id, {}).get("familiarity", 0)
    familiarity_b = npc_b.social_links.get(npc_a.id, {}).get("familiarity", 0)
    if familiarity_a < MIN_FAMILIARITY_FOR_CHAT and familiarity_b < MIN_FAMILIARITY_FOR_CHAT:
        return False  # 完全陌生，除非双方都极想社交
    return True


def _cooldown_ok(a: Any, b: Any, last: dict, day: int) -> bool:
    key = frozenset({a.id, b.id})
    last_day = last.get(key)
    if last_day is None:
        return True
    return day - last_day >= INTERACTION_COOLDOWN_DAYS


def interact(npc_a: Any, npc_b: Any, *, day: int) -> NPCSocialInteraction | None:
    """在当前地点尝试互动。成功返回记录，失败返回 None。"""
    if not can_interact(npc_a, npc_b):
        return None
    if not _cooldown_ok(npc_a, npc_b, _last_interactions, day):
        return None

    _last_interactions[frozenset({npc_a.id, npc_b.id})] = day

    # 首次见面建立 link
    if npc_b.id not in npc_a.social_links:
        _seal_new_link(npc_a, npc_b)
    if npc_a.id not in npc_b.social_links:
        _seal_new_link(npc_b, npc_a)

    # 双向收益
    for npc, other in ((npc_a, npc_b), (npc_b, npc_a)):
        if npc.needs is not None:
            npc.needs.social = max(0, npc.needs.social + CHAT_GAINS["social_need_relief"])
        for key, val in (("familiarity", CHAT_GAINS["familiarity"]),
                         ("affection", CHAT_GAINS["affection"])):
            _link(npc, other, key, val)
        if npc.state is not None:
            npc.state.mood = max(0, min(100, npc.state.mood + CHAT_GAINS["mood"]))

    return NPCSocialInteraction(
        npc_a=npc_a.id, npc_b=npc_b.id, location=npc_a.location,
        kind="chat",
        details={
            "familiarity_a": npc_a.social_links.get(npc_b.id, {}).get("familiarity", 0),
            "familiarity_b": npc_b.social_links.get(npc_a.id, {}).get("familiarity", 0),
            "social_a": npc_a.needs.social if npc_a.needs else None,
            "social_b": npc_b.needs.social if npc_b.needs else None,
        },
    )


def _seal_new_link(npc: Any, other: Any) -> None:
    npc.social_links[other.id] = {
        "familiarity": NEW_LINK_GAIN["familiarity"],
        "affection": NEW_LINK_GAIN["affection"],
        "trust": 0,
        "fear": 0,
    }


# 运行期互动冷却记录（不持久化，重启后自然清零）
_last_interactions: dict = {}



def scan_and_interact(
    npcs: list[Any], *, day: int, location: str, use_day_locations: bool = True
) -> list[NPCSocialInteraction]:
    """扫描某地点的 NPC，两两尝试互动（O(n²) 但 n 很小）。

    默认（use_day_locations=True）用"当天白天待过的地点"判定共处：
    两人都在某地工作过即便晚上各自回家也算共处，社会网络因此能形成。
    """
    results: list[NPCSocialInteraction] = []
    present = []
    for n in npcs:
        if n.disappeared or n.state is None or not n.state.alive:
            continue
        day_locs = getattr(n, "_day_locations", None)
        if use_day_locations and day_locs is not None:
            if location in day_locs:
                present.append(n)
        elif n.location == location:
            present.append(n)
    for i in range(len(present)):
        for j in range(i + 1, len(present)):
            result = interact(present[i], present[j], day=day)
            if result is not None:
                results.append(result)
    return results