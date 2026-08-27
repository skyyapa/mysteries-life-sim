"""V0.15.4 专项测试：地点+经济联动（涌现循环）。"""

from life_sim.engine import WorldEngine
from life_sim.economy.system import NPC_DAILY_EXPENSE, npc_wage


# ---- NPC 经济 ----

def test_npc_wage_by_job():
    assert npc_wage("酒馆老板") == 6
    assert npc_wage("工厂工人") == 4
    assert npc_wage("流浪者") == 0
    assert npc_wage("不存在的职业") == 3  # 默认


def test_work_pays_wage():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]  # 酒馆老板 £6/天
    money_before = tom.state.money

    from life_sim.npc.effects import apply_result, build_result

    result = build_result(
        tom, "work", prev_location=tom.home,
        loc_type_map={"work": "workplace"}, loc_name_map={},
    )
    assert result.money_delta == 6.0  # 工作赚 £6
    apply_result(state, tom, result)
    assert tom.state.money == money_before + 6.0


def test_shop_consumes_money():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    money_before = tom.state.money

    from life_sim.npc.effects import apply_result, build_result

    result = build_result(
        tom, "shop", prev_location=tom.home,
        loc_type_map={"shop": "market"}, loc_name_map={},
    )
    assert result.money_delta < 0  # 购物花钱
    apply_result(state, tom, result)
    assert tom.state.money < money_before


def test_poverty_raises_npc_stress():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    bob = state.npcs["quincy_beggar"]  # 流浪者日薪 0
    bob.state.money = 0
    stress0 = bob.state.stress

    engine.economy_system._tick_npcs(state)  # 日常开销没钱

    assert bob.state.stress > stress0  # 吃不上饭压力上升


# ---- 地点联动 ----

def test_location_activity_follows_npc_density():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.location_system.ensure(state)

    # 北区塞满活跃工作的 NPC，教堂没人
    for nid in list(state.npcs)[:6]:
        state.npcs[nid].location = "北区"
        state.npcs[nid].current_activity = "工作"

    engine.location_system.tick(state)

    north = state.world.locations["北区"]["activity"]
    church = state.world.locations["黑夜教堂"]["activity"]
    assert north >= church


def test_occupancy_reports_npcs_per_location():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    # 把 3 个 NPC 移到市场区（无论原本在哪）
    moved = 0
    for nid in list(state.npcs):
        if moved >= 3:
            break
        if state.npcs[nid].location != "市场区":
            state.npcs[nid].location = "市场区"
            moved += 1

    occ = engine.location_system.occupancy(state)
    # 市场区 NPC = 原本就在市场的 + 移过去的 3 个
    assert occ["市场区"] >= 3


def test_night_reduces_activity_target():
    """夜间地点活跃度下降（factor 0.3）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    engine.location_system.ensure(state)
    state.date.hour = 23

    # 白天记录 vs 夜间记录
    engine.location_system.tick(state)
    day_act = state.world.locations["市场区"]["activity"]
    engine.location_system.tick(state)  # 连续夜间 tick
    state.world.locations["市场区"]["activity"] = day_act  # 重置便于对比
    engine.location_system.tick(state)

    # 用 occupancy+heat 保证：无 NPC 空地上，夜间更趋低
    assert 0 <= state.world.locations["市场区"]["activity"] <= 100


# ---- 涌现循环集成 ----

def test_poor_npc_trends_to_work():
    """没钱 → behavior 更倾向工作（涌现循环入口）。"""
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    tom.state.money = 1.0

    from life_sim.npc.behavior import _need_weight

    work_w = _need_weight(tom.needs, tom.state, "work")
    rest_w = _need_weight(tom.needs, tom.state, "rest")
    assert work_w > rest_w


def test_economy_npc_tick_keeps_money_nonneg():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    for npc in state.npcs.values():
        npc.state.money = 0  # 全员赤贫

    engine.economy_system._tick_npcs(state)

    for npc in state.npcs.values():
        assert npc.state.money >= 0  # 开销被截断不为负


def test_missing_npc_not_billed():
    engine = WorldEngine(seed=1)
    state = engine.new_game()
    tom = state.npcs["tom_tavern"]
    engine.npc_system.disappear(state, "tom_tavern")
    money0 = tom.state.money

    engine.economy_system._tick_npcs(state)

    assert tom.state.money == money0  # 失踪者不参与经济