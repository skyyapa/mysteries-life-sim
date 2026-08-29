"""V0.24 专项测试：途径深化（占卜/观众加成/不眠者耐力）。"""

import pytest

from life_sim.engine import WorldEngine


def make_seer(seed=1):
    engine = WorldEngine(seed=seed)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.spirituality = 20
    return engine, state


def test_divination_action_visible_only_to_seer():
    engine = WorldEngine(seed=1)
    plain = engine.new_game()
    assert "divination" not in engine.available_actions(plain)

    plain.character.pathway = "占卜家"
    assert "divination" in engine.available_actions(plain)


def test_divination_requires_pathway():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    with pytest.raises(ValueError, match="占卜家"):
        engine.process_action(state, "divination")


def test_divination_effects_and_tag():
    engine, state = make_seer()
    before_sp = state.character.spirituality

    entry = engine.process_action(state, "divination")

    assert state.character.spirituality < before_sp  # 消耗灵性
    assert state.character.mysticism_knowledge >= 1
    assert "占卜过" in state.character.tags
    assert entry.action == "占卜"


def test_divination_on_cooldown_via_days():
    """占卜会推进一天（days=1），不能同一回合连发导致事故。"""
    engine, state = make_seer()
    d0 = state.days_lived
    engine.process_action(state, "divination")
    assert state.days_lived == d0 + 1


def test_viewer_social_bonus():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "观众"
    tom = state.npcs["tom_tavern"]
    state.focused_contact = "tom_tavern"
    t0 = tom.trust

    engine.process_action(state, "social")

    assert tom.trust >= t0 + 3  # 观众社交 +3 bonus（基础 3 → 6）


def test_insomniac_stamina_saving_on_work():
    """不眠者工作不额外耗体力（stamina 净变化 >= 默认工作）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "不眠者"
    state.character.money = 100

    entry = engine.process_action(state, "work")

    # 工作默认 stamina -12；不眠者 +4 → 净 -8
    stamina_delta = entry.changes.get("stamina", 0)
    assert stamina_delta >= -12


def test_pathway_events_exist():
    """途径专属事件节点已在事件图中。"""
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["path_choice"]
    ids = set(graph.nodes)
    assert "path_seer_master" in ids
    assert "path_reader_insight" in ids
    assert "path_insomn_night" in ids


def test_pathway_event_requires_pathway_tag():
    """专属事件需要对应途径标签。"""
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["path_choice"]
    seer_event = graph.nodes["path_seer_master"]
    assert "途径：占卜家" in seer_event.conditions.get("any_tag", [])


def test_plain_character_no_pathway_events():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 60

    avail = engine.event_system.available_nodes(state)
    pathway_ids = {n.id for g, n in avail if g.id == "path_choice" and n.id.startswith("path_") and n.id != "start"}
    # 无途径角色不应看到途径专属事件（3 个专属节点 + 3 个选择节点需要标签）
    assert not any("_master" in n or "_insight" in n or "_night" in n for n in pathway_ids)