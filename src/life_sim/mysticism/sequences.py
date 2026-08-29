"""非凡序列体系（V0.28+，克制版：每条途径 9→8→7 三阶）。

原著对应（简化）：
- 占卜家：序列9 占卜家 → 序列8 小丑 → 序列7 魔术师
- 观众：   序列9 观众   → 序列8 读心者 → 序列7 心理医生
- 不眠者： 序列9 不眠者 → 序列8 午夜诗人 → 序列7 梦魇

服食魔药（V0.30 原著失控模型，用户定稿）：
危险的核心不是"够不够格"，而是失控——
诱因（原著"失控的常见原因"）：
  1. 魔药本身：相性差（初饮基线）/ 高序列污染更重
  2. 自身状态：灵性枯竭（外溢）/ 精神低谷 / 疯狂已深
  3. 未消化就强行晋升（距上次晋升 <30 天）
  4. 外界污染：接触高位格类标签
  5. 跨途径服用（极高，数据防护）
后果分档（原著"失控的典型表现"）：
  B 精神失常·当场发狂（最常：疯狂大爆、晋升失败）
  A 人格被扭曲（较常：冷酷残忍、魅力-）
  S 精神死亡·身体崩溃（致命：灵魂湮灭、身体异变 → 角色终结）
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
        7: {"name": "心理医生", "别名": "精神分析师", "魔药": "心理医生魔药", "灵性门槛": 45, "疯狂风险": 14, "特质": "言语如刀"},
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

# ---- 失控检定（V0.30 原著模型：诱因 × 后果） ----

# 诱因权重（概率加成，对应原著"失控的常见原因"）
CONTROL_BASE_RISK = 0.06        # 相性差基线（初饮者极易失控）
CONTROL_MID_SEQ_PENALTY = 0.06  # 序列 8+ 的魔药精神污染更重
GATE_DEFICIT_PER = 0.45         # 灵性枯竭：每差门槛比例%的加成（灵性外溢）
STRESS_HIGH_RISK = 0.12         # 长期精神低谷（stress>60）
MOOD_LOW_RISK = 0.10            # 情绪低谷（mood<25）
MADNESS_HIGH_RISK = 0.15        # 自身疯狂高（madness>60）
RUINOUS_EXTRA = 0.35            # 已是濒危（madness≥80）时再加
UNSUPERVISED_RISK = 0.20        # 未消化就强行晋升（上次晋升 <30 天）
POLLUTION_TAG_RISK = 0.08       # 外界污染：接触高位格类标签
CROSS_PATHWAY_RISK = 0.60       # 服用不相邻途径魔药（极高）

# 后果分档权重（失控时 roll；对应原著"失控的三种典型表现"）
OUTCOME_WEIGHTS = {
    "B": 55,   # 精神失常·当场发狂（最常）
    "A": 32,   # 人格被扭曲（较常）
    "S": 13,   # 精神死亡·身体崩溃（罕见但致命）
}

# 后果标签
TAG_RUNAWAY = "魔药反噬"
TAG_UNSTABLE = "灵性外溢"
TAG_POISONED = "精神污染"
TAG_BERSERK = "当场发狂"       # B：精神失常
TAG_TWISTED = "人格被扭曲"     # A：人格扭曲
TAG_DEAD_BODY = "身体崩溃"     # S：精神死亡，身体异变

# 需带"外界污染"特征才加权的标签（接触高位格/邪神呓语）
POLLUTION_TAGS = {"精神污染", "镜中的窥视者", "接触高位格", "邪神呓语"}


def seq_name(pathway: str | None, sequence: int | None) -> str | None:
    """当前序列的人类可读名（含别名，如 心理医生（精神分析师））。"""
    if not pathway or sequence is None:
        return None
    spec = SEQUENCES.get(pathway, {}).get(sequence)
    if spec is None:
        return None
    base = spec["name"]
    alias = spec.get("别名")
    return f"{base}（{alias}）" if alias else base


def seq_tag_name(pathway: str | None, sequence: int | None) -> str | None:
    """序列标签名（纯名，无别名）——用于 tags 匹配，保证条件稳定。"""
    if not pathway or sequence is None:
        return None
    spec = SEQUENCES.get(pathway, {}).get(sequence)
    return spec["name"] if spec else None


def next_sequence(pathway: str | None, sequence: int | None) -> int | None:
    """晋升目标序列（9→8→7，越低越高阶）。"""
    if not pathway or sequence is None or sequence <= 7:
        return None
    target = sequence - 1
    if target not in SEQUENCES.get(pathway, {}):
        return None
    return target


def _additive_risk(character: Any, pathway: str, target_seq: int) -> float:
    """失控概率：按原著诱因逐项累积。"""
    spec = SEQUENCES.get(pathway, {}).get(target_seq)
    if spec is None:
        return 0.0
    risk = CONTROL_BASE_RISK
    # 1) 魔药本身：序列越高污染越重
    if target_seq <= 8:
        risk += CONTROL_MID_SEQ_PENALTY
    # 2) 自身状态：灵性枯竭（外溢）+ 精神低谷 + 疯狂已高
    gate = spec["灵性门槛"]
    spirit = getattr(character, "spirituality", 0)
    if spirit < gate:
        risk += min(0.7, GATE_DEFICIT_PER * (gate - spirit) / gate * 3)
    if getattr(character, "stress", 0) > 60:
        risk += STRESS_HIGH_RISK
    if getattr(character, "mood", 50) < 25:
        risk += MOOD_LOW_RISK
    if getattr(character, "madness", 0) > 60:
        risk += MADNESS_HIGH_RISK
    if getattr(character, "madness", 0) >= 80:
        risk += RUINOUS_EXTRA
    # 3) 未消化就强行晋升（上次晋升距今 <30 天）
    last_advance = getattr(character, "_last_advance_day", None)
    now = getattr(character, "_day", 0)
    if last_advance is not None and (now - last_advance) < 30:
        risk += UNSUPERVISED_RISK
    # 4) 外界污染：带高位格接触类标签
    tags = getattr(character, "tags", []) or []
    if POLLUTION_TAGS & set(tags):
        risk += POLLUTION_TAG_RISK
    # 5) 跨途径：目标序列不在本途径 → 极高（数据防护）
    if target_seq not in SEQUENCES.get(pathway, {}):
        risk += CROSS_PATHWAY_RISK
    return min(0.97, risk)


def _roll_outcome(rng: Any) -> tuple[str, dict[str, int]]:
    """失控后果 roll：S 致命 / A 扭曲 / B 发狂（对应原著三种表现）。"""
    total = sum(OUTCOME_WEIGHTS.values())
    roll = rng.random() * total
    acc = 0
    for key, weight in OUTCOME_WEIGHTS.items():
        acc += weight
        if roll < acc:
            if key == "B":  # 精神失常·当场发狂
                return key, {"madness": 14, "stress": 12, "stamina": -6}
            if key == "A":  # 人格被扭曲
                return key, {"madness": 16, "stress": 6, "charisma": -6}
            # S：精神死亡·身体崩溃（最致命）
            return key, {"madness": 30, "health": -50, "stamina": -20}
    return "B", {"madness": 14, "stress": 12, "stamina": -6}


def drink_potion(
    character: Any, pathway: str, target_seq: int, rng: Any = None
) -> dict[str, Any]:
    """服食魔药（V0.30 原著失控模型）。

    返回：
      {"ok": bool,           # 平稳晋升成功
       "changes": {...},      # 需应用的属性变化
       "tags": [str],         # 需打上的标签（成功=序列；失控=对应反噬）
       "reason": str,         # 结果说明
       "outcome": str|None    # 失控时：S 精神死亡 / A 人格扭曲 / B 当场发狂
       "death": bool}         # 是否精神死亡·身体崩溃（角色终结）
    """
    import random

    if rng is None:
        rng = random.Random()
    spec = SEQUENCES.get(pathway, {}).get(target_seq)
    if spec is None:
        return {"ok": False, "changes": {}, "tags": [], "reason": "该序列不存在",
                "outcome": None, "death": False}

    risk = _additive_risk(character, pathway, target_seq)
    runaway = rng.random() < risk

    changes: dict[str, int] = {"madness": spec["疯狂风险"]}
    tags: list[str] = [f"序列：{seq_tag_name(pathway, target_seq)}"]
    if runaway:
        outcome, extra = _roll_outcome(rng)
        # 叠加：基疯狂代价 + 后果额外（原 update 会覆盖，改为逐项加）
        for k, v in extra.items():
            changes[k] = changes.get(k, 0) + v
        # 标签按后果分档
        if outcome == "B":
            tags = [TAG_BERSERK, TAG_RUNAWAY, TAG_UNSTABLE, TAG_POISONED]
            reason = (
                f"魔药入喉，你的精神当场崩断——你发疯般撕扯着一切近身之物（失控·发狂）。"
                f"众人合力才将你制住，晋升失败。"
            )
        elif outcome == "A":
            tags = [TAG_TWISTED, TAG_RUNAWAY, TAG_POISONED]
            reason = (
                f"魔药中那道古老意志压过了你——你清醒地感受着自己变得冷酷残忍，"
                f"却再也没能找回原来的自己（失控·人格扭曲）。晋升失败。"
            )
        else:  # S 精神死亡·身体崩溃
            tags = [TAG_DEAD_BODY, TAG_RUNAWAY, TAG_POISONED, TAG_UNSTABLE]
            reason = (
                f"魔药的力量炸开了你意识的最深处——灵魂在震爆中湮灭，"
                f"你的身体开始异变、崩解（失控·精神死亡）。这是终局。"
            )
        return {"ok": False, "changes": changes, "tags": tags, "reason": reason,
                "outcome": outcome, "death": (outcome == "S")}

    # 平稳服食：套用序列加成
    for key, val in SEQUENCE_STAT_BONUS.get(target_seq, {}).items():
        changes[key] = val
    reason = (
        f"魔药在意识中沉定成新的形状，你成为「{seq_name(pathway, target_seq)}」。"
    )
    return {"ok": True, "changes": changes, "tags": tags, "reason": reason,
            "outcome": None, "death": False}


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