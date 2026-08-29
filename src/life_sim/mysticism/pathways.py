"""非凡途径（V0.21，克制版：3 条低序列途径，不展开 22 途）。

原则：不做完整途径树，只做 3 条的代表性能力差异，让选择有实质影响：
- 占卜家：灵性敏锐 → 调查/推理更稳、疯狂更敏感但可控
- 观众：洞察人心 → 社交更强、发现隐藏线索能力
- 不眠者：夜行耐力 → 夜间行动优势、恐惧耐受
"""

from __future__ import annotations

from typing import Any

PATHWAYS = {
    "占卜家": {
        "id": "seer",
        "trait": "灵性敏锐",
        "description": "你开始能隐约捕捉到事物之间的联系。占卜是你最贴近的日常能力。",
        "stat_bonus": {"spirituality": 5, "mysticism_knowledge": 3},
    },
    "观众": {
        "id": "reader",
        "trait": "洞察人心",
        "description": "你看人的方式与过去不同：眼神、停顿、指尖的小动作都开始说话。",
        "stat_bonus": {"charisma": 4, "spirituality": 2},
    },
    "不眠者": {
        "id": "insomn",  # 不眠者/夜行者
        "trait": "夜行耐力",
        "description": "夜对你不再可怕。你在黑暗中看得更清，也熬得住更长的夜。",
        "stat_bonus": {"stamina": 4, "spirituality": 3},
    },
}

# 途径 → 行为权重影响（behavior.decide_behavior 读取）
PATHWAY_BEHAVIOR = {
    "占卜家": {"investigate": 12, "deduce": 12, "pray": 6},
    "观众": {"socialize": 10, "wander": 6, "visit": 8},
    "不眠者": {"work": 6, "wander": 6},  # 耐劳/耐夜
}


def apply_pathway_bonus(character: Any, pathway: str) -> None:
    """选择途径时套用属性加成。"""
    spec = PATHWAYS.get(pathway)
    if spec is None:
        return
    for key, value in spec["stat_bonus"].items():
        if hasattr(character, key):
            current = getattr(character, key)
            setattr(character, key, max(0, min(100, current + value)))


def pathway_behavior_bonus(pathway: str | None, action_id: str, sequence: int | None = None) -> int:
    """行为评分加成：途径影响行为倾向；序列越高加成越强（V0.28）。"""
    if not pathway:
        return 0
    base = PATHWAY_BEHAVIOR.get(pathway, {}).get(action_id, 0)
    if base == 0:
        return 0
    from .sequences import SEQUENCE_BEHAVIOR_MULT

    mult = SEQUENCE_BEHAVIOR_MULT.get(sequence or 9, 1.0)
    return int(round(base * mult))