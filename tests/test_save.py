"""存档系统测试。

第五阶段重点：
- 保存 → 加载后状态完全一致（字典级相等）
- 包含线索、结论、标签、NPC 日程等全量状态
- 旧版本存档（无 clues/deductions 字段）可加载且不崩溃
- 多个存档文件互不干扰
- 世界 Tick 后的动态状态也能往返
"""

import json

from life_sim.engine import WorldEngine
from life_sim.models import GameState
from life_sim.save import load_game, save_game


def test_save_load_roundtrip_full_state(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=30)

    save_game(state, "full.json")
    loaded = load_game("full.json")

    assert loaded.to_dict() == state.to_dict()


def test_roundtrip_preserves_clues_deductions_tags(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.tags.append("见过失踪启事")
    state.clues.append("missing_notice")
    state.deductions.append("east_case_pattern")

    save_game(state, "meta.json")
    loaded = load_game("meta.json")

    assert loaded.character.tags == ["见过失踪启事"]
    assert loaded.clues == ["missing_notice"]
    assert loaded.deductions == ["east_case_pattern"]


def test_roundtrip_preserves_npc_runtime_state(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=10)  # NPC 位置/活动/疲劳已推进

    save_game(state, "npcs.json")
    loaded = load_game("npcs.json")

    assert loaded.npcs["tom_tavern"].to_dict() == state.npcs["tom_tavern"].to_dict()


def test_roundtrip_preserves_event_progress(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.event_nodes["abnormal_disappearance"] = "abnormal_overlap"
    state.days_lived = 7

    save_game(state, "events.json")
    loaded = load_game("events.json")

    assert loaded.event_nodes == state.event_nodes
    assert loaded.world.event_nodes == state.world.event_nodes


def test_old_save_without_clues_deductions_loads(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    data = state.to_dict()
    data.pop("clues", None)
    data.pop("deductions", None)

    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    loaded = GameState.from_dict(json.loads(path.read_text(encoding="utf-8")))

    assert loaded.clues == []
    assert loaded.deductions == []
    assert loaded.character.name == state.character.name


def test_multiple_saves_are_isolated(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)

    state_a = engine.new_game()
    state_a.days_lived = 10
    state_a.character.tags.append("只有A")

    state_b = engine.new_game()
    state_b.days_lived = 20

    save_game(state_a, "a.json")
    save_game(state_b, "b.json")

    loaded_a = load_game("a.json")
    loaded_b = load_game("b.json")

    assert loaded_a.days_lived == 10
    assert loaded_b.days_lived == 20
    assert "只有A" in loaded_a.character.tags
    assert "只有A" not in loaded_b.character.tags


def test_tick_then_roundtrip_keeps_money_and_stats(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=3)
    state = engine.new_game()
    state.character.money = 12
    engine.tick(state, days=15)

    save_game(state, "stats.json")
    loaded = load_game("stats.json")

    assert loaded.character.money == 12
    assert loaded.character.health == state.character.health
    assert loaded.days_lived == 15