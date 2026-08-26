"""V0.15.1 专项测试：NPC State + Needs。"""

from life_sim.engine import WorldEngine
from life_sim.models import NPC
from life_sim.npc.models import NPCNeeds, NPCState, NPCRelationship, migrate_relationship
from life_sim.npc.needs import apply_activity, drift_needs
from life_sim.save import load_game, save_game


# ---- NPCState ----

def test_npc_state_defaults_and_clamp():
    s = NPCState(health=100, fatigue=90, mood=50)
    s.clamp()
    assert s.health == 100
    assert s.fatigue == 90

    s.health = 120
    s.clamp()
    assert s.health == 100


def test_npc_state_roundtrip():
    s = NPCState(health=92, fatigue=38, stress=21, mood=60, money=12.5, sick=True)
    loaded = NPCState.from_dict(s.to_dict())
    assert loaded.to_dict() == s.to_dict()


# ---- NPCNeeds ----

def test_needs_drift_integers():
    n = NPCNeeds(hunger=50, rest=40, social=20, safety=0)
    drift_needs(n, hours=12)  # hunger +26.4, rest +19.2, social +9.6, safety +4.8

    assert isinstance(n.hunger, int)
    assert n.hunger > 50
    assert n.rest > 40
    assert n.social > 20
    assert n.safety > 0
    n.clamp()
    assert 0 <= n.hunger <= 100


def test_needs_activity_effects():
    n = NPCNeeds(hunger=80, rest=30, social=20, safety=0)
    s = NPCState(health=90, fatigue=60)

    apply_activity(n, s, "eat", hours=1)
    assert n.hunger < 80  # 进食降饥饿

    apply_activity(n, s, "sleep", hours=8)
    assert n.rest < 30  # 睡觉降疲劳需求

    # 只传需求（V0.15.1 日程满足路径）：state 不变但需求降
    n2 = NPCNeeds(hunger=70, rest=50, social=20, safety=0)
    apply_activity(n2, None, "eat", hours=1)
    assert n2.hunger < 70


def test_needs_roundtrip():
    n = NPCNeeds(hunger=35, rest=40, social=23, safety=8)
    loaded = NPCNeeds.from_dict(n.to_dict())
    assert loaded.to_dict() == n.to_dict()


# ---- NPCRelationship ----

def test_relationship_four_dimensions():
    r = NPCRelationship(trust=30, familiarity=45, affection=12, fear=0)
    assert r.to_dict() == {"trust": 30, "familiarity": 45, "affection": 12, "fear": 0}


def test_relationship_migration_from_legacy():
    legacy = {"trust": 30, "friendship": 20, "fear": 5}
    migrated = migrate_relationship(legacy)
    assert migrated["trust"] == 30
    assert migrated["familiarity"] == 20  # friendship → familiarity
    assert migrated["affection"] == 0
    assert migrated["fear"] == 5


# ---- NPC 集成 ----

def test_npc_has_state_and_needs():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]

    assert tom.state is not None
    assert tom.needs is not None
    assert tom.state.fatigue == tom.fatigue  # 旧字段与新状态同步
    assert tom.state.money == tom.money


def test_needs_grow_over_days():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    hunger0 = tom.needs.hunger

    engine.tick(state, days=3)

    assert tom.needs.hunger > hunger0  # 会饿
    assert tom.needs.social >= 0


def test_state_saved_and_loaded(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=5)
    tom = state.npcs["tom_tavern"]
    tom.state.stress = 42
    tom.needs.social = 33

    save_game(state, "npc15.json")
    loaded = load_game("npc15.json")
    ltom = loaded.npcs["tom_tavern"]

    assert ltom.state.stress == 42
    assert ltom.needs.social == 33
    assert ltom.state.sick == tom.state.sick


def test_legacy_save_without_state_loads(tmp_path, monkeypatch):
    """旧存档（无 state/needs 字段）仍能加载并补齐。"""
    import json

    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    data = state.to_dict()
    for npc in data["world"]["npcs"].values():
        npc.pop("state", None)
        npc.pop("needs", None)

    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    loaded = save_module.load_game("legacy.json")
    tom = loaded.npcs["tom_tavern"]
    assert tom.state is not None
    assert tom.needs is not None
    assert tom.state.fatigue == tom.fatigue