"""非凡序列体系（V0.28，克制版：每条途径 9→8→7 三阶）。

原著对应（简化）：
- 占卜家：序列9 占卜家 → 序列8 小丑 → 序列7 魔术师
- 观众：   序列9 观众   → 序列8 读心者 → 序列7 心理医生
- 不眠者： 序列9 不眠者 → 序列8 午夜诗人 → 序列7 梦魇

服食魔药：需要灵性门槛 + 疯狂风险（越高序列越险）；
高阶序列解锁更强的专属加成/行动。
"""

from __future__ import annotations

from typing import Any

# 途径 → {序列号: 序列资料}
SEQUENCES: dict[str, dict[int, dict[str, Any]]] = {
    "占卜家": {
        9: {"name": "占卜家", "魔药": "占卜家魔药", "灵性门槛": 12, "疯狂风险": 5, "特质": "灵性敏锐"},
        8: {"name": "小丑", "魔药": "小丑魔药", "灵性门槛": 25, "疯狂风险": 10, "特质": "七窍皆明"},
        7: {"name": "魔术师", "魔药": "魔术师魔药", "灵性门槛": 45, "疯狂风险": 16, "特质": "掌心把戏"},
    },
    "观众": {
        9: {"name": "观众", "魔药": "观众魔药", "灵性门槛": 12, "疯狂风险": 4, "特质": "洞察人心"},
        8: {"name": "读心者", "魔药": "读心者魔药", "灵性门槛": 25, "疯狂风险": 9, "特质": "见他心识"},
        7: {"name": "心理医生", "魔药": "心理医生魔药", "灵性门槛": 45, "疯狂风险": 14, "特质": "言语如刀"},
    },
    "不眠者": {
        9: {"name": "不眠者", "魔药": "不眠者魔药", "灵性门槛": 12, "疯狂风险": 6, "特质": "夜行耐力"},
        8: {"name": "午夜诗人", "魔药": "午夜诗人魔药", "灵性门槛": 25, "疯狂风险": 11, "特质": "夜曲入梦"},
        7: {"name": "梦魇", "魔药": "梦魇魔药", "灵性门槛": 45, "疯狂风险": 18, "特质": "织梦者"},
    },
}

# 序列 → 行为加成强度（越高越强；路径接 behavior._goal_weight）
SEQUENCE_BEHAVIOR_MULT: dict[int, float] = {9: 1.0, 8: 1.6, 7: 2.4}

# 序列 → 额外属性加成（服食魔药时一次性套用）
SEQUENCE_STAT_BONUS: dict[int, dict[str, int]] = {
    8: {"spirituality": 4, "intelligence": 2},
    7: {"spirituality": 6, "intelligence": 3, "stamina": -3},
}


def seq_name(pathway: str | None, sequence: int | None) -> str | None:
    """当前序列的人类可读名。"""
    if not pathway or sequence is None:
        return None
    if sequence not in SEQUENCES.get(pathway, {}):
        return None
    return SEQUENCES[pathway][sequence]["name"]


def next_sequence(pathway: str | None, sequence: int | None) -> int | None:
    """晋升目标序列（9→8→7，越低越高阶）。"""
    if not pathway or sequence is None or sequence <= 7:
        return None
    target = sequence - 1
    if target not in SEQUENCES.get(pathway, {}):
        return None
    return target


def can_consume(
    character: Any, pathway: str, target_seq: int
) -> tuple[bool, str]:
    """能否服食某序列魔药：灵性门槛。"""
    spec = SEQUENCES.get(pathway, {}).get(target_seq)
    if spec is None:
        return False, "该序列不存在"
    if character.spirituality < spec["灵性门槛"]:
        return (
            False,
            f"灵性不足：需要 {spec['灵性门槛']}，当前 {character.spirituality}",
        )
    return True, "可以服食"


def consume_potion(character: Any, pathway: str, target_seq: int) -> dict[str, int]:
    """服食魔药：套用序列加成与疯狂代价，返回变化。

    注意：疯狂判定（是否失控）由调用方（事件系统）决定。
    """
    spec = SEQUENCES.get(pathway, {}).get(target_seq)
    if spec is None:
        return {}
    changes: dict[str, int] = {"madness": spec["疯狂风险"]}
    for key, val in SEQUENCE_STAT_BONUS.get(target_seq, {}).items():
        changes[key] = val
    character.apply_changes({k: v for k, v in changes.items() if k != "madness"})
    return changes