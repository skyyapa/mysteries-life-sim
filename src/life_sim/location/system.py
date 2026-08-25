"""地点系统：地点的状态演化（人口 / 活跃度 / 危险）。

每个地点在 WorldState.locations 中保存：
    {"population": int, "activity": int, "danger": int}

Tick 规则（规则驱动，非随机）：
- 人口随城市整体繁荣缓慢变化（经济压力越低越有人气）
- 活跃度白天升、夜晚降；有 NPC 在附近的地点更活跃
- 危险度随暗流组织活跃上升；教会注意度高时下降（教会压制）
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import GameState


DEFAULT_LOCATIONS = {
    "北区": {"population": 40, "activity": 30, "danger": 6},
    "市场区": {"population": 60, "activity": 50, "danger": 12},
    "黑夜教堂": {"population": 20, "activity": 25, "danger": 4},
    "东区": {"population": 55, "activity": 35, "danger": 22},
    "廷根车站": {"population": 35, "activity": 45, "danger": 14},
}


@dataclass
class LocationSystem:
    ids: tuple[str, ...] = ("北区", "市场区", "黑夜教堂", "东区", "廷根车站")

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

        for name, loc in state.world.locations.items():
            pop, act, dang = loc["population"], loc["activity"], loc["danger"]

            # 人口：经济压力高压人口外流，低压力缓慢回升
            pop += -1 if economy_pressure > 60 else (1 if economy_pressure < 25 else 0)

            # 活跃度：白天 +，夜晚 -
            act += (-4 if is_night else +3)

            # 危险：暗流活跃推高，教会注意压制
            dang += (1 if secret > 40 else 0) - (1 if church > 40 else 0)

            loc["population"] = max(1, min(200, pop))
            loc["activity"] = max(0, min(100, act))
            loc["danger"] = max(0, min(100, dang))