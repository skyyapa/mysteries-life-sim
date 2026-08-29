"""calendar 日历条件机制测试（引擎能力保留，不绑定任何编造节日名）。

用途：未来若接入原著真实的教会圣日/纪念日，calendar {month,day} 直接可用。
"""

from life_sim.engine import WorldEngine
from life_sim.event_system import EventGraph, EventNode, EventSystem


def test_calendar_condition_exact_date():
    """指定月日命中才满足。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="g",
        nodes={
            "start": EventNode(id="start", text="占位", chance=0),
            "onday": EventNode(
                id="onday", text="当日", chance=50,
                conditions={"calendar": {"month": 3, "day": 1}},
            ),
        },
        edges=[],
        start_node="start",
    )
    es = EventSystem([graph])

    state.date.month, state.date.day = 3, 1
    assert es.conditions_met(graph.nodes["onday"].conditions, state)

    state.date.month, state.date.day = 3, 2
    assert not es.conditions_met(graph.nodes["onday"].conditions, state)

    state.date.month, state.date.day = 4, 1
    assert not es.conditions_met(graph.nodes["onday"].conditions, state)


def test_calendar_normalized_from_data():
    """数据里 calendar 字段被 normalize 成 conditions.calendar。"""
    engine = WorldEngine(seed=1)
    data = {"id": "n1", "text": "x", "calendar": {"month": 7, "day": 30}}
    graph = EventGraph(
        id="g2",
        nodes={"start": EventNode(id="start", text="占", chance=0)},
        edges=[],
        start_node="start",
    )
    # 直接测 normalize_conditions 输出
    from life_sim.event_system import normalize_conditions

    cond = normalize_conditions(data)
    assert cond.get("calendar") == {"month": 7, "day": 30}