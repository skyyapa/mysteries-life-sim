"""V0.25 专项测试：NPC 轻量记忆（规则驱动，帮过/坑过影响社交）。"""

import pytest

from life_sim.engine import WorldEngine
from life_sim.save import load_game, save_game


def test_remember_records_count_and_day():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]

    tom.remember("helped", day=10)
    tom.remember("helped", day=20)

    mem = tom.memories["helped"]
    assert mem["count"] == 2
    assert mem["last_day"] == 20


def test_memory_magnitude_recent_full():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    tom.remember("helped", day=10)

    assert tom.memory_magnitude("helped", day=20) == 1  # 30 天内全强度


def test_memory_magnitude_decays():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    tom.remember("helped", day=10)
    tom.remember("helped", day=11)
    tom.remember("helped", day=12)

    recent = tom.memory_magnitude("helped", day=20)
    old = tom.memory_magnitude("helped", day=200)
    assert recent > old, "近期记忆强度应更高（衰减生效）"


def test_unknown_memory_zero():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    assert tom.memory_magnitude("admired", day=5) == 0


def test_event_positive_trust_creates_helped():
    """事件给了 NPC 正信任 → 记录 helped 记忆。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    # 直接调用事件系统的信任效果路径
    graph = engine.event_system.graphs["ordinary_life"]
    node = graph.nodes["ordinary_illness"]
    # 构造一个带正 trust_effects 的节点应用
    from life_sim.event_system import EventNode

    node = EventNode(
        id="t_test",
        text="帮了汤姆一把",
        trust_effects={"tom_tavern": 5},
    )
    engine.event_system.apply(graph, node, state)

    tom = state.npcs["tom_tavern"]
    assert tom.trust >= 5
    assert tom.memories.get("helped", {}).get("count", 0) >= 1


def test_event_negative_trust_creates_harmed():
    from life_sim.event_system import EventNode

    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = engine.event_system.graphs["ordinary_life"]
    node = EventNode(
        id="t_neg",
        text="得罪了酒馆老板",
        trust_effects={"tom_tavern": -4},
    )
    engine.event_system.apply(graph, node, state)

    tom = state.npcs["tom_tavern"]
    assert tom.memories.get("harmed", {}).get("count", 0) >= 1


def test_social_benefit_from_helped_memory():
    """帮过的人社交收益更高。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    state.focused_contact = "tom_tavern"
    tom.remember("helped", day=state.days_lived)

    before = tom.trust
    engine.process_action(state, "social")

    assert tom.trust >= before + 3 + 1  # 基础 3 + 记忆 1


def test_social_penalty_from_harmed_memory():
    """坑过的人社交收益更低。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    state.focused_contact = "tom_tavern"
    tom.remember("harmed", day=state.days_lived)
    tom.remember("harmed", day=state.days_lived)

    before = tom.trust
    engine.process_action(state, "social")

    assert tom.trust < before + 3  # 被坑过：信任收益被削弱


def test_memories_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    tom.remember("helped", day=5)
    tom.remember("harmed", day=9)

    save_game(state, "mem.json")
    loaded = load_game("mem.json")
    ltom = loaded.npcs["tom_tavern"]

    assert ltom.memories["helped"]["count"] == 1
    assert ltom.memories["harmed"]["last_day"] == 9