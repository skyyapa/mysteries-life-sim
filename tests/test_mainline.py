"""主线剧情 + 非凡代价测试。"""

from life_sim.engine import WorldEngine
from life_sim.save import load_game, save_game


def test_madness_starts_zero():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    assert state.character.madness == 0
    assert "madness" in state.character.to_dict()


def test_madness_rises_with_corruption_and_stress():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.corruption = 40
    state.character.stress = 80
    state.character.spirituality = 5

    for _ in range(10):
        engine.update_madness(state)

    # 污染 40 → 每日 +2；压力 >60 → +0.3；无灵性锚 → 十天后约 23
    assert 15 <= state.character.madness <= 30


def test_madness_slowed_by_spirituality_anchor():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.corruption = 40
    state.character.stress = 80
    state.character.spirituality = 70

    state.character.madness = 50
    for _ in range(10):
        engine.update_madness(state)

    # 强锚（≥60）每日 -0.5，污染+2 - 0.5 = +1.5/天 → 缓慢上升
    assert 55 <= state.character.madness <= 70


def test_madness_clamped_to_100():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.madness = 98
    state.character.corruption = 100
    state.character.stress = 100

    engine.update_madness(state)

    assert state.character.madness == 100


def test_madness_never_drops_below_zero():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.madness = 1
    state.character.corruption = 0
    state.character.stress = 20
    state.character.spirituality = 100

    for _ in range(10):
        engine.update_madness(state)

    assert state.character.madness == 0


def test_madness_stage_labels():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    state.character.madness = 0
    assert engine.madness_stage(state) == "平稳"

    state.character.madness = 30
    assert engine.madness_stage(state) == "恍惚"

    state.character.madness = 55
    assert engine.madness_stage(state) == "不安"

    state.character.madness = 80
    assert engine.madness_stage(state) == "濒危"


def test_mainline_graph_structure():
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["hidden_current"]

    assert set(graph.nodes) == {
        "start",
        "second_errand",
        "church_voice",
        "losing_control",
        "truth_choice",
    }
    edges = {(e.from_node, e.to_node) for e in graph.edges}
    assert edges == {
        ("start", "second_errand"),
        ("second_errand", "church_voice"),
        ("church_voice", "losing_control"),
        ("losing_control", "truth_choice"),
    }


def test_mainline_requires_beyonder_entry():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system
    second = event_system.graphs["hidden_current"].nodes["second_errand"]

    state.days_lived = 35
    # 未初涉非凡 → 不可触发
    assert not event_system.conditions_met(second.conditions, state)
    state.character.tags.append("初涉非凡")
    assert event_system.conditions_met(second.conditions, state)


def test_losing_control_requires_madness_40():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system
    losing = event_system.graphs["hidden_current"].nodes["losing_control"]

    state.days_lived = 45
    state.character.tags.append("初涉非凡")
    state.clues.append("second_errand_clue")
    state.character.madness = 39
    assert not event_system.conditions_met(losing.conditions, state)

    state.character.madness = 40
    assert event_system.conditions_met(losing.conditions, state)


def test_mainline_full_reach():
    """主线链完整推进：初涉非凡 → 第二委托 → 教会声音 → 失控 → 真相。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system
    graph = event_system.graphs["hidden_current"]

    # 前置条件
    state.character.tags.append("初涉非凡")
    state.days_lived = 50
    state.character.madness = 50
    state.clues.append("second_errand_clue")
    state.clues.append("church_coin")

    # start（占位）→ second_errand
    event_system.apply(graph, graph.nodes["start"], state)
    assert state.event_nodes["hidden_current"] == "second_errand"

    second = graph.nodes["second_errand"]
    assert event_system.conditions_met(second.conditions, state)
    event_system.apply(graph, second, state)
    assert "完成第二件委托" in state.character.tags
    assert state.event_nodes["hidden_current"] == "church_voice"

    church = graph.nodes["church_voice"]
    assert event_system.conditions_met(church.conditions, state)
    event_system.apply(graph, church, state)
    assert state.event_nodes["hidden_current"] == "losing_control"

    losing = graph.nodes["losing_control"]
    assert event_system.conditions_met(losing.conditions, state)
    event_system.apply(graph, losing, state)
    assert state.event_nodes["hidden_current"] == "truth_choice"

    truth = graph.nodes["truth_choice"]
    assert event_system.conditions_met(truth.conditions, state)
    # 终局有三个出口
    assert {c["label"] for c in truth_data_choices(engine)} == {
        "加入组织",
        "投向教会",
        "抽身退回",
    }


def truth_data_choices(engine) -> list:
    """读取原始数据的终局选项（choices 未进引擎，直接查 JSON）。"""
    import json

    with open("data/event_graphs.json", encoding="utf-8") as f:
        graphs = json.load(f)
    for graph in graphs:
        if graph["id"] == "hidden_current":
            for node in graph["nodes"]:
                if node["id"] == "truth_choice":
                    return node["choices"]
    return []


def test_madness_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.madness = 66

    save_game(state, "madness.json")
    loaded = load_game("madness.json")

    assert loaded.character.madness == 66