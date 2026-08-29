"""V0.28 专项测试：非凡序列与魔药晋升。"""

import pytest

from life_sim.engine import WorldEngine
from life_sim.mysticism.sequences import (
    SEQUENCES,
    can_consume,
    consume_potion,
    drink_potion,
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


def test_can_consume_spirituality_hint_not_blocker():
    """V0.29：灵性门槛不再是硬门槛——低于门槛也给提示（高风险可尝试）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.spirituality = 10

    ok, msg = can_consume(state.character, "占卜家", 8)
    assert not ok  # 低于门槛给出警告
    assert "风险" in msg or "偏低" in msg

    state.character.spirituality = 30
    ok, _ = can_consume(state.character, "占卜家", 8)
    assert ok  # 达标提示低风险


def test_drink_potion_ok_gives_bonus_and_madness():
    import random

    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 9
    state.character.spirituality = 60  # 远超门槛 → 绝大多数种子平稳
    sp0 = state.character.spirituality

    # 灵性达标时：多数种子平稳（仍保留极低失控可能——原著永远有风险）
    ok_count = 0
    for seed in range(20):
        result = drink_potion(state.character, "占卜家", 8, rng=random.Random(seed))
        if result["ok"]:
            ok_count += 1
    assert ok_count >= 18, f"灵性达标应 ~98% 平稳，实际 {ok_count}/20"

    # 平稳示例：属性加成生效
    result = drink_potion(state.character, "占卜家", 8, rng=random.Random(0))
    if result["ok"]:
        assert result["changes"].get("madness", 0) >= 10
        assert "序列：小丑" in result["tags"]


def test_drink_potion_low_spirit_high_risk():
    """V0.29 核心：灵性严重不足时很可能失控（反噬不进序列）。"""
    import random

    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 9
    state.character.spirituality = 3  # 远低于门槛 25

    # 统计 500 次中的失控率（规则驱动：应在 40%+ 高位）
    runaway = 0
    for seed in range(500):
        try:
            state2 = engine.new_game()
            state2.character.pathway = "占卜家"
            state2.character.sequence = 9
            state2.character.spirituality = 3
            result = drink_potion(state2.character, "占卜家", 8, rng=random.Random(seed))
            if not result["ok"]:
                runaway += 1
        except Exception:
            pass
    rate = runaway / 500
    assert rate > 0.4, f"灵性过低失控率应很高，实际 {rate:.2f}"
    assert rate < 1.0  # 不是必死（仍有幸存可能）


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
    """服食魔药事件（_potion 特效键，灵性充足）平稳晋升序列并打标签。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = 9
    state.character.spirituality = 60  # 远超门槛 25 → 平稳概率高
    state.days_lived = 62

    graph = engine.event_system.graphs["seq_advance"]
    node = graph.nodes["seq9_seer_advance"]
    # 直接应用"饮下魔药"choice（引擎内部用随机 rng）
    engine.event_system.apply_choice(graph, node, 0, state)

    # 灵性充足时平稳服食应晋升（若个别种子失控可在后续验证数值）
    assert "序列：小丑" in state.character.tags or "魔药反噬" in state.character.tags
    if "序列：小丑" in state.character.tags:
        assert state.character.sequence == 8


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