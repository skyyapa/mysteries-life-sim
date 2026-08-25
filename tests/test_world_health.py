"""长时间运行健康测试。

模拟器最怕的事：跑很久之后世界坏掉。
- 角色属性必须始终在合理范围（0-100，金钱 >= 0）
- 世界状态（经济压力/城市紧张）必须界内
- NPC 都不腐坏：疲劳界内、日程可推进、位置合理
- 事件图不卡死：每个链图要么在有效节点，要么明确 done
- 存档在任何时刻都能保存并往返一致（可随时存档是长期可玩的前提）
- 多随机种子下都稳定（撒网找脆弱点）
"""

import pytest

from life_sim.engine import WorldEngine
from life_sim.save import load_game, save_game

STAT_RANGES = {
    "health": (0, 100),
    "stamina": (0, 100),
    "intelligence": (0, 100),
    "charisma": (0, 100),
    "stress": (0, 100),
    "money": (0, None),  # 无上限，但 >= 0
    "mysticism_knowledge": (0, 100),
    "spirituality": (0, 100),
    "corruption": (0, 100),
}


def assert_stats_in_range(state, label):
    for stat, (lo, hi) in STAT_RANGES.items():
        value = getattr(state.character, stat)
        assert lo <= value, f"{label}: {stat} 低于下限 {lo}，实际 {value}"
        if hi is not None:
            assert value <= hi, f"{label}: {stat} 超过上限 {hi}，实际 {value}"


def assert_world_healthy(state, label):
    assert 0 <= state.world.economy["pressure"] <= 100, f"{label}: 经济压力越界"
    assert 0 <= state.world.city["tension"] <= 100, f"{label}: 城市紧张越界"
    assert state.world.weather, f"{label}: 天气为空"
    for npc_id, npc in state.npcs.items():
        assert 0 <= npc.fatigue <= 100, f"{label}: NPC {npc_id} 疲劳越界"
        assert npc.current_activity, f"{label}: NPC {npc_id} 活动为空"
        assert npc.location, f"{label}: NPC {npc_id} 位置为空"
        if npc.schedule:
            assert npc.current_time, f"{label}: NPC {npc_id} 时间为空"


def assert_graphs_not_stuck(state, label, engine):
    """链图必须处于有效节点或 done，不允许指向不存在的节点。"""
    known = {
        graph_id: set(graph.nodes) | {"done"}
        for graph_id, graph in engine.event_system.graphs.items()
    }
    for graph_id, node_id in state.event_nodes.items():
        allowed = known.get(graph_id)
        assert allowed is not None, f"{label}: 未知事件图 {graph_id}"
        assert node_id in allowed, f"{label}: 图 {graph_id} 卡在未知节点 {node_id}"


@pytest.mark.parametrize("seed,days", [(1, 100), (2, 360), (3, 365), (4, 730), (5, 100)])
def test_long_run_keeps_world_healthy(seed, days):
    engine = WorldEngine(seed=seed)
    state = engine.new_game()

    import random

    rng = random.Random(seed)
    for _ in range(days):
        action = rng.choice(engine.available_actions())
        entry = engine.process_action(state, action)
        # 每天推进后立即校验，抓最早腐坏点
        assert entry.summary, f"day{state.days_lived}: 日志摘要为空"

    label = f"seed={seed} day={state.days_lived}"
    assert state.days_lived == days
    assert_stats_in_range(state, label)
    assert_world_healthy(state, label)
    assert_graphs_not_stuck(state, label, engine)


@pytest.mark.parametrize(
    "seed,days,expected_age_gain,expected_year",
    [(1, 360, 1, 1349), (2, 730, 2, 1350), (3, 1095, 3, 1351)],
)
def test_long_run_age_and_year_progress(seed, days, expected_age_gain, expected_year):
    engine = WorldEngine(seed=seed)
    state = engine.new_game()
    age = state.character.age

    engine.tick(state, days=days)

    assert state.character.age == age + expected_age_gain
    assert state.date.year == expected_year


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_long_run_save_roundtrip_at_end(tmp_path, monkeypatch, seed):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=seed)
    state = engine.new_game()

    import random

    rng = random.Random(seed)
    for _ in range(120):
        action = rng.choice(engine.available_actions())
        engine.process_action(state, action)

    save_game(state, f"long_{seed}.json")
    loaded = load_game(f"long_{seed}.json")

    assert loaded.to_dict() == state.to_dict()


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_long_run_character_survives_200_days(seed):
    """200 天行动后角色不应死亡或进入不可逆坏状态。"""
    engine = WorldEngine(seed=seed)
    state = engine.new_game()

    import random

    rng = random.Random(seed)
    for _ in range(200):
        engine.process_action(state, rng.choice(engine.available_actions()))

    assert state.character.health > 0
    assert state.character.stress <= 100
    assert len(state.journal) == 200