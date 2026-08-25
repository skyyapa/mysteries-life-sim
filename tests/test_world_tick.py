"""World Tick 组织行动 + NPC 模拟 + Canon 导入测试。"""

import json
from pathlib import Path

from life_sim.engine import WorldEngine
from life_sim.models import NPC, NPCScheduleEntry
from life_sim.save import load_game, save_game


# ============ ① World Tick：组织行动 ============

def test_organizations_exist_by_default():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    assert "黑夜教会" in state.world.organizations
    assert "暗流组织" in state.world.organizations
    assert state.world.organizations["黑夜教会"]["attention"] == 0
    assert state.world.organizations["暗流组织"]["activity"] == 0


def test_church_attention_rises_with_clues():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.clues = ["missing_notice", "wall_symbol", "old_button"]

    for _ in range(5):
        engine.update_organizations(state)

    assert state.world.organizations["黑夜教会"]["attention"] > 0


def test_church_attention_spikes_when_ally():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.tags.append("成为教会线人")

    for _ in range(3):
        engine.update_organizations(state)

    assert state.world.organizations["黑夜教会"]["attention"] >= 3


def test_secret_activity_rises_with_beyonder_ties():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.tags.append("加入神秘组织")
    state.character.corruption = 12

    for _ in range(5):
        engine.update_organizations(state)

    assert state.world.organizations["暗流组织"]["activity"] > 0


def test_organizations_clamped_0_100():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.clues = ["a", "b", "c", "d", "e", "f", "g"]

    for _ in range(50):
        engine.update_organizations(state)

    assert 0 <= state.world.organizations["黑夜教会"]["attention"] <= 100
    assert 0 <= state.world.organizations["暗流组织"]["activity"] <= 100


def test_organizations_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.organizations["暗流组织"]["activity"] = 42

    save_game(state, "org.json")
    loaded = load_game("org.json")

    assert loaded.world.organizations["暗流组织"]["activity"] == 42
    assert "黑夜教会" in loaded.world.organizations


# ============ ② NPC 模拟：周末与失踪 ============

def test_npc_weekend_schedule_differs():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    assert tom.weekend_schedule, "汤姆应有周末日程"

    # 周一（day 0）：用工作日日程
    state.days_lived = 0
    engine.npc_system.tick(state)
    monday_activity = tom.current_activity

    # 周六（day 5）：用周末日程
    state.days_lived = 5
    engine.npc_system.tick(state)
    saturday_activity = tom.current_activity

    assert monday_activity != saturday_activity


def test_npc_missing_stops_moving():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    engine.npc_system.disappear(state, "tom_tavern")

    assert tom.disappeared
    assert tom.current_activity == "（失踪）"

    before_loc = tom.location
    engine.tick(state, days=10)
    assert tom.location == before_loc, "失踪 NPC 不应再移动"


def test_npc_missing_tracked():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.npc_system.disappear(state, "erin_doctor")

    missing = engine.npc_system.missing_npcs(state)
    assert [n.id for n in missing] == ["erin_doctor"]
    assert state.npcs["erin_doctor"].disappeared_day == 0


# ============ ③ Canon 导入 ============

def test_canon_import_generates_structured_data(tmp_path):
    from life_sim.canon_importer import import_canon, load_canon

    # 用测试源目录
    src = tmp_path / "src"
    src.mkdir()
    (src / "organizations.json").write_text(
        json.dumps(
            [
                {
                    "id": "night_goddess_church",
                    "name": "黑夜女神教会",
                    "era": "第五纪",
                    "location": ["鲁恩", "廷根"],
                }
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    import_canon(src, out_dir=out_dir)
    orgs = load_canon("organizations", root=out_dir)

    assert len(orgs) == 1
    assert orgs[0]["id"] == "night_goddess_church"
    assert orgs[0]["name"] == "黑夜女神教会"
    assert orgs[0]["type"] == "organization"
    assert orgs[0]["era"] == "第五纪"
    assert "廷根" in orgs[0]["location"]


def test_canon_import_merges_and_dedups(tmp_path):
    from life_sim.canon_importer import import_canon, load_canon

    src = tmp_path / "src"
    src.mkdir()
    (src / "organizations.json").write_text(
        json.dumps(
            [
                {"id": "a", "name": "教会A", "locations": ["廷根"]},
                {"id": "a", "name": "教会A新版", "locations": ["贝克兰德"]},
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    out_dir = tmp_path / "out"

    import_canon(src, out_dir=out_dir)
    orgs = load_canon("organizations", root=out_dir)

    assert len(orgs) == 1  # 同 id 去重，源覆盖
    assert orgs[0]["name"] == "教会A新版"


def test_canon_load_missing_returns_empty(tmp_path):
    from life_sim.canon_importer import load_canon

    assert load_canon("nope.json", root=tmp_path) == []