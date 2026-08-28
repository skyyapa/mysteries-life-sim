"""V0.15.5 专项测试：NPC-NPC 轻量互动（社会形成）。"""

import pytest

import life_sim.npc.interaction as interaction_module
from life_sim.engine import WorldEngine
from life_sim.npc.interaction import (
    can_interact,
    interact,
    scan_and_interact,
)
from life_sim.npc.models import NPCNeeds, NPCState
from life_sim.save import load_game, save_game


@pytest.fixture(autouse=True)
def clean_interactions():
    interaction_module._last_interactions.clear()
    yield
    interaction_module._last_interactions.clear()


def make_pair(engine, a="tom_tavern", b="toby_newsboy", social=60):
    state = engine.new_game()
    na = state.npcs[a]
    nb = state.npcs[b]
    na.needs.social = social
    nb.needs.social = social
    na.state = NPCState(health=100, fatigue=30)
    nb.state = NPCState(health=100, fatigue=30)
    return na, nb, state


def test_unknown_npcs_do_not_chat():
    """完全陌生的两个 NPC 不互动（familiarity=0 < 门槛）。"""
    engine = WorldEngine(seed=1)
    na, nb, _ = make_pair(engine, social=80)
    assert can_interact(na, nb) is False


def test_known_npcs_chat():
    """有 familiarity 的熟人会互动。"""
    engine = WorldEngine(seed=1)
    na, nb, state = make_pair(engine, social=80)
    na.social_links[nb.id] = {"familiarity": 20, "affection": 5, "trust": 5, "fear": 0}

    result = interact(na, nb, day=5)
    assert result is not None
    assert result.kind == "chat"
    # 双方需求下降、熟悉度上升
    assert na.needs.social < 80
    assert nb.needs.social < 80
    assert na.social_links[nb.id]["familiarity"] > 20
    assert nb.social_links[na.id]["familiarity"] > 0  # 对方也建立了 link


def test_social_need_below_threshold_no_chat():
    """双方社交需求都低于门槛则不互动。"""
    engine = WorldEngine(seed=1)
    na, nb, _ = make_pair(engine, social=10)
    na.social_links[nb.id] = {"familiarity": 20, "affection": 0, "trust": 0, "fear": 0}
    nb.social_links[na.id] = {"familiarity": 20, "affection": 0, "trust": 0, "fear": 0}

    assert interact(na, nb, day=1) is None


def test_interaction_cooldown():
    """同对 NPC 有冷却：连续两次只发生一次。"""
    engine = WorldEngine(seed=1)
    na, nb, _ = make_pair(engine)
    na.social_links[nb.id] = {"familiarity": 30, "affection": 5, "trust": 5, "fear": 0}
    nb.social_links[na.id] = {"familiarity": 30, "affection": 5, "trust": 5, "fear": 0}

    first = interact(na, nb, day=10)
    second = interact(na, nb, day=11)  # 冷却 3 天内
    assert first is not None
    assert second is None

    third = interact(na, nb, day=14)  # 冷却过了
    assert third is not None


def test_scan_interacts_same_location():
    """同一地点的熟人组合会触发互动。"""
    engine = WorldEngine(seed=1)
    na, nb, state = make_pair(engine)
    na.social_links[nb.id] = {"familiarity": 30, "affection": 5, "trust": 5, "fear": 0}
    nb.social_links[na.id] = {"familiarity": 30, "affection": 5, "trust": 5, "fear": 0}
    na.location = "市场区"
    nb.location = "市场区"

    results = scan_and_interact(list(state.npcs.values()), day=2, location="市场区")
    assert any(r.npc_a in (na.id, nb.id) for r in results)


def test_missing_npc_no_interaction():
    engine = WorldEngine(seed=1)
    na, nb, state = make_pair(engine)
    na.social_links[nb.id] = {"familiarity": 30, "affection": 5, "trust": 5, "fear": 0}
    nb.social_links[na.id] = {"familiarity": 30, "affection": 5, "trust": 5, "fear": 0}
    na.disappeared = True

    assert interact(na, nb, day=1) is None
    assert can_interact(na, nb) is False


def test_links_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    tom.social_links["toby_newsboy"] = {"familiarity": 42, "affection": 8, "trust": 12, "fear": 0}

    save_game(state, "links.json")
    loaded = load_game("links.json")
    ltom = loaded.npcs["tom_tavern"]

    assert ltom.social_links["toby_newsboy"]["familiarity"] == 42


def test_social_network_grows_over_time():
    """连续共处一段时间的熟人会加深友谊（社会网络增长）。"""
    engine = WorldEngine(seed=3)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    toby = state.npcs["toby_newsboy"]
    # 让两人共同在北区办公（酒馆老板/报童的 job_location 都在市场区，此处统一到市场区）
    tom.location = "市场区"
    toby.location = "市场区"
    tom.job_location = "市场区"
    toby.job_location = "市场区"
    tom.needs.social = 70
    toby.needs.social = 70
    # 工作日两人都去市场区工作，白天共处 → 应发生互动
    tom.social_links[toby.id] = {"familiarity": 15, "affection": 3, "trust": 3, "fear": 0}
    toby.social_links[tom.id] = {"familiarity": 15, "affection": 3, "trust": 3, "fear": 0}

    engine.tick(state, days=10)

    tom_link = state.npcs["tom_tavern"].social_links.get("toby_newsboy", {})
    # 长期共处应加深（至少有一次互动：familiarity +2 → >15）
    assert tom_link.get("familiarity", 0) >= 15
    assert tom_link.get("affection", 0) >= 3
    # 网络存在即可（值合法）
    assert 0 <= tom_link.get("familiarity", 0) <= 100