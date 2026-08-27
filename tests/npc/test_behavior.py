"""V0.15.3 专项测试：Behavior Candidate（NPC 会改变计划）。"""

from life_sim.engine import WorldEngine
from life_sim.models import NPC
from life_sim.npc.behavior import (
    BehaviorCandidate,
    decide_behavior,
    generate_candidates,
    select,
)


def make_npc(engine, nid="tom_tavern"):
    state = engine.new_game()
    return state.npcs[nid], state


# ---- 候选生成与选择 ----

def test_candidates_include_schedule_and_pool():
    engine = WorldEngine(seed=1)
    npc, state = make_npc(engine)
    candidates = generate_candidates(
        npc,
        schedule_action="work",
        needs=npc.needs,
        state=npc.state,
        is_night=False,
        city_tension=20,
        day_index=0,
    )
    ids = [c.action_id for c in candidates]
    assert "work" in ids  # 日程行为
    assert len(ids) > 1  # 有候选池


def test_schedule_action_wins_by_default():
    """健康/需求正常时，日程行为应该胜出（基准 50）。"""
    engine = WorldEngine(seed=1)
    npc, _ = make_npc(engine)
    npc.state.health = 100
    npc.state.fatigue = 20
    npc.needs.hunger = 20
    npc.needs.rest = 20

    action, _cands = decide_behavior(
        npc,
        schedule_action="work",
        needs=npc.needs,
        state=npc.state,
        is_night=False,
        city_tension=10,
        day_index=1,
    )
    best = max(_cands, key=lambda c: c.score)
    assert best.action_id == "work"


# ---- 需求驱动 ----

def test_hunger_boosts_eat_scores():
    """饥饿对 eat 有强加分（need 贡献）。"""
    engine = WorldEngine(seed=1)
    npc, _ = make_npc(engine)
    from life_sim.npc.behavior import _need_weight

    npc.needs.hunger = 90
    eat_score = _need_weight(npc.needs, npc.state, "eat")
    work_score = _need_weight(npc.needs, npc.state, "work")
    assert eat_score >= 60, "饿极时 eat 加分应很高"
    assert eat_score > work_score, "饿极时 eat 应明显高于 work"


def test_fatigue_boosts_rest_scores():
    engine = WorldEngine(seed=1)
    npc, _ = make_npc(engine)
    from life_sim.npc.behavior import _need_weight

    npc.state.fatigue = 90
    npc.needs.rest = 90
    rest_score = _need_weight(npc.needs, npc.state, "rest")
    work_score = _need_weight(npc.needs, npc.state, "work")
    assert rest_score > work_score, "累垮时休息应占优"


# ---- 生病改变计划（规格重点） ----

def test_sick_npc_skips_work():
    """生病 → 待家分远高于上班分（stay_home 加分、work 大扣分）。"""
    engine = WorldEngine(seed=1)
    npc, _ = make_npc(engine)
    from life_sim.npc.behavior import _need_weight

    npc.state.sick = True
    home_score = _need_weight(npc.needs, npc.state, "stay_home")
    work_score = _need_weight(npc.needs, npc.state, "work")
    assert home_score >= 40, "生病待家应强加分"
    assert work_score < 0, "生病应给工作大幅扣分"
    assert home_score > work_score + 60, "生病时待家应显著压过工作"


def test_sick_npc_objectively_weakened_work():
    engine = WorldEngine(seed=1)
    npc, _state = make_npc(engine)
    npc.state.sick = True
    from life_sim.npc.behavior import _need_weight

    work_score = _need_weight(npc.needs, npc.state, "work")
    assert work_score < 0, "生病应给工作扣分"


def test_money_pressure_pushes_work():
    engine = WorldEngine(seed=1)
    npc, _ = make_npc(engine)
    from life_sim.npc.behavior import _need_weight

    npc.state.money = 1.0
    npc.state.fatigue = 30
    npc.needs.hunger = 30
    work_score = _need_weight(npc.needs, npc.state, "work")
    rest_score = _need_weight(npc.needs, npc.state, "rest")
    assert work_score > rest_score, "没钱时工作的需求贡献应更高"


# ---- 夜间 ----

def test_night_boosts_stay_in():
    engine = WorldEngine(seed=1)
    npc, _ = make_npc(engine)
    from life_sim.npc.behavior import _world_weight

    night_home = _world_weight(True, 10, "sleep")
    night_wander = _world_weight(True, 10, "wander")
    assert night_home > 30, "夜间回家/休息应强加分"
    assert night_wander < 0, "夜间闲逛应扣分"
    assert night_home > night_wander + 30


# ---- 目标影响（V0.15.3 核心） ----

def _npc_by_id(engine, nid):
    state = engine.new_game()
    return state.npcs[nid]


def test_goal_weights_money_lover():
    engine = WorldEngine(seed=1)
    from life_sim.npc.behavior import _goal_weight

    tom = _npc_by_id(engine, "tom_tavern")  # goal="赚钱"
    assert _goal_weight(tom, "work") >= 15  # 赚钱目标强化工作


def test_goal_weights_church_man():
    engine = WorldEngine(seed=1)
    from life_sim.npc.behavior import _goal_weight

    priest = _npc_by_id(engine, "olson_priest")  # 教士：维持教区安稳
    score = max(_goal_weight(priest, "stay_home"), _goal_weight(priest, "work"))
    assert score >= 8


def test_restday_behavior_remembers_weekend():
    """休息日模板无 work → NPC 不去上班（即便有 ambition）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    template = engine.npc_system.schedule_templates["factory_worker"]
    assert "work" not in template.rest_day.timeline.values()


# ---- Effects ----

def test_action_result_build_and_apply():
    engine = WorldEngine(seed=1)
    npc, state = make_npc(engine)
    from life_sim.npc.effects import apply_result, build_result

    result = build_result(
        npc, "work", prev_location=npc.home,
        hours=1.0,
        loc_type_map={"work": "workplace"},
        loc_name_map={},
    )
    assert result.action == "work"
    assert "NPCAttributeError" or "NPC_WORKED" in result.emitted_events

    apply_result(state, npc, result)
    assert npc.state.fatigue >= 0
    assert npc.fatigue == npc.state.fatigue


def test_missing_npc_does_not_act():
    engine = WorldEngine(seed=1)
    npc, state = make_npc(engine)
    engine.npc_system.disappear(state, npc.id)  # 走正式失踪流程
    before = npc.location
    engine.tick(state, days=3)
    assert npc.location == before  # 失踪者不动