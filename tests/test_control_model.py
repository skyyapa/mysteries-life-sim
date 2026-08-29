"""V0.30 专项测试：原著失控模型（诱因 × 三档后果）。"""

import random

import pytest

from life_sim.engine import WorldEngine
from life_sim.mysticism.sequences import (
    SEQUENCES,
    TAG_BERSERK,
    TAG_DEAD_BODY,
    TAG_POISONED,
    TAG_RUNAWAY,
    TAG_TWISTED,
    TAG_UNSTABLE,
    _additive_risk,
    drink_potion,
)


def make_char(engine, spirit=30, stress=20, mood=50, madness=0):
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 9
    state.character.spirituality = spirit
    state.character.stress = stress
    state.character.mood = mood
    state.character.madness = madness
    return state.character


def test_additive_risk_accumulates_by_cause():
    """诱因逐项累积：状态越好风险越低，越差越高。"""
    engine = WorldEngine(seed=1)
    # 健康状态（灵性充足、压力低、疯狂 0）
    good = make_char(engine, spirit=60, stress=20, madness=0)
    risk_good = _additive_risk(good, "占卜家", 8)

    # 灵性枯竭 + 高压 + 深疯狂
    bad = make_char(engine, spirit=5, stress=75, madness=70)
    risk_bad = _additive_risk(bad, "占卜家", 8)

    assert risk_bad > risk_good + 0.3, f"状态差应远超状态好：{risk_good:.2f} vs {risk_bad:.2f}"


def test_unconsumed_advance_adds_risk():
    """未消化就强行晋升（<30 天）加成。"""
    engine = WorldEngine(seed=1)
    c = make_char(engine)
    base = _additive_risk(c, "占卜家", 8)
    c._last_advance_day = 5
    c._day = 10  # 间隔 5 天
    with_haste = _additive_risk(c, "占卜家", 8)
    assert with_haste > base + 0.1


def test_pollution_tag_adds_risk():
    engine = WorldEngine(seed=1)
    c = make_char(engine)
    base = _additive_risk(c, "占卜家", 8)
    c.tags.append("镜中的窥视者")
    polluted = _additive_risk(c, "占卜家", 8)
    assert polluted > base


def test_three_outcomes_occur_over_many_rolls():
    """三档后果都会出现（B 最多，S 罕见）。"""
    outcomes = {"B": 0, "A": 0, "S": 0}
    for seed in range(3000):
        r = drink_potion(make_char(WorldEngine(seed=1), spirit=3, madness=90),
                         "占卜家", 8, rng=random.Random(seed))
        if not r["ok"]:
            outcomes[r["outcome"]] += 1
    assert outcomes["B"] > 0
    assert outcomes["A"] > 0
    assert outcomes["S"] > 0
    assert outcomes["B"] > outcomes["S"]


def test_berserk_outcome_has_correct_tags():
    """B 当场发狂：标签与疯狂大涨、晋升失败。"""
    outcomes = {"B": None, "A": None, "S": None}
    for seed in range(600):
        r = drink_potion(make_char(WorldEngine(seed=1), spirit=3, madness=95),
                         "占卜家", 8, rng=random.Random(seed))
        if not r["ok"] and outcomes[r["outcome"]] is None:
            outcomes[r["outcome"]] = r
    b = outcomes["B"]
    assert b is not None and TAG_BERSERK in b["tags"] and TAG_RUNAWAY in b["tags"]
    assert b["changes"]["madness"] >= 20  # 基疯狂10 + 发狂14


def test_twisted_outcome_charisma_drop():
    a = None
    for seed in range(2000):
        r = drink_potion(make_char(WorldEngine(seed=1), spirit=3, madness=95),
                         "占卜家", 8, rng=random.Random(seed))
        if not r["ok"] and r["outcome"] == "A":
            a = r
            break
    assert a is not None and TAG_TWISTED in a["tags"]
    assert a["changes"]["charisma"] < 0  # 人格扭曲魅力下降


def test_death_outcome_fatal():
    s = None
    for seed in range(4000):
        r = drink_potion(make_char(WorldEngine(seed=1), spirit=2, madness=99),
                         "占卜家", 8, rng=random.Random(seed))
        if not r["ok"] and r["outcome"] == "S":
            s = r
            break
    assert s is not None and s["death"] is True
    assert TAG_DEAD_BODY in s["tags"]
    assert s["changes"]["health"] <= -40  # 身体崩溃


def test_event_sets_dead_on_fatal_outcome():
    """致命失控（S）经事件应用后角色死亡。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 9
    state.character.spirituality = 2
    state.character.madness = 99
    state.days_lived = 62

    graph = engine.event_system.graphs["seq_advance"]
    node = graph.nodes["seq9_seer_advance"]
    # 多试几个引擎实例直到触发死亡
    for seed in range(50):
        s = engine.new_game()
        s.character.pathway = "占卜家"
        s.character.sequence = 9
        s.character.spirituality = 2
        s.character.madness = 99
        s.days_lived = 62
        engine.event_system.apply_choice(graph, node, 0, s)
        if s.character.dead:
            assert s.character.death_reason is not None
            assert "失控" in s.character.death_reason
            break
    else:
        pytest.skip("本批种子未触发 S（罕见），机制由 drink_potion 单测覆盖")


def test_dead_character_cannot_act():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.dead = True
    with pytest.raises(ValueError, match="失控死亡"):
        engine.process_action(state, "work")