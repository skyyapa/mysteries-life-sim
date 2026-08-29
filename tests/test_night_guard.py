"""V0.32 专项测试：值夜者线（贴合原著：黑夜教会外勤武装）。"""

from life_sim.engine import WorldEngine


def test_dunn_smith_in_world():
    """邓恩·史密斯（值夜者队长）存在于世界且驻圣赛琳娜教堂。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    dunn = state.npcs["dunn_smith"]
    assert dunn.name == "邓恩·史密斯"
    assert dunn.location == "圣赛琳娜教堂"


def test_guard_line_needs_church_tag():
    """值夜者线入口需教会线人/向教会举报标签。"""
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["night_guard_line"]
    start = graph.nodes["meet_dunn"]
    assert "成为教会线人" in start.conditions.get("any_tag", []) or \
        "向教会举报" in start.conditions.get("any_tag", [])


def test_guard_line_progression():
    """完整推进：见队长→受托夜巡→收容异常→结缘。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 48
    state.character.tags.append("称为教会线人")  # noop guard
    state.character.tags.append("成为教会线人")

    graph = engine.event_system.graphs["night_guard_line"]
    node = graph.nodes["meet_dunn"]
    assert engine.event_system.conditions_met(node.conditions, state)

    # 选"如实相告" → 受托夜巡
    engine.event_system.apply_choice(graph, node, 0, state)
    assert state.character.tags.count("受托夜巡") >= 1
    assert state.npcs["dunn_smith"].trust >= 5  # meet_dunn 给了 +5 信任

    # 夜巡 → 收容
    state.days_lived = 50
    node2 = graph.nodes["night_patrol"]
    assert engine.event_system.conditions_met(node2.conditions, state)
    engine.event_system.apply_choice(graph, node2, 0, state)
    assert "随值夜者巡夜" in state.character.tags

    # 收容 → 结缘（min_day 55）
    state.days_lived = 56
    node3 = graph.nodes["contain_anomaly"]
    assert engine.event_system.conditions_met(node3.conditions, state)
    engine.event_system.apply_choice(graph, node3, 0, state)
    assert "成为值夜者" in state.character.tags or "值夜者结缘" in state.character.tags


def test_guard_line_chain_edges_exist():
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["night_guard_line"]
    edge_pairs = {(e.from_node, e.to_node) for e in graph.edges}
    assert ("start", "meet_dunn") in edge_pairs
    assert ("meet_dunn", "night_patrol") in edge_pairs
    assert ("night_patrol", "contain_anomaly") in edge_pairs
    assert ("contain_anomaly", "night_guard_end") in edge_pairs


def test_dunn_trust_from_events():
    """值夜者事件正信任会记录到邓恩。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 48
    state.character.tags.append("成为教会线人")
    graph = engine.event_system.graphs["night_guard_line"]
    engine.event_system.apply_choice(graph, graph.nodes["meet_dunn"], 0, state)

    assert state.npcs["dunn_smith"].trust >= 5
    assert state.npcs["dunn_smith"].memories.get("helped", {}).get("count", 0) >= 1