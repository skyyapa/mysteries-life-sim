"""时间系统测试。

第五阶段重点：
- 日期推进正确（30 天为一个月，12 个月为一年，第 5 纪 1348 年）
- 推进 100 天日期正确
- 推进一年（360 天）回到同月同日、年龄 +1
- 跨年、多年年龄计算正确
- 存档日期往返一致
"""

from life_sim.engine import WorldEngine
from life_sim.models import WorldDate


def test_world_date_advances_by_month_30_days():
    date = WorldDate(year=1348, month=1, day=1)

    date.advance_days(30)

    assert (date.year, date.month, date.day) == (1348, 2, 1)


def test_world_date_advances_across_year():
    date = WorldDate(year=1348, month=12, day=30)

    date.advance_days(2)

    assert (date.year, date.month, date.day) == (1349, 1, 2)


def test_world_date_360_days_is_exactly_one_year():
    date = WorldDate(year=1348, month=1, day=1)

    date.advance_days(360)

    assert (date.year, date.month, date.day) == (1349, 1, 1)


def test_tick_100_days_date_matches_expected():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    engine.tick(state, days=100)

    assert state.days_lived == 100
    assert (state.date.year, state.date.month, state.date.day) == (1348, 4, 11)


def test_tick_30_days_advances_one_month():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    engine.tick(state, days=30)

    assert (state.date.month, state.date.day) == (2, 1)


def test_tick_one_year_increases_age_once():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    age = state.character.age

    engine.tick(state, days=360)

    assert state.date.year == 1349
    assert state.character.age == age + 1


def test_tick_730_days_increases_age_twice():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    age = state.character.age

    engine.tick(state, days=730)

    assert state.date.year == 1350
    assert state.character.age == age + 2


def test_tick_one_year_returns_to_same_month_day():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    engine.tick(state, days=360)

    assert (state.date.month, state.date.day) == (1, 1)


def test_days_lived_matches_date_after_long_run():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=365)

    # 110 天后应为 1349 年第 5 天（365 = 360 + 5）
    assert state.days_lived == 365
    assert (state.date.year, state.date.month, state.date.day) == (1349, 1, 6)


def test_date_label_is_stable_format():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    assert state.date.label() == "第五纪 1348年1月1日"

    engine.tick(state, days=30)
    assert state.date.label() == "第五纪 1348年2月1日"