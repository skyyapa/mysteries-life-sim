"""V0.26 专项测试：事件图图级分支（choice.branch_to）。"""

import json
from pathlib import Path

from life_sim.engine import WorldEngine

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"


def _setup_mainline(engine, state):
    """推进主线到 truth_choice 处（设标签模拟已走完前面链）。"""
    state.days_lived = 52
    state.event_nodes["hidden_current"] = "truth_choice"


def test_truth_choice_has_branches():
    engine = WorldEngine(seed=1)
    graph = engine.event_system.graphs["hidden_current"]
    node = graph.nodes["truth_choice"]

    assert node.choices
    branches = {c.get("branch_to") for c in node.choices}
    assert branches == {
        "branch_org_life",
        "branch_church_life",
        "branch_plain_life",
    }


def test_apply_choice_moves_chain_to_branch():
    """选择"加入组织" → 链推进到 branch_org_life，且带标签。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    _setup_mainline(engine, state)

    graph = engine.event_system.graphs["hidden_current"]
    node = graph.nodes["truth_choice"]
    org_choice = next(i for i, c in enumerate(node.choices) if c.get("branch_to") == "branch_org_life")

    engine.event_system.apply_choice(graph, node, org_choice, state)

    assert state.event_nodes["hidden_current"] == "branch_org_life"
    assert "加入神秘组织" in state.character.tags


def test_branch_node_visible_after_choice():
    """选择加入组织后：只有组织线分支可用，其它线不可见。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 55
    state.character.tags.append("加入神秘组织")
    state.event_nodes["hidden_current"] = "truth_choice"  # 玩家正处抉择点

    avail = engine.event_system.available_nodes(state)
    nodes = {n.id for g, n in avail if g.id == "hidden_current"}

    assert "branch_org_life" in nodes
    assert "branch_church_life" not in nodes  # 未选教会，教会线不可见
    assert "branch_plain_life" not in nodes


def test_other_branch_hidden_without_tag():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 55
    state.character.tags.append("成为教会线人")
    state.event_nodes["hidden_current"] = "truth_choice"

    avail = engine.event_system.available_nodes(state)
    nodes = {n.id for g, n in avail if g.id == "hidden_current"}

    assert "branch_church_life" in nodes
    assert "branch_org_life" not in nodes
    assert "branch_plain_life" not in nodes


def test_branch_chain_continues():
    """组织线：branch_org_life → 选择 → branch_org_life_end。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    state.days_lived = 60
    state.character.tags.append("加入神秘组织")
    state.event_nodes["hidden_current"] = "branch_org_life"

    graph = engine.event_system.graphs["hidden_current"]
    node = graph.nodes["branch_org_life"]
    engine.event_system.apply_choice(graph, node, 0, state)

    assert state.event_nodes["hidden_current"] == "branch_org_life_end"
    assert "组织线结局" in state.character.tags


def test_every_branch_to_target_exists():
    """数据中所有 branch_to 引用都存在（语义校验，和 validate 交叉印证）。"""
    data = json.loads((DATA_DIR / "event_graphs.json").read_text(encoding="utf-8"))
    for graph in data:
        ids = {n["id"] for n in graph.get("nodes", [])}
        for node in graph.get("nodes", []):
            for choice in node.get("choices", []):
                branch_to = choice.get("branch_to")
                if branch_to:
                    assert branch_to in ids, f"{graph['id']}/{node['id']} branch_to '{branch_to}' 不存在"


def test_validate_catches_bad_branch_to():
    """校验器应能抓住无效 branch_to（写错目标）。"""
    from life_sim.validate_data import validate_event_graphs

    graphs = json.loads((DATA_DIR / "event_graphs.json").read_text(encoding="utf-8"))
    import copy

    bad = copy.deepcopy(graphs[-1])  # 主线图
    bad["nodes"][0]["choices"] = [{"label": "x", "result": "y", "branch_to": "ghost_node"}]
    errors = validate_event_graphs([bad])
    assert any("branch_to 'ghost_node' 不存在" in e for e in errors)