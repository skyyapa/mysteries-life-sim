"""事件时效性测试：窗口期、过期失效、错过痕迹。"""

from life_sim.engine import WorldEngine


def test_abnormal_events_have_max_day():
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["abnormal_disappearance"]

    expected = {
        "abnormal_notice": 60,
        "abnormal_overlap": 90,
        "abnormal_symbol": 120,
        "abnormal_followed": 150,
    }
    for node_id, max_day in expected.items():
        node = graph.nodes[node_id]
        assert node.conditions.get("max_day") == max_day, f"{node_id} max_day 应为 {max_day}"


def test_abnormal_notice_expires_after_window():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system
    notice = event_system.graphs["abnormal_disappearance"].nodes["abnormal_notice"]

    # 窗口内可触发（当前节点是 start_node）
    state.days_lived = 10
    assert event_system.conditions_met(notice.conditions, state)

    # 超过窗口不可触发
    state.days_lived = 61
    assert not event_system.conditions_met(notice.conditions, state)


def test_missed_trace_logged_once():
    """错过痕迹：事件过期后写日志，且只写一次。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    # 从未见过失踪启事，直接跳到 70 天 → 应留痕
    state.days_lived = 70
    engine.update_world(state, previous_year=state.date.year)
    lengths = len(state.journal)
    assert lengths >= 1
    trace = state.journal[-1]
    assert "错过" in trace.summary or "错过" in (trace.event or "") or "撤下" in trace.summary

    # 再跳一天 → 不再重复留痕
    state.days_lived = 71
    engine.update_world(state, previous_year=state.date.year)
    assert len(state.journal) == lengths, "错过痕迹不应重复写入"


def test_triggered_event_no_trace():
    """如果玩家已触发过事件（链条已推进），过期时不留“错过”痕迹。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    # 真实触发 abnormal_notice：链条推进到 abnormal_overlap
    graph = engine.event_system.graphs["abnormal_disappearance"]
    state.character.tags.append("见过失踪启事")
    engine.event_system.apply(graph, graph.nodes["abnormal_notice"], state)
    assert state.event_nodes["abnormal_disappearance"] == "abnormal_overlap"

    state.days_lived = 70
    engine.update_world(state, previous_year=state.date.year)

    trace_entries = [e for e in state.journal if "错过" in e.summary]
    assert not any("车站" in e.summary for e in trace_entries), "已触发启事不应留错过痕迹"


def test_decision_event_has_no_max_day():
    """核心抉择事件不受时效限制（线索会凉，但抉择随时能做）。"""
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["abnormal_disappearance"]
    decision = graph.nodes["abnormal_decision"]

    assert "max_day" not in decision.conditions, "失踪案抉择不应设时限"