"""V0.23 专项测试：一年人生总结。"""

from life_sim.engine import WorldEngine
from life_sim.summary import summarize_life


def test_summary_structure():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=365)

    report = summarize_life(state)
    assert "character" in report
    assert "people" in report
    assert "experiences" in report
    assert "pathway_line" in report
    assert "one_liner" in report
    assert "city_echoes" in report
    assert report["days_lived"] == 365


def test_summary_character_info():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"
    engine.tick(state, days=30)

    report = summarize_life(state)
    assert report["character"]["name"] == state.character.name
    assert report["mystery_stats"]["madness"] == state.character.madness


def test_pathway_line_mentions_pathway():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.pathway = "占卜家"

    report = summarize_life(state)
    assert "占卜家" in report["pathway_line"]


def test_no_pathway_line_is_plain():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    assert state.character.pathway is None

    report = summarize_life(state)
    assert "普通人" in report["pathway_line"]


def test_madness_stage_mapping():
    from life_sim.summary import _madness_stage

    assert _madness_stage(10) == "平稳"
    assert _madness_stage(35) == "恍惚"
    assert _madness_stage(60) == "不安"
    assert _madness_stage(90) == "濒危"


def test_city_echoes_present_after_year():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.economy["pressure"] = 90
    engine.tick(state, days=370)

    report = summarize_life(state)
    if state.world.bulletin:
        assert report["city_echoes"], "有公告时应能采样到城市回声"


def test_top_contacts_sorted_by_friendship():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    toby = state.npcs["toby_newsboy"]
    tom.relationship["friendship"] = 50
    toby.relationship["friendship"] = 10

    report = summarize_life(state)
    people = report["people"]
    assert len(people) >= 2
    assert people[0]["name"] == tom.name  # 友好度最高排第一


def test_one_liner_mentions_money_state():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.money = 500

    report = summarize_life(state)
    assert "积蓄" in report["one_liner"]


def test_summary_roundtrip_consistent():
    """总结是基于导入数据的纯函数：同一状态两次调用结果一致。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=60)

    r1 = summarize_life(state)
    r2 = summarize_life(state)
    assert r1["one_liner"] == r2["one_liner"]
    assert r1["pathway_line"] == r2["pathway_line"]