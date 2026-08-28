"""V0.15.6 专项测试：Event Hooks + Debug 面板。"""

import pytest

from life_sim.engine import WorldEngine
from life_sim.npc.events import (
    EV_NPC_ABSENT,
    EV_NPC_ARRIVED,
    EV_NPC_INTERACTION,
    EV_NPC_MISSING,
    EV_NPC_SICK,
    EV_NPC_WORKED,
    WorldEvent,
    WorldEventBus,
    reset_bus,
)


@pytest.fixture(autouse=True)
def fresh_bus():
    reset_bus()
    yield
    reset_bus()


def test_bus_publish_and_history():
    bus = WorldEventBus()
    bus.publish(WorldEvent(kind="X", npc_id="a", day=1))
    bus.publish(WorldEvent(kind="Y", npc_id="b", day=2))

    assert len(bus.history()) == 2
    assert len(bus.history(kind="X")) == 1


def test_bus_subscribe():
    bus = WorldEventBus()
    seen = []
    bus.subscribe("NPC_SICK", lambda e: seen.append(e))
    bus.publish(WorldEvent(kind="NPC_SICK", npc_id="t", day=3))

    assert len(seen) == 1
    assert seen[0].npc_id == "t"


def test_bus_recent_by_npc():
    bus = WorldEventBus()
    for day in range(1, 6):
        bus.publish(WorldEvent(kind="NPC_WORKED", npc_id="t", day=day))
    bus.publish(WorldEvent(kind="NPC_WORKED", npc_id="o", day=6))

    recent = bus.recent("t")
    assert len(recent) == 5
    assert all(e.npc_id == "t" for e in recent)


def test_work_emits_npc_worked():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    from life_sim.npc.effects import apply_result, build_result

    tom = state.npcs["tom_tavern"]
    result = build_result(tom, "work", prev_location=tom.home,
                          loc_type_map={"work": "workplace"}, loc_name_map={})
    apply_result(state, tom, result, bus=engine.event_bus)

    kinds = [e.kind for e in engine.event_bus.history()]
    assert EV_NPC_WORKED in kinds


def test_missing_emits_npc_missing():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.npc_system.disappear(state, "erin_doctor")

    kinds = [e.kind for e in engine.event_bus.history()]
    assert EV_NPC_MISSING in kinds
    missing = [e for e in engine.event_bus.history(kind=EV_NPC_MISSING)]
    assert missing[0].npc_id == "erin_doctor"


def test_sick_absence_emits_absent():
    """生病 → 缺勤 → NPC_ABSENT_FROM_WORK。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    alfred = state.npcs["alfred_factory_worker"]  # factory_worker 模板（工作日 7:00 work）
    alfred.state.sick = True
    alfred.needs.rest = 95
    alfred.state.fatigue = 90

    engine.tick(state, days=1)

    kinds = [e.kind for e in engine.event_bus.history()]
    assert EV_NPC_ABSENT in kinds


def test_interaction_emits_interaction_event():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    toby = state.npcs["toby_newsboy"]
    tom.location = "市场区"
    toby.location = "市场区"
    tom.needs.social = 70
    toby.needs.social = 70
    tom.social_links[toby.id] = {"familiarity": 20, "affection": 5, "trust": 4, "fear": 0}
    toby.social_links[tom.id] = {"familiarity": 20, "affection": 5, "trust": 4, "fear": 0}

    engine.tick(state, days=1)

    kinds = [e.kind for e in engine.event_bus.history()]
    assert EV_NPC_INTERACTION in kinds


def test_detected_anomaly_reason_thinks():
    """缺勤事件带原因（生病/疲劳等），可供调试面板展示。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    alfred = state.npcs["alfred_factory_worker"]
    alfred.state.sick = True

    engine.tick(state, days=1)

    absent = [e for e in engine.event_bus.history(kind=EV_NPC_ABSENT)]
    if absent:
        assert absent[0].reason  # 有原因
        assert "病" in absent[0].reason or "疲劳" in absent[0].reason or "睡眠" in absent[0].reason


def test_event_log_capped():
    bus = WorldEventBus()
    for day in range(600):
        bus.publish(WorldEvent(kind="X", npc_id="t", day=day))
    assert len(bus.history()) <= 500