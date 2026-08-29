"""V0.28 细节复查回归测试：过逐个场景验证晋升机制边界。"""

from life_sim.engine import WorldEngine


def _seer_state(engine, spirit=30, seq=9, day=62):
    state = engine.new_game()
    state.character.pathway = "占卜家"
    state.character.sequence = seq
    state.character.spirituality = spirit
    state.days_lived = day
    state.character.tags += ["途径：占卜家"]
    state.clues.append("shadow_watcher")
    return state


def test_once_tag_blocks_repeat_trigger():
    """修复1：once_tag 事件触发后（无论饮/等）不再出现。"""
    engine = WorldEngine(seed=1)
    state = _seer_state(engine)
    graph = engine.event_system.graphs["seq_advance"]
    node = graph.nodes["seq9_seer_advance"]

    # 触发前可用
    assert not engine.event_system._once_triggered(node, state)
    # 触发（选"再等等"）
    engine.event_system.apply_choice(graph, node, 1, state)
    # 触发后一次标记已写入 → 不再可遇
    assert node.once_tag in state.character.tags
    assert engine.event_system._once_triggered(node, state)


def test_once_tag_filters_available():
    engine = WorldEngine(seed=1)
    state = _seer_state(engine)
    graph = engine.event_system.graphs["seq_advance"]
    state.character.tags.append("占卜家晋升")  # 模拟已触发过

    avail = engine.event_system.available_nodes(state)
    ids = {n.id for g, n in avail if g.id == "seq_advance"}
    assert "seq9_seer_advance" not in ids  # 已触发不再列出


def test_sequence_no_downgrade():
    """修复2：_sequence 不允许降级（当前8 → target9 无效）。"""
    engine = WorldEngine(seed=1)
    state = _seer_state(engine, seq=8, day=85)
    from life_sim.event_system import EventNode

    node = EventNode(
        id="x",
        text="伪造的晋升",
        effects={"_sequence": 9, "madness": 5},
    )
    graph = engine.event_system.graphs["seq_advance"]
    engine.event_system.apply(graph, node, state)

    assert state.character.sequence == 8  # 未降级


def test_spirituality_does_not_hide_advance_event():
    """V0.29 修正：灵性不足事件照常出现（风险在服食时，不在遇不到）。"""
    engine = WorldEngine(seed=1)
    state = _seer_state(engine, spirit=10, day=62)  # 灵性 10 < 25

    avail = engine.event_system.available_nodes(state)
    ids = {n.id for g, n in avail if g.id == "seq_advance"}
    assert "seq9_seer_advance" in ids  # 低灵性也能遇到晋升事件


def test_advance_event_not_gated_by_spirituality():
    """序列8→7 事件同样不受灵性硬门槛限制。"""
    engine = WorldEngine(seed=1)
    state = _seer_state(engine, spirit=30, seq=8, day=88)
    state.character.tags += ["序列：小丑"]

    avail = engine.event_system.available_nodes(state)
    ids = {n.id for g, n in avail if g.id == "seq_advance"}
    assert "seq8_seer_advance" in ids  # 30 < 45 也能遇到