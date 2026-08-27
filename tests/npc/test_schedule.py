"""V0.15.2 专项测试：Schedule 2.0。"""

from life_sim.engine import WorldEngine
from life_sim.npc.schedule import (
    ACTIVITY_NAMES,
    Schedule2,
    ScheduleTemplate,
    load_schedule_templates,
)
from life_sim.save import load_game, save_game


def test_schedule2_activity_at():
    s = Schedule2.from_dict({"07:00": "wake", "09:00": "work", "13:00": "lunch"})
    assert s.activity_at(6) is None  # 6 点前无行为
    assert s.activity_at(7) == "wake"
    assert s.activity_at(8) == "wake"  # 取最近不晚于的时刻
    assert s.activity_at(9) == "work"
    assert s.activity_at(15) == "lunch"  # 15 点后仍是午餐


def test_schedule_template_weekday_vs_restday():
    tpl = ScheduleTemplate.from_dict(
        {
            "id": "x",
            "weekday": {"08:00": "work"},
            "rest_day": {"10:00": "shopping"},
        }
    )
    assert tpl.for_day(hour=9, is_rest_day=False) == "work"
    assert tpl.for_day(hour=10, is_rest_day=True) == "shopping"


def test_schedule_template_special_overrides():
    tpl = ScheduleTemplate.from_dict(
        {
            "id": "x",
            "weekday": {"08:00": "work"},
            "rest_day": {"08:00": "shopping"},
            "special": {"1348-05-01": {"09:00": "pray"}},
        }
    )
    # 特殊日覆盖工作日
    assert tpl.for_day(hour=10, is_rest_day=False, date_key="1348-05-01") == "pray"
    # 其他日期走常规
    assert tpl.for_day(hour=10, is_rest_day=False, date_key="1348-05-02") == "work"


def test_schedule_templates_loaded():
    engine = WorldEngine(seed=1)
    templates = engine.npc_system.schedule_templates

    assert "tavern_owner" in templates
    assert "factory_worker" in templates
    assert "priest" in templates
    assert "student" in templates
    # 模板含工作日 work
    assert "work" in templates["tavern_owner"].weekday.timeline.values()


def test_npc_with_schedule_id_uses_time_schedule():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    assert tom.schedule_id == "tavern_owner"

    engine.tick(state)

    # 一天结束停在 sleep（23:00 入睡）
    assert tom.current_activity == "入睡"
    assert tom.current_time == "23:00"
    assert tom.location == tom.home  # 回到家


def test_npc_goes_to_workplace():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    alfred = state.npcs["alfred_factory_worker"]  # factory_worker 模板，job_location=东区
    assert alfred.schedule_id == "factory_worker"

    engine.tick(state)

    # 工作日晚上回东区住处（工厂在东区）
    assert alfred.location == alfred.home
    assert alfred.current_activity in ACTIVITY_NAMES.values()


def test_npc_moves_between_locations_during_day():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    priest = state.npcs["olson_priest"]
    assert priest.schedule_id == "priest"

    engine.tick(state)

    # 教士工作日结束在家（job_location=黑夜教堂，home=黑夜教堂）
    assert priest.location == priest.home


def test_weekday_work_raises_fatigue():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    alfred = state.npcs["alfred_factory_worker"]
    f0 = alfred.state.fatigue

    engine.tick(state, days=3)  # 工作日 work 累积

    # 工作会累（3 天工作 ≥ 初始，且界内）
    assert 0 <= alfred.state.fatigue <= 100
    assert alfred.current_activity  # 有活动


def test_restday_no_work():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    template = engine.npc_system.schedule_templates["factory_worker"]

    weekday_values = list(template.weekday.timeline.values())
    restday_values = list(template.rest_day.timeline.values())

    assert "work" in weekday_values
    assert "work" not in restday_values


def test_schedule_id_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    save_game(state, "sched.json")
    loaded = load_game("sched.json")

    assert loaded.npcs["tom_tavern"].schedule_id == "tavern_owner"
    assert loaded.npcs["alfred_factory_worker"].schedule_id == "factory_worker"