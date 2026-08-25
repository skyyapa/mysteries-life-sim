from life_sim.engine import LifeEngine


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
