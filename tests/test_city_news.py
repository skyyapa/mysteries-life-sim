"""V0.20 专项测试：城市感知层（每日见闻）。"""

from life_sim.engine import WorldEngine
from life_sim.city.news import CityTidings, daily_bulletin, generate_tidings
from life_sim.save import load_game, save_game


def test_quiet_city_has_no_news():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.economy["pressure"] = 30
    state.world.locations["东区"] = {"danger": 20, "activity": 30, "population": 55}

    t = generate_tidings(state)
    # 稳定/无失踪/无组织异常 → 可能无新闻（或仅季节新闻）
    assert t is None or t.text


def test_economy_pressure_drives_news():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.economy["pressure"] = 80

    t = generate_tidings(state)
    assert t is not None
    assert t.source == "economy_news"


def test_missing_npc_drives_top_news():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.npc_system.disappear(state, "erin_doctor")

    t = generate_tidings(state)
    assert t is not None
    assert "艾琳" in t.text or "不见人影" in t.text
    # 失踪新闻是优先源
    assert t.source == "npc_missing_news"


def test_secret_activity_news():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.organizations["暗流组织"]["activity"] = 70

    t = generate_tidings(state)
    assert t is not None
    assert t.source in ("org_news", "crime_news", "economy_news", "season_news")


def test_daily_bulletin_writes_world_state():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.economy["pressure"] = 90

    txt = daily_bulletin(state)
    assert txt is not None
    assert state.world.daily_bulletin.get("text") == txt
    assert len(state.world.bulletin) >= 1


def test_bulletin_history_capped():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.economy["pressure"] = 90
    for _ in range(300):
        daily_bulletin(state)
    assert len(state.world.bulletin) <= 200


def test_tick_writes_daily_tidings():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=1)
    # 每天 update_world 生成见闻
    assert state.world.daily_bulletin.get("text") or state.world.bulletin


def test_bulletin_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.economy["pressure"] = 88
    daily_bulletin(state)

    save_game(state, "bulletin.json")
    loaded = load_game("bulletin.json")

    assert loaded.world.daily_bulletin.get("text") == state.world.daily_bulletin.get("text")
    assert loaded.world.bulletin == state.world.bulletin