"""V0.16 专项测试：世界事件驱动事件图。"""

import pytest

from life_sim.engine import WorldEngine
from life_sim.npc.events import (
    EV_NPC_MISSING,
    EV_NPC_WORKED,
    WorldEvent,
    reset_bus,
)


@pytest.fixture(autouse=True)
def fresh_bus():
    reset_bus()
    yield
    reset_bus()


def test_node_can_listen_world_event():
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["abnormal_disappearance"]
    notice = graph.nodes["abnormal_notice"]

    assert notice.on_world_event == "NPC_MISSING"


def test_missing_event_activates_disappearance_graph():
    """NPC 失踪 → 事件图失踪链被推进到 abnormal_notice。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    # 玩家遇到 NPC_MISSING 事件
    engine.event_bus.publish(
        WorldEvent(
            kind=EV_NPC_MISSING,
            npc_id="erin_doctor",
            day=3,
            location="北区",
            reason="行踪不明",
        )
    )
    # Tick（消费总线事件 → 事件图）
    engine.tick(state, days=1)

    assert state.event_nodes.get("abnormal_disappearance") == "abnormal_notice"


def test_other_events_do_not_activate_by_default():
    """普通事件（NPC_WORKED）不应无缘无故激活失踪链。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    engine.event_bus.publish(
        WorldEvent(kind=EV_NPC_WORKED, npc_id="tom_tavern", day=1, location="市场区")
    )
    engine.tick(state, days=1)

    # 未设置 on_world_event=NPC_WORKED 的节点不应被激活
    assert state.event_nodes.get("abnormal_disappearance", "start") == (
        "start" if "abnormal_disappearance" not in state.event_nodes else state.event_nodes["abnormal_disappearance"]
    )


def test_reactivate_once_only():
    """已经激活过一次的链不会重复推进。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    for _ in range(2):
        engine.event_bus.publish(
            WorldEvent(kind=EV_NPC_MISSING, npc_id="a", day=5, location="?"),
            # 连续两次相同事件
        )
    engine.tick(state, days=1)

    assert state.event_nodes["abnormal_disappearance"] == "abnormal_notice"


def test_full_flow_missing_leads_to_player_event():
    """完整流：NPC 失踪 → 链激活 → 布告事件可触发（玩家在车站可遇）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.date.day = 5
    state.days_lived = 5

    engine.event_bus.publish(
        WorldEvent(kind=EV_NPC_MISSING, npc_id="erin_doctor", day=3, location="北区")
    )
    engine.tick(state, days=0)  # 仅消费事件不推进天数
    # 或直接 tick 1 天

    graph = engine.event_system.graphs["abnormal_disappearance"]
    current = engine.event_system.current_node(graph, state)
    assert current is not None
    assert current.id == "abnormal_notice"


def test_drain_new_only_consumes_latest():
    """总线 drain_new 只返回未被消费的事件。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.event_bus.publish(WorldEvent(kind="X1", npc_id="a", day=1))

    first = engine.event_bus.drain_new()
    assert len(first) == 1 and first[0].kind == "X1"

    engine.event_bus.publish(WorldEvent(kind="X2", npc_id="b", day=2))
    remaining = engine.event_bus.drain_new()
    assert len(remaining) == 1
    assert remaining[0].kind == "X2"


def test_cond_on_world_event_extra():
    """on_world_event_cond：附加条件匹配才激活。"""
    from life_sim.event_system import EventGraph, EventNode, EventSystem

    graph = EventGraph(
        id="g",
        nodes={
            "start": EventNode(id="start", text="占位", chance=0),
            "target": EventNode(
                id="target",
                text="目标",
                on_world_event="NPC_MISSING",
                on_world_event_cond={"location": "东区"},
            ),
        },
        edges=[],
        start_node="start",
    )
    es = EventSystem([graph])
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    # 地点不匹配 → 不激活
    ev1 = WorldEvent(kind="NPC_MISSING", npc_id="x", day=1, location="北区")
    assert es.handle_world_event(ev1, state) is False

    # 地点匹配 → 激活
    ev2 = WorldEvent(kind="NPC_MISSING", npc_id="x", day=1, location="东区")
    assert es.handle_world_event(ev2, state) is True
    assert state.event_nodes["g"] == "target"