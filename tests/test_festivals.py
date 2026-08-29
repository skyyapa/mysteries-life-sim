"""V0.31 专项测试：廷根岁时节令（节日事件）。"""

from life_sim.engine import WorldEngine


def _at_date(engine, state, month, day, days_lived):
    """把世界时间拨到指定月日。"""
    state.date.month = month
    state.date.day = day
    state.days_lived = max(days_lived, state.days_lived)


def test_festival_visible_on_its_date():
    """节日当天，对应节点应可触发（日历条件命中）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    _at_date(engine, state, 3, 1, 40)  # 万象节

    avail = engine.event_system.available_nodes(state)
    festival_ids = {n.id for g, n in avail if g.id == "festival_days"}
    assert "festival_wake" in festival_ids


def test_festival_hidden_other_days():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    _at_date(engine, state, 3, 2, 41)  # 次日

    avail = engine.event_system.available_nodes(state)
    festival_ids = {n.id for g, n in avail if g.id == "festival_days"}
    assert "festival_wake" not in festival_ids


def test_all_four_festivals_exist():
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["festival_days"]
    assert set(graph.nodes) == {
        "festival_wake",
        "festival_longnight",
        "festival_harvest",
        "festival_year_end",
    }


def test_calendar_conditions_require_exact_date():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    node = engine.event_system.graphs["festival_days"].nodes["festival_longnight"]

    state.date.month, state.date.day = 7, 29
    assert not engine.event_system.conditions_met(node.conditions, state)
    state.date.month, state.date.day = 7, 30
    assert engine.event_system.conditions_met(node.conditions, state)


def test_year_run_hits_all_festivals():
    """一年模拟应触发全部 4 个节日（每个至少一次）。"""
    engine = WorldEngine(seed=3)
    state = engine.new_game()
    seen: set[str] = set()
    for _ in range(365):
        engine.tick(state, days=1)
        avail = engine.event_system.available_nodes(state)
        for g, n in avail:
            if g.id == "festival_days":
                seen.add(n.id)
    assert seen >= {"festival_wake", "festival_longnight", "festival_harvest", "festival_year_end"}, (
        f"一年内应遇到全部节日，缺: {set(['festival_wake','festival_longnight','festival_harvest','festival_year_end']) - seen}"
    )


def test_festival_cooldown_allows_year_repeat():
    """cooldown 360：跨年可以再遇同节日（无常驻 once）。"""
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["festival_days"]
    node = graph.nodes["festival_wake"]
    assert node.cooldown == 360
    assert node.once_tag is None


def test_festival_is_one_time_per_day_by_calendar():
    """同一天只有一个节日节点可触（日历排他）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    _at_date(engine, state, 3, 1, 40)
    avail = engine.event_system.available_nodes(state)
    festival = [n for g, n in avail if g.id == "festival_days"]
    assert len(festival) == 1  # 只有万象节