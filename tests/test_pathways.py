"""V0.21 专项测试：非凡途径选择。"""

from life_sim.engine import WorldEngine
from life_sim.mysticism.pathways import (
    PATHWAYS,
    apply_pathway_bonus,
    pathway_behavior_bonus,
)
from life_sim.save import load_game, save_game


def test_pathways_defined_three():
    assert set(PATHWAYS) == {"占卜家", "观众", "不眠者"}
    assert PATHWAYS["占卜家"]["id"] == "seer"
    assert PATHWAYS["观众"]["id"] == "reader"
    assert PATHWAYS["不眠者"]["id"] == "insomn"


def test_character_starts_without_pathway():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    assert state.character.pathway is None


def test_apply_pathway_bonus():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    char = state.character
    sp0 = char.spirituality

    apply_pathway_bonus(char, "占卜家")
    assert char.pathway is None  # 加成函数不改字段，只改属性
    assert char.spirituality >= sp0 + 4  # 占卜家 +5 spirituality


def test_behavior_bonus_by_pathway():
    assert pathway_behavior_bonus("占卜家", "investigate") == 12
    assert pathway_behavior_bonus("观众", "socialize") == 10
    assert pathway_behavior_bonus("不眠者", "work") == 6
    assert pathway_behavior_bonus(None, "work") == 0


def test_event_set_pathway_via_effect():
    """途径选择事件的效果键 _pathway 设置角色途径。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.tags.append("加入神秘组织")
    state.days_lived = 55

    graph = engine.event_system.graphs["path_choice"]
    node = graph.nodes["path_seer"]
    assert graph.is_pool

    engine.event_system.apply(graph, node, state)

    assert state.character.pathway == "占卜家"
    assert "途径：占卜家" in state.character.tags
    assert state.character.spirituality >= 5


def test_pathway_saved_and_loaded(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "观众"

    save_game(state, "pathway.json")
    loaded = load_game("pathway.json")

    assert loaded.character.pathway == "观众"


def test_old_save_without_pathway_loads():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    data = state.to_dict()
    data["character"].pop("pathway", None)

    import json
    import tempfile
    import pathlib

    import life_sim.save as save_module

    tmp = pathlib.Path(tempfile.mkdtemp())
    save_module.SAVE_DIR = tmp
    path = tmp / "old.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    loaded = save_module.load_game("old.json")
    assert loaded.character.pathway is None  # 旧存档默认无途径


def test_seer_pathway_boosts_investigate_score():
    """占卜家的 investigate 评分加成应通过 behavior._goal_weight 生效。"""
    engine = WorldEngine(seed=1)
    from life_sim.npc.behavior import _goal_weight

    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    # NPC 通常无 pathway；模拟有途径的角色（临时加字段）
    tom.pathway = "占卜家"
    bonus = _goal_weight(tom, "investigate")
    assert bonus >= 12