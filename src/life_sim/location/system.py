"""地点系统：地点的状态演化（人口 / 活跃度 / 危险）。

V0.15.4：活跃度不再凭空变——主要由"该地点的 NPC 数量 × 他们在做什么 × 昼夜"决定。
规格示例：上午 9 点市场里有 26 个 NPC、20 人在工作、6 人在购物 → activity = 78。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import GameState


DEFAULT_LOCATIONS = {
    "北区": {"population": 40, "activity": 30, "danger": 6},
    "市场区": {"population": 60, "activity": 50, "danger": 12},
    "圣赛琳娜教堂": {"population": 20, "activity": 25, "danger": 4},
    "东区": {"population": 55, "activity": 35, "danger": 22},
    "廷根车站": {"population": 35, "activity": 45, "danger": 14},
}

# 行为 → 给所在地点提供的"活动热度"
ACTIVITY_HEAT = {
    "work": 4,
    "shop": 3,
    "socialize": 3,
    "visit": 2,
    "wander": 1,
    "pray": 1,
    "breakfast": 1,
    "lunch": 2,
    "dinner": 2,
    "eat": 2,
}


@dataclass
class LocationSystem:
    ids: tuple[str, ...] = ("北区", "市场区", "圣赛琳娜教堂", "东区", "廷根车站")

    def init_state(self) -> dict[str, dict[str, int]]:
        return {name: dict(DEFAULT_LOCATIONS[name]) for name in self.ids}

    def ensure(self, state: GameState) -> None:
        if not state.world.locations:
            state.world.locations = self.init_state()
        for name in self.ids:
            state.world.locations.setdefault(name, dict(DEFAULT_LOCATIONS[name]))

    def tick(self, state: GameState) -> None:
        self.ensure(state)
        is_night = state.world.date.is_night()
        economy_pressure = state.world.economy.get("pressure", 0)
        secret = state.world.organizations.get("暗流组织", {}).get("activity", 0)
        church = state.world.organizations.get("黑夜教会", {}).get("attention", 0)

        # 统计每个地点的 NPC 分布与行为热度
        heat_by_loc: dict[str, int] = {name: 0 for name in self.ids}
        count_by_loc: dict[str, int] = {name: 0 for name in self.ids}
        is_night_factor = 0.3 if is_night else 1.0

        for npc in state.npcs.values():
            if npc.disappeared or not npc.state.alive:
                continue
            loc = npc.location
            if loc not in count_by_loc:
                continue
            count_by_loc[loc] += 1
            activity = npc.current_activity or ""
            # 中文活动名 → 行为 id 近似的热度（或直接用 behavior 的 current_activity 匹配热词）
            heat = 0
            for keyword, h in ACTIVITY_HEAT.items():
                if keyword in activity or activity == keyword:
                    heat = h
                    break
            heat_by_loc[loc] += heat

        for name, loc in state.world.locations.items():
            pop, act, dang = loc["population"], loc["activity"], loc["danger"]

            # 人口：经济压力高压人口外流，低压力缓慢回升
            pop += -1 if economy_pressure > 60 else (1 if economy_pressure < 25 else 0)

            # 活跃度：由该地 NPC 数量 + 行为热度驱动，向目标值靠拢
            target = int((count_by_loc.get(name, 0) * 2 + heat_by_loc.get(name, 0)) * is_night_factor)
            target = max(0, min(100, target + DEFAULT_LOCATIONS[name]["activity"] // 2))
            act = act + (2 if target > act else -1)  # 缓慢逼近目标，避免跳变

            # 危险：暗流活跃推高，教会注意压制
            dang += (1 if secret > 40 else 0) - (1 if church > 40 else 0)

            loc["population"] = max(1, min(200, pop))
            loc["activity"] = max(0, min(100, act))
            loc["danger"] = max(0, min(100, dang))

    def occupancy(self, state: GameState) -> dict[str, int]:
        """当前各地点 NPC 数量（用于 UI / 调试）。"""
        out = {name: 0 for name in self.ids}
        for npc in state.npcs.values():
            if npc.disappeared or not npc.state.alive:
                continue
            if npc.location in out:
                out[npc.location] += 1
        return out