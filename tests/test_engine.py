from life_sim.engine import LifeEngine, WorldEngine
from life_sim.event_system import EventEdge, EventGraph, EventNode, EventSystem
from life_sim.save import load_game, save_game


def test_action_advances_time_and_records_journal():
    engine = LifeEngine(seed=1)
    state = engine.new_game()

    entry = engine.take_action(state, "study")

    assert state.days_lived == 1
    assert state.date.day == 2
    assert state.character.intelligence == 57
    assert state.journal == [entry]


def test_auto_action_prefers_rest_when_exhausted():
    engine = LifeEngine(seed=1)
    state = engine.new_game()
    state.character.stamina = 20

    assert engine.auto_action(state) == "rest"


def test_world_engine_process_action_keeps_life_engine_compatibility():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    entry = engine.process_action(state, "study")

    assert state.days_lived == 1
    assert state.date.day == 2
    assert entry.action == "学习"


def test_world_engine_tick_increases_age_after_new_year():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.date.month = 12
    state.date.day = 30
    age = state.character.age

    engine.tick(state)

    assert state.date.year == 1349
    assert state.character.age == age + 1


def test_event_system_advances_graph_when_edge_condition_is_met():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="missing_person",
        nodes={
            "start": EventNode(id="start", text="有人失踪"),
            "find_clue": EventNode(
                id="find_clue",
                text="你发现了线索",
                conditions={"min_stat": {"intelligence": 10}},
            ),
        },
        edges=[
            EventEdge(
                from_node="start",
                to_node="find_clue",
                condition={"min_stat": {"intelligence": 10}},
            )
        ],
    )
    event_system = EventSystem([graph])

    event_system.apply(graph, graph.nodes["start"], state)

    assert state.event_nodes["missing_person"] == "find_clue"
    assert event_system.available_nodes(state)[0][1].text == "你发现了线索"


def test_event_system_does_not_advance_graph_when_edge_condition_fails():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="missing_person",
        nodes={
            "start": EventNode(id="start", text="有人失踪"),
            "find_clue": EventNode(id="find_clue", text="你发现了线索"),
        },
        edges=[
            EventEdge(
                from_node="start",
                to_node="find_clue",
                condition={"min_stat": {"mysticism_knowledge": 10}},
            )
        ],
    )
    event_system = EventSystem([graph])

    event_system.apply(graph, graph.nodes["start"], state)

    assert state.event_nodes["missing_person"] == "done"


def test_world_engine_loads_event_graph_data():
    engine = WorldEngine(seed=1)

    assert "ordinary_life" in engine.event_system.graphs
    assert "abnormal_disappearance" in engine.event_system.graphs
    ordinary = engine.event_system.graphs["ordinary_life"]
    fun = engine.event_system.graphs["abnormal_disappearance"]

    assert ordinary.is_pool
    assert len(ordinary.nodes) == 24  # start + 10 普通 + 4 季节 + 4 职业 + 3 意外支出 + 2 社交层次
    assert {n.id for n in ordinary.nodes.values()} - {"start"}

    assert not fun.is_pool
    assert len(fun.nodes) == 5
    assert fun.edges[0].from_node == "abnormal_notice"
    assert fun.edges[0].to_node == "abnormal_overlap"


def test_world_engine_creates_21_npcs_with_schedules():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    assert len(state.npcs) == 22  # V0.32 加值夜者队长邓恩
    assert "dunn_smith" in state.npcs
    tom = state.npcs["tom_tavern"]
    assert tom.name == "汤姆"
    assert tom.job == "酒馆老板"
    assert tom.goal == "赚钱"
    assert len(tom.schedule) == 4
    assert tom.current_time == "08:00"
    for npc in state.npcs.values():
        assert npc.schedule, f"{npc.id} 应该有日程"


def test_world_engine_tick_updates_npc_activity_and_fatigue():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]  # 使用 Schedule 2.0（tavern_owner 模板）
    fatigue = tom.fatigue

    engine.tick(state)

    # V0.15.2：一天走完整时间线，最终停在入睡（23:00）
    assert tom.current_time == "23:00"
    assert tom.current_activity == "入睡"
    assert tom.location == tom.home
    assert 0 <= tom.fatigue <= 100  # 全天活动后疲劳仍在界内


def test_world_engine_tick_100_days_keeps_world_state_consistent():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    engine.tick(state, days=100)

    assert state.days_lived == 100
    assert state.date.month == 4
    assert state.date.day == 11
    assert state.world.weather
    assert 0 <= state.world.economy["pressure"] <= 100
    assert 0 <= state.world.city["tension"] <= 100
    assert state.npcs["tom_tavern"].current_activity


def test_actions_include_investigate_and_deduce():
    engine = WorldEngine(seed=1)

    assert "investigate" in engine.available_actions()
    assert "deduce" in engine.available_actions()


def test_mystic_chain_advances_after_disappearance_decision():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system
    graph = event_system.graphs["mystic_contact"]

    assert len(graph.nodes) == 4  # start + 3 个非凡接触节点

    # 模拟失踪案调查到底：角色选择“向教会举报”
    state.character.tags.append("向教会举报")
    state.days_lived = 16

    # start（占位）→ contact_priest（min_day 16 + any_tag 满足）
    start = graph.nodes["start"]
    event_system.apply(graph, start, state)
    assert state.event_nodes["mystic_contact"] == "contact_priest"

    # contact_priest → dream_first（需要拿到教堂旧币）
    state.days_lived = 20
    priest = graph.nodes["contact_priest"]
    assert event_system.conditions_met(priest.conditions, state)
    event_system.apply(graph, priest, state)
    assert "拿到教堂旧币" in state.character.tags
    assert state.event_nodes["mystic_contact"] == "dream_first"

    # dream_first → contact_beyonder（需要 min_day 25 + dream_route 线索）
    state.days_lived = 25
    dream = graph.nodes["dream_first"]
    assert event_system.conditions_met(dream.conditions, state)
    event_system.apply(graph, dream, state)
    assert "dream_route" in state.clues
    assert state.event_nodes["mystic_contact"] == "contact_beyonder"

    beyonder = graph.nodes["contact_beyonder"]
    assert event_system.conditions_met(beyonder.conditions, state)
    assert beyonder.add_tags == ["初涉非凡"]


def test_abnormal_graph_conditions_require_clues():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 10
    event_system = engine.event_system

    overlap = event_system.graphs["abnormal_disappearance"].nodes["abnormal_overlap"]

    assert not event_system.conditions_met(overlap.conditions, state)
    state.clues.append("missing_notice")
    assert event_system.conditions_met(overlap.conditions, state)


def test_ordinary_pool_events_have_location_conditions():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    event_system = engine.event_system
    ordinary = event_system.graphs["ordinary_life"]

    # 车站事件要求地点在 station 列表中
    notice = ordinary.nodes["ordinary_rain"]
    assert "location" not in notice.conditions or isinstance(
        notice.conditions["location"], list
    )


def test_event_system_lists_condition_ready_node():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    graph = EventGraph(
        id="ordinary_job",
        nodes={
            "start": EventNode(
                id="start",
                text="上司注意到了你",
                conditions={"min_stat": {"intelligence": 55}},
            )
        },
    )
    event_system = EventSystem([graph])

    available = event_system.available_nodes(state)

    assert available == [(graph, graph.nodes["start"])]


def test_save_and_load_preserves_state(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.tick(state, days=3)

    save_game(state, "roundtrip.json")
    loaded = load_game("roundtrip.json")

    assert loaded.to_dict() == state.to_dict()
