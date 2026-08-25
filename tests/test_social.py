"""社交层次测试：信任分层、接触门槛、信任效果。"""

from life_sim.engine import WorldEngine
from life_sim.event_system import get_relationship_tier, EventGraph, EventNode, EventSystem
from life_sim.save import load_game, save_game


def test_npcs_have_initial_trust():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    # 莎伦太太 18 → 熟人；托比 12 → 生面孔
    assert state.npcs["sha_ren_neighbor"].trust == 18
    assert state.npcs["toby_newsboy"].trust == 12
    assert state.npcs["tom_tavern"].trust == 10


def test_relationship_tiers():
    assert get_relationship_tier(5) == "生面孔"
    assert get_relationship_tier(20) == "熟人"
    assert get_relationship_tier(45) == "朋友"
    assert get_relationship_tier(65) == "密友"
    assert get_relationship_tier(85) == "挚友"


def test_trust_condition_gates_by_threshold():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system

    friend_event = event_system.graphs["ordinary_life"].nodes["ordinary_friend_errand"]
    confession = event_system.graphs["ordinary_life"].nodes["ordinary_confession"]
    state.days_lived = 30

    # 莎伦太太信任 18，未达 40 → 朋友的私事不可触发
    assert not event_system.conditions_met(friend_event.conditions, state)
    state.npcs["sha_ren_neighbor"].trust = 40
    assert event_system.conditions_met(friend_event.conditions, state)

    # 未达 70 → 深夜倾吐不可触发
    assert not event_system.conditions_met(confession.conditions, state)
    state.npcs["sha_ren_neighbor"].trust = 70
    assert event_system.conditions_met(confession.conditions, state)


def test_trust_effects_apply_to_npc():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="trust_test",
        nodes={
            "start": EventNode(
                id="start",
                text="信任变化",
                trust_effects={"sha_ren_neighbor": 5},
            )
        },
        edges=[],
        start_node="start",
    )
    es = EventSystem([graph])
    before = state.npcs["sha_ren_neighbor"].trust

    es.apply(graph, graph.nodes["start"], state)

    assert state.npcs["sha_ren_neighbor"].trust == before + 5


def test_trust_never_exceeds_100():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.npcs["sha_ren_neighbor"].trust = 99
    graph = EventGraph(
        id="trust_cap",
        nodes={"start": EventNode(id="start", text="信任封顶", trust_effects={"sha_ren_neighbor": 5})},
        edges=[],
        start_node="start",
    )
    es = EventSystem([graph])

    es.apply(graph, graph.nodes["start"], state)

    assert state.npcs["sha_ren_neighbor"].trust == 100


def test_trust_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.npcs["erin_doctor"].trust = 55

    save_game(state, "trust.json")
    loaded = load_game("trust.json")

    assert loaded.npcs["erin_doctor"].trust == 55


def test_social_graph_has_tier_events():
    engine = WorldEngine(seed=1)
    ordinary = engine.event_system.graphs["ordinary_life"]
    node_ids = set(ordinary.nodes)

    assert "ordinary_friend_errand" in node_ids
    assert "ordinary_confession" in node_ids


def test_broad_social_caps_at_friend():
    """泛社交（无深交对象）把联系人信任最多推到 40（朋友），不能再高。"""
    engine = WorldEngine(seed=5)
    state = engine.new_game()
    # 把莎伦太太推到 39
    state.npcs["sha_ren_neighbor"].trust = 39

    for _ in range(5):
        engine.process_action(state, "social")

    assert state.npcs["sha_ren_neighbor"].trust == 40


def test_focused_social_breaks_beyond_friend():
    """选中深交对象后，社交可突破 40 继续上升。"""
    engine = WorldEngine(seed=5)
    state = engine.new_game()
    state.npcs["sha_ren_neighbor"].trust = 39
    engine.set_focused_contact(state, "sha_ren_neighbor")

    engine.process_action(state, "social")

    assert state.npcs["sha_ren_neighbor"].trust == 42


def test_focused_contact_required_for_deep_ties():
    """40+ 是分水岭：没有深交对象时永远停在 40。"""
    engine = WorldEngine(seed=7)
    state = engine.new_game()
    state.npcs["erin_doctor"].trust = 40

    for _ in range(10):
        engine.process_action(state, "social")

    assert state.npcs["erin_doctor"].trust == 40
    assert state.focused_contact is None


def test_focus_toggle_and_validation():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    assert engine.set_focused_contact(state, "erin_doctor") is True
    assert state.focused_contact == "erin_doctor"

    assert engine.set_focused_contact(state, "不存在的NPC") is False
    assert engine.set_focused_contact(state, None) is True
    assert state.focused_contact is None


def test_focused_social_reaches_close_friend():
    """持续深交能把信任推到挚友（80+）。"""
    engine = WorldEngine(seed=3)
    state = engine.new_game()
    state.npcs["erin_doctor"].trust = 70
    engine.set_focused_contact(state, "erin_doctor")

    for _ in range(10):
        engine.process_action(state, "social")

    assert state.npcs["erin_doctor"].trust >= 80


def test_focused_contact_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.focused_contact = "erin_doctor"

    save_game(state, "focus.json")
    loaded = load_game("focus.json")

    assert loaded.focused_contact == "erin_doctor"