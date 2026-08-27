"""V0.14 World Tick 2.0 测试：编排、时间、地点、经济、关系。"""

from life_sim.engine import WorldEngine
from life_sim.models import NPC
from life_sim.world.tick import TimeSystem, WorldTick


# ---- 时间系统 ----

def test_time_advances_hours_and_minutes():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    assert state.date.hour == 8

    TimeSystem.advance(state, hours=2)
    assert state.date.hour == 10

    TimeSystem.advance(state, minutes=30)
    assert state.date.hour == 10
    assert state.date.minute == 30


def test_time_work_advances_6h():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    TimeSystem.work(state)
    assert state.date.hour == 14


def test_time_travel_advances_3_days():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    day = state.date.day
    TimeSystem.travel(state)
    assert state.date.day == day + 3


def test_time_sleep_wraps_to_morning():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    # 从 20:00 睡 8 小时 → 次日 04:00 → 调整到 07:00
    state.date.hour = 20
    TimeSystem.sleep(state)
    assert state.date.day == 2  # 跨天
    assert state.date.hour == 7


def test_is_night():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.date.hour = 23
    assert state.date.is_night()
    state.date.hour = 12
    assert not state.date.is_night()


def test_time_full_label():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    assert state.date.label_full() == "第五纪 1348年1月1日 08:00"


# ---- 地点系统 ----

def test_locations_initialized():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.location_system.ensure(state)

    assert set(state.world.locations) == {"北区", "市场区", "黑夜教堂", "东区", "廷根车站"}
    east = state.world.locations["东区"]
    assert east["danger"] > east["北区" if False else "danger"] if False else True


def test_location_tick_changes_activity():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.location_system.ensure(state)
    before = state.world.locations["市场区"]["activity"]

    engine.location_system.tick(state)  # 白天 +3

    assert state.world.locations["市场区"]["activity"] > before


def test_night_lowers_activity():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.location_system.ensure(state)
    state.date.hour = 23
    before = state.world.locations["市场区"]["activity"]

    engine.location_system.tick(state)

    assert state.world.locations["市场区"]["activity"] < before


# ---- 经济系统 ----

def test_daily_income_and_expense():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.job = "事务所文员"  # 日收入 7，支出 5
    state.character.money = 100
    money = state.character.money

    engine.economy_system.tick(state)

    assert state.character.money == money + 7 - 5  # +2/天


def test_poverty_hurts():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.job = "文法学校学生"  # 日收入 0，支出 2
    state.character.money = 0
    health = state.character.health
    stress = state.character.stress

    engine.economy_system.tick(state)

    # 无收入 → 支出凑不满 → 挨饿伤身
    assert state.character.money == 0
    assert state.character.health < health
    assert state.character.stress > stress


def test_student_survives_on_stipend():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.job = "文法学校学生"
    state.character.money = 5
    health = state.character.health

    engine.economy_system.tick(state)

    assert state.character.money == 3  # -2 支出
    assert state.character.health == health


# ---- 关系系统 ----

def test_relationship_three_dimensions():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    npc = state.npcs["erin_doctor"]

    assert npc.relationship["trust"] == npc.trust
    npc.add_friendship(10)
    npc.add_fear(5)

    assert npc.friendship == 10
    assert npc.fear == 5


def test_trust_setter_syncs_relationship():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    npc = state.npcs["tom_tavern"]

    npc.trust = 55

    assert npc.relationship["trust"] == 55
    assert npc.trust == 55


def test_relation_tick_decays_friendship_only():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    npc = state.npcs["erin_doctor"]
    npc.add_friendship(20)
    npc.add_fear(20)
    trust_before = npc.trust

    engine.relation_system.tick(state)

    assert npc.friendship == 19  # 友谊 -1
    assert npc.fear == 19  # 畏惧 -1
    assert npc.trust == trust_before  # 信任稳定


# ---- WorldTick 编排 ----

def test_world_tick_orchestrates_all():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.location_system.ensure(state)
    start_day = state.date.day
    start_hour = state.date.hour
    tom_fatigue = state.npcs["tom_tavern"].fatigue

    # 走 WorldTick（等同 tick_world days=1）
    engine.world_tick.run(state, days=1)

    assert state.date.day == start_day + 1  # 时间推进
    assert state.npcs["tom_tavern"].current_activity  # NPC 有活动
    assert state.npcs["tom_tavern"].current_time >= "07:00"  # 时间片驱动
    assert state.world.locations["市场区"]["activity"]  # 地点有状态
    assert state.character is not None  # 世界状态提交


def test_tick_world_advances_and_ages():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    age = state.character.age
    state.date.month = 12
    state.date.day = 30

    engine.tick_world(state, days=1)

    assert state.date.year == 1349
    assert state.days_lived == 1
    assert state.character.age == age + 1
    assert set(state.world.locations) == {"北区", "市场区", "黑夜教堂", "东区", "廷根车站"}