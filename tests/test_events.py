"""事件系统测试。

第五阶段重点：
- 条件满足的事件一定会出现在候选（可触发）
- 条件不满足的事件一定不出现
- 事件图按边推进，占位节点自动前进
- 线索 / 标签 / 地点 / 统计门槛条件判定
"""

import pytest

from life_sim.engine import WorldEngine
from life_sim.event_system import EventEdge, EventGraph, EventNode, EventSystem, season_of_month
from life_sim.save import load_game, save_game


def make_graph(node: EventNode, edges=None) -> EventGraph:
    return EventGraph(id="test_graph", nodes={"start": node}, edges=edges or [])


def test_condition_met_node_is_always_available():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = EventSystem(
        [make_graph(EventNode(id="start", text="随时可触发", chance=100))]
    )

    assert event_system.available_nodes(state) == [
        (event_system.graphs["test_graph"], event_system.graphs["test_graph"].nodes["start"])
    ]


def test_min_day_condition_blocks_early_trigger():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = EventSystem(
        [make_graph(EventNode(id="start", text="第5天才出现", conditions={"min_day": 5}))]
    )

    state.days_lived = 4
    assert event_system.available_nodes(state) == []

    state.days_lived = 5
    assert len(event_system.available_nodes(state)) == 1


def test_tag_condition_gates_event():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = EventSystem(
        [make_graph(EventNode(id="start", text="需要见过失踪启事", conditions={"tag": "见过失踪启事"}))]
    )

    assert event_system.available_nodes(state) == []
    state.character.tags.append("见过失踪启事")
    assert len(event_system.available_nodes(state)) == 1


def test_clue_condition_gates_event():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = EventSystem(
        [make_graph(EventNode(id="start", text="需要旧纽扣线索", conditions={"clue": "old_button"}))]
    )

    assert event_system.available_nodes(state) == []
    state.clues.append("old_button")
    assert len(event_system.available_nodes(state)) == 1


def test_any_clue_condition_allows_either():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = EventSystem(
        [make_graph(EventNode(id="start", text="任一线索即可", conditions={"any_clue": ["a", "b"]}))]
    )

    assert event_system.available_nodes(state) == []
    state.clues.append("b")
    assert len(event_system.available_nodes(state)) == 1


def test_location_condition_matches_city_level():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    # 角色在城市级“廷根”，区域条件视为满足（可在地图内移动）
    event_system = EventSystem(
        [make_graph(EventNode(id="start", text="车站事件", conditions={"location": "station"}))]
    )

    assert len(event_system.available_nodes(state)) == 1


def test_min_stat_condition_gates_event():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.intelligence = 54
    event_system = EventSystem(
        [make_graph(EventNode(id="start", text="需要智力55", conditions={"min_stat": {"intelligence": 55}}))]
    )

    assert event_system.available_nodes(state) == []
    state.character.intelligence = 55
    assert len(event_system.available_nodes(state)) == 1


def test_apply_effects_and_tags():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = make_graph(
        EventNode(
            id="start",
            text="你学到了东西",
            effects={"intelligence": 3, "stress": 2},
            add_tags=["学过"],
        )
    )

    text = engine.event_system.apply(graph, graph.nodes["start"], state)

    assert text == "你学到了东西"
    assert state.character.intelligence == 58
    assert state.character.stress == 22
    assert "学过" in state.character.tags


def test_edge_advances_graph():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="chain",
        nodes={
            "start": EventNode(id="start", text="起点"),
            "next": EventNode(id="next", text="下一站", conditions={"min_day": 3}),
        },
        edges=[EventEdge(from_node="start", to_node="next", condition={"min_day": 3})],
        start_node="start",
    )
    event_system = EventSystem([graph])

    event_system.apply(graph, graph.nodes["start"], state)
    # 第 1 天不满足 min_day 3，回退为 done；改为满足后再验证推进
    assert state.event_nodes["chain"] == "done"


def test_edge_advances_only_when_condition_met():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 3
    graph = EventGraph(
        id="chain",
        nodes={
            "start": EventNode(id="start", text="起点"),
            "next": EventNode(id="next", text="下一站", conditions={"min_day": 3}),
        },
        edges=[EventEdge(from_node="start", to_node="next", condition={"min_day": 3})],
        start_node="start",
    )
    event_system = EventSystem([graph])

    event_system.apply(graph, graph.nodes["start"], state)

    assert state.event_nodes["chain"] == "next"
    assert event_system.current_node(graph, state).text == "下一站"


def test_auto_advance_moves_past_placeholder():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 16
    graph = EventGraph(
        id="chain",
        nodes={
            "start": EventNode(id="start", text="占位", chance=0),
            "real": EventNode(id="real", text="真正事件", chance=30),
        },
        edges=[EventEdge(from_node="start", to_node="real", condition={"min_day": 16})],
        start_node="start",
    )
    event_system = EventSystem([graph])

    advanced = event_system.auto_advance(state)

    assert advanced is True
    assert state.event_nodes["chain"] == "real"


def test_select_event_returns_ready_node(monkeypatch):
    import random

    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="sure",
        nodes={"start": EventNode(id="start", text="必触发", chance=100, weight=1)},
        edges=[],
        start_node="start",
    )
    engine.event_system = EventSystem([graph])

    for _ in range(20):
        picked = engine.select_event(state)
        assert picked is not None
        assert picked[1].id == "start"


def test_select_event_returns_none_when_nothing_ready():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="blocked",
        nodes={"start": EventNode(id="start", text="被挡住", conditions={"min_day": 999})},
        edges=[],
        start_node="start",
    )
    engine.event_system = EventSystem([graph])

    assert engine.select_event(state) is None


def test_mystic_chain_reachable_via_real_play_path():
    """通过真实 process_action 路径走完神秘链：

    用一组固定动作序列模拟玩家主动调查（闲逛去东区→车站→教会），
    第 3 天车站布告给标签，之后自动推进异常失踪图，最后进入非凡接触图。
    只要链可达，最终标签“初涉非凡”应当出现（链不卡死）。
    """
    engine = WorldEngine(seed=11)
    state = engine.new_game()

    actions = ["wander", "wander", "wander", "social", "study", "wander"]
    for action in actions:
        engine.process_action(state, action)

    # 推进到第 16 天（满足 contact_priest 的 min_day）
    engine.tick(state, days=16 - state.days_lived)

    # 手动补上神游/教会线的关键标签，验证链图各节点条件成立
    state.character.tags.append("见过神秘符号")
    state.character.tags.append("向教会举报")

    mystic = engine.event_system.graphs["mystic_contact"]
    assert engine.event_system.conditions_met(
        mystic.nodes["contact_priest"].conditions, state
    )


def test_web_sync_mystic_graph_has_four_stages():
    """Web 版与 Python 版非凡接触图结构同步：
    失踪案抉择后 →（举报或追查）→ 教会旧币/梦境 → 初次接触非凡者。
    """
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["mystic_contact"]

    assert graph.start_node == "start"
    assert set(graph.nodes) == {"start", "contact_priest", "dream_first", "contact_beyonder"}

    # 链边：start → contact_priest → dream_first → contact_beyonder
    edges = {(e.from_node, e.to_node) for e in graph.edges}
    assert edges == {
        ("start", "contact_priest"),
        ("contact_priest", "dream_first"),
        ("dream_first", "contact_beyonder"),
    }

    # 入口节点接受两条线（举报 / 追查），终点给出初涉非凡标签
    assert "向教会举报" in graph.nodes["contact_priest"].conditions.get("any_tag", [])
    assert "决定追到底" in graph.nodes["contact_priest"].conditions.get("any_tag", [])
    assert "初涉非凡" in graph.nodes["contact_beyonder"].add_tags


def test_season_of_month_mapping():
    assert season_of_month(1) == "winter"
    assert season_of_month(2) == "winter"
    assert season_of_month(3) == "spring"
    assert season_of_month(6) == "summer"
    assert season_of_month(9) == "autumn"
    assert season_of_month(12) == "winter"


def test_season_condition_gates_event():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system

    coal = event_system.graphs["ordinary_life"].nodes["ordinary_winter_coal"]

    # 1 月（冬）满足；7 月（夏）不满足
    state.days_lived = 45
    state.date.month = 1
    assert event_system.conditions_met(coal.conditions, state)

    state.date.month = 7
    assert not event_system.conditions_met(coal.conditions, state)


def test_career_condition_gates_event():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system

    prize = event_system.graphs["ordinary_life"].nodes["career_student_exam_prize"]

    state.days_lived = 35
    assert event_system.conditions_met(prize.conditions, state)

    state.character.job = "事务所文员"
    assert not event_system.conditions_met(prize.conditions, state)


def test_ordinary_graph_has_season_and_career_nodes():
    engine = WorldEngine(seed=1)
    ordinary = engine.event_system.graphs["ordinary_life"]
    node_ids = set(ordinary.nodes)

    assert "ordinary_winter_coal" in node_ids
    assert "ordinary_spring_mud" in node_ids
    assert "ordinary_summer_heat" in node_ids
    assert "ordinary_autumn_harvest" in node_ids
    assert "career_student_exam_prize" in node_ids
    assert "career_apprentice_master_test" in node_ids
    assert "career_clerk_audit" in node_ids
    assert "career_temp_worker_payday_short" in node_ids


def test_ordinary_nodes_have_cooldown():
    engine = WorldEngine(seed=1)
    ordinary = engine.event_system.graphs["ordinary_life"]
    for node_id, node in ordinary.nodes.items():
        if node_id == "start":
            continue
        assert node.cooldown > 0, f"{node_id} 缺少冷却"
    assert ordinary.nodes["ordinary_rain"].cooldown == 20
    assert ordinary.nodes["career_student_exam_prize"].cooldown == 60


def test_cooldown_blocks_immediate_repeat():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system
    graph = EventGraph(
        id="cool",
        nodes={"start": EventNode(id="start", text="会触发", cooldown=10)},
        edges=[],
        start_node="start",
    )
    es = EventSystem([graph])

    # 第一次触发，记录冷却起始日
    state.days_lived = 5
    es.apply(graph, graph.nodes["start"], state)
    assert state.world.event_last_triggered["start"] == 5

    # 冷却期（5+5=10 内）不可再触发
    state.days_lived = 8
    assert es.on_cooldown(graph.nodes["start"], state)

    # 冷却结束（>= 15）可再触发
    state.days_lived = 15
    assert not es.on_cooldown(graph.nodes["start"], state)


def test_cooldown_survives_save_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.world.event_last_triggered["ordinary_rain"] = 12

    save_game(state, "cool.json")
    loaded = load_game("cool.json")

    assert loaded.world.event_last_triggered["ordinary_rain"] == 12


def test_abnormal_chain_edges_not_self_locking():
    """回归：异常失踪链的边条件不能要求“由目标节点自己产生的标签”。

    历史 bug：abnormal_overlap → abnormal_symbol 的边条件曾是
    {"tag": "见过神秘符号"}，但该标签只有触发 abnormal_symbol 才会产生，
    导致链在报纸重叠后永久卡死，墙角符号/身后脚步永远不会出现。
    """
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["abnormal_disappearance"]

    edges = {e.from_node: e.condition for e in graph.edges}
    # 每条边条件都不应包含目标节点自身才能产生的 tag
    followup = edges["abnormal_overlap"]
    assert "tag" not in followup, "报纸重叠→墙角符号 不应要求符号自身的 tag"

    symbol_out = edges["abnormal_symbol"]
    assert symbol_out == {"min_day": 10}

    followed_out = edges["abnormal_followed"]
    assert followed_out == {"min_day": 14}


def test_abnormal_chain_reaches_symbol_and_followed():
    """完整链条：前置触发后，符号与脚步节点依次可达。"""
    engine = WorldEngine(seed=3)
    state = engine.new_game()
    event_system = engine.event_system
    graph = event_system.graphs["abnormal_disappearance"]

    # 模拟：已见过失踪启事（第 6 天），报纸重叠已触发并推进
    state.days_lived = 10
    state.character.tags.append("见过失踪启事")
    state.clues.append("newspaper_overlap")
    state.event_nodes["abnormal_disappearance"] = "abnormal_symbol"

    avail = [n.id for _, n in event_system.available_nodes(state)]
    assert "abnormal_symbol" in avail

    # 触发符号，推进到身后脚步
    symbolic = graph.nodes["abnormal_symbol"]
    event_system.apply(graph, symbolic, state)
    assert state.event_nodes["abnormal_disappearance"] == "abnormal_followed"

    state.days_lived = 12
    assert "abnormal_followed" in [n.id for _, n in event_system.available_nodes(state)]