"""经济系统测试：存款、利息、意外支出、财务实战支取。"""

from life_sim.engine import WorldEngine
from life_sim.event_system import EventGraph, EventNode, EventSystem
from life_sim.save import load_game, save_game


def test_character_has_savings_field():
    engine = WorldEngine(seed=1)
    state = engine.new_game()

    assert state.character.savings == 0
    assert "savings" in state.character.to_dict()


def test_save_and_withdraw_actions_exist():
    engine = WorldEngine(seed=1)

    assert "save" in engine.available_actions()
    assert "withdraw" in engine.available_actions()


def test_save_action_moves_money_to_savings():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.money = 50

    engine.process_action(state, "save")

    assert state.character.money == 40
    assert state.character.savings == 10


def test_withdraw_action_moves_savings_to_money():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.savings = 30

    engine.process_action(state, "withdraw")

    assert state.character.savings == 20
    assert state.character.money == 130


def test_savings_never_negative():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.money = 5
    state.character.savings = 0

    engine.process_action(state, "withdraw")

    # 没钱可取时取 0，存款不为负
    assert state.character.savings == 0


def test_savings_roundtrip(tmp_path, monkeypatch):
    import life_sim.save as save_module

    monkeypatch.setattr(save_module, "SAVE_DIR", tmp_path)
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.savings = 42

    save_game(state, "savings.json")
    loaded = load_game("savings.json")

    assert loaded.character.savings == 42


def test_illness_event_effects_money_and_health():
    engine = WorldEngine(seed=1)
    graph = EventGraph(
        id="test_illness",
        nodes={
            "start": EventNode(
                id="start",
                text="染上风寒",
                effects={"money": -8, "health": 10, "stress": -2},
            )
        },
        edges=[],
        start_node="start",
    )
    es = EventSystem([graph])
    state = engine.new_game()
    health = state.character.health
    money = state.character.money

    es.apply(graph, graph.nodes["start"], state)

    assert state.character.money == money - 8
    assert state.character.health == health + 10


def test_ordinary_graph_has_economy_nodes():
    engine = WorldEngine(seed=1)
    ordinary = engine.event_system.graphs["ordinary_life"]
    node_ids = set(ordinary.nodes)

    assert "ordinary_illness" in node_ids
    assert "ordinary_broken_boots" in node_ids
    assert "ordinary_bank_counter" in node_ids


def test_bank_counter_deposit_moves_to_savings():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.character.money = 40
    graph = EventGraph(
        id="test_bank",
        nodes={
            "start": EventNode(
                id="start",
                text="银行柜台",
                effects={"money": -10, "savings": 10},
            )
        },
        edges=[],
        start_node="start",
    )
    es = EventSystem([graph])

    es.apply(graph, graph.nodes["start"], state)

    assert state.character.money == 30
    assert state.character.savings == 10