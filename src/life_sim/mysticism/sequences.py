"""非凡序列体系（V0.28，克制版：每条途径 9→8→7 三阶）。

原著对应（简化）：
- 占卜家：序列9 占卜家 → 序列8 小丑 → 序列7 魔术师
- 观众：   序列9 观众   → 序列8 读心者 → 序列7 心理医生
- 不眠者： 序列9 不眠者 → 序列8 午夜诗人 → 序列7 梦魇

服食魔药（V0.29 失控模型，用户修正）：
危险的核心不是"够不够格"，而是失控——
- 精神污染：魔药蕴含原主人精神烙印，服食者被疯狂/偏执意志侵蚀（基线风险）
- 灵性外溢：刚非凡者灵性不稳，灵性越低越易外溢（门槛不足 → 风险上升）
- 相性差：初期魔药与意识相性差，极易失控
灵性门槛不再是硬门槛（灵性低照样能遇事件/能喝），而是"安全线"——
灵性 ≥ 门槛 → 平稳服食概率高；灵性 < 门槛 → 失控风险大。
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

# 序列 → 额外属性加成（平稳服食成功后一次性套用）
SEQUENCE_STAT_BONUS: dict[int, dict[str, int]] = {
    8: {"spirituality": 4, "intelligence": 2},
    7: {"spirituality": 6, "intelligence": 3, "stamina": -3},
}

# 失控检定参数（规则驱动）
CONTROL_BASE_RISK = 0.10      # 平稳线以下的基线失控率（相性差/精神污染）
CONTROL_GATE_BONUS = 0.35     # 灵性达标时的安全加成（风险降低）
STRAY_PER_GATE = 0.35         # 灵性亏空每差一格门槛比例的额外失控率（灵性外溢）
RUNAWAY_MADNESS_BASE = 10     # 失控时额外疯狂（精神污染反噬）

# 失控结果标签
TAG_RUNAWAY = "魔药反噬"
TAG_UNSTABLE = "灵性外溢"
TAG_POISONED = "精神污染"


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


def _base_control_risk(pathway: str, target_seq: int) -> float:
    """不含灵性修正的失控基线（精神污染/相性差）。"""
    spec = SEQUENCES.get(pathway, {}).get(target_seq)
    if spec is None:
        return 0.0
    # 序列越高、魔药精神污染越重（疯狂风险越高 → 更易失控）
    return CONTROL_BASE_RISK + (spec["疯狂风险"] - 4) * 0.02


def drink_potion(
    character: Any, pathway: str, target_seq: int, rng: Any = None
) -> dict[str, Any]:
    """服食魔药（V0.29 失控模型）。

    返回：
      {"ok": bool,          # 平稳晋升成功
       "changes": {...},     # 需应用的属性变化（疯狂/灵性/智力…）
       "tags": [str],        # 需打上的标签
       "reason": str}        # 结果说明（平稳/失控原因）
    """
    import random

    if rng is None:
        rng = random.Random()
    spec = SEQUENCES.get(pathway, {}).get(target_seq)
    if spec is None:
        return {"ok": False, "changes": {}, "tags": [], "reason": "该序列不存在"}

    gate = spec["灵性门槛"]
    spirit = getattr(character, "spirituality", 0)
    deficit = max(0, gate - spirit)

    # 失控率：基线（污染/相性） − 灵性达标安全加成 + 灵性外溢惩罚
    risk = _base_control_risk(pathway, target_seq)
    if deficit <= 0:
        risk = max(0.02, risk - CONTROL_GATE_BONUS)
    else:
        risk += min(0.7, STRAY_PER_GATE * (deficit / gate) * 3)

    runaway = rng.random() < risk

    changes: dict[str, int] = {"madness": spec["疯狂风险"]}
    tags: list[str] = [f"序列：{seq_name(pathway, target_seq)}"]
    if runaway:
        # 失控：精神污染反噬 + 灵性外溢，序列不晋升
        changes["madness"] += RUNAWAY_MADNESS_BASE
        changes["stress"] = changes.get("stress", 0) + 8
        tags = [TAG_RUNAWAY, TAG_UNSTABLE, TAG_POISONED]
        reason = (
            f"魔药入喉，意识猛地被另一股疯狂意志撕扯（失控）——"
            f"精神烙印的反噬让你眼前一片血红，晋升失败。"
        )
        return {"ok": False, "changes": changes, "tags": tags, "reason": reason}

    # 平稳服食：套用序列加成
    for key, val in SEQUENCE_STAT_BONUS.get(target_seq, {}).items():
        changes[key] = val
    reason = (
        f"魔药在意识中沉定成新的形状，你成为「{seq_name(pathway, target_seq)}」。"
    )
    return {"ok": True, "changes": changes, "tags": tags, "reason": reason}


# 兼容旧接口
def can_consume(character: Any, pathway: str, target_seq: int) -> tuple[bool, str]:
    """【弃用语义】原为硬门槛；现只做提示，不再阻止。"""
    spec = SEQUENCES.get(pathway, {}).get(target_seq)
    if spec is None:
        return False, "该序列不存在"
    if character.spirituality < spec["灵性门槛"]:
        return False, f"灵性偏低（{character.spirituality} < {spec['灵性门槛']}）——高风险，但可以尝试"
    return True, "灵性达标，风险较低"


def consume_potion(character: Any, pathway: str, target_seq: int) -> dict[str, int]:
    """【兼容旧测试】旧接口：模拟平稳服食（不检定）。"""
    result = drink_potion(character, pathway, target_seq, rng=_dummy_rng())
    return result["changes"]


def _dummy_rng():
    import random

    return random.Random(0)