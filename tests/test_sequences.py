"""V0.28 专项测试：非凡序列与魔药晋升。"""

import pytest

from life_sim.engine import WorldEngine
from life_sim.mysticism.sequences import (
    SEQUENCES,
    can_consume,
    consume_potion,
    next_sequence,
    seq_name,
)
from life_sim.save import load_game, save_game


def test_sequences_defined_three_steps_each():
    assert set(SEQUENCES) == {"占卜家", "观众", "不眠者"}
    for pathway in SEQUENCES:
        assert set(SEQUENCES[pathway]) == {9, 8, 7}


def test_sequence_names():
    assert seq_name("占卜家", 9) == "占卜家"
    assert seq_name("占卜家", 8) == "小丑"
    assert seq_name("占卜家", 7) == "魔术师"
    assert seq_name("观众", 8) == "读心者"
    assert seq_name("不眠者", 7) == "梦魇"
    assert seq_name(None, 9) is None
    assert seq_name("占卜家", None) is None


def test_next_sequence_chain():
    assert next_sequence("占卜家", 9) == 8
    assert next_sequence("占卜家", 8) == 7
    assert next_sequence("占卜家", 7) is None  # 到底


def test_can_consume_spirituality_gate():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.spirituality = 10

    ok, msg = can_consume(state.character, "占卜家", 8)
    assert not ok  # 灵性门槛 25 未达
    assert "灵性不足" in msg

    state.character.spirituality = 30
    ok, _ = can_consume(state.character, "占卜家", 8)
    assert ok


def test_consume_potion_applies_bonus_and_madness():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 9
    state.character.spirituality = 30
    sp0 = state.character.spirituality

    changes = consume_potion(state.character, "占卜家", 8)

    assert changes.get("madness", 0) >= 10  # 疯狂代价
    assert state.character.spirituality >= sp0 + 4  # 序列加成


def test_select_pathway_starts_sequence_9():
    """选择途径时 sequence 应设为 9（V0.28 起始）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    graph = engine.event_system.graphs["path_choice"]
    seer = graph.nodes["path_seer"]
    engine.event_system.apply(graph, seer, state)

    assert state.character.pathway == "占卜家"
    assert state.character.sequence == 9


def test_event_promotes_sequence():
    """服食魔药事件（_sequence 特效键）晋升序列并打标签。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 9
    state.days_lived = 62

    graph = engine.event_system.graphs["seq_advance"]
    node = graph.nodes["seq9_seer_advance"]
    # 直接应用"饮下魔药"choice
    engine.event_system.apply_choice(graph, node, 0, state)

    assert state.character.sequence == 8
    assert "序列：小丑" in state.character.tags


def test_advance_events_require_own_pathway_lore():
    """晋升事件前置各自专属经历（镜像线索/看破谎言/夜巡）。"""
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["seq_advance"]
    seer = graph.nodes["seq9_seer_advance"]
    reader = graph.nodes["seq9_reader_advance"]
    insomn = graph.nodes["seq9_insomn_advance"]

    assert "shadow_watcher" in seer.conditions.get("any_clue", [])
    assert "途径：占卜家" in seer.conditions.get("any_tag", [])
    assert "看破谎言" in reader.conditions.get("any_tag", [])
    assert "不眠者夜巡" in insomn.conditions.get("any_tag", [])


def test_sequence_boosts_behavior_bonus():
    from life_sim.mysticism.pathways import pathway_behavior_bonus

    base9 = pathway_behavior_bonus("占卜家", "investigate", 9)
    seq8 = pathway_behavior_bonus("占卜家", "investigate", 8)
    seq7 = pathway_behavior_bonus("占卜家", "investigate", 7)

    assert base9 == 12
    assert seq8 > base9  # 高阶更强
    assert seq7 > seq8


def test_sequence_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 8

    save_game(state, "seq.json")
    loaded = load_game("seq.json")

    assert loaded.character.sequence == 8
    assert loaded.character.pathway == "占卜家"


def test_old_save_without_sequence_loads_none():
    import json
    import tempfile
    import pathlib

    import life_sim.save as save_module

    engine = WorldEngine(seed=1)
    state = engine.new_game()
    data = state.to_dict()
    data["character"].pop("sequence", None)

    tmp = pathlib.Path(tempfile.mkdtemp())
    save_module.SAVE_DIR = tmp
    path = tmp / "old.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    loaded = save_module.load_game("old.json")
    assert loaded.character.sequence is None