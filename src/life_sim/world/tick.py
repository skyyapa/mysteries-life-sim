"""WorldTick：世界推进的唯一入口。

设计原则（V0.14）：
- 所有世界变化必须经由 WorldTick.run()，禁止到处直接调用 npc.update() / event.trigger() 等。
- 七步编排：时间 → NPC → 地点 → 经济 → 关系 → 事件 → 存档。

分层与模块的对应：
    WorldEngine (总控制器)
        └── WorldTick (编排器)
              ├── TimeSystem        （时间推进，见 world.time）
              ├── NPCSystem         （NPC 行动，见 npc.system）
              ├── LocationSystem    （地点变化，见 location.system）
              ├── EconomySystem     （经济变化，见 economy.system）
              ├── RelationshipSystem（关系变化）
              ├── EventSystem       （事件检查，见 event.system）
              └── SaveSystem        （提交世界状态）
"""

from __future__ import annotations

from typing import Any, Callable

from ..models import GameState


class TimeSystem:
    """时间推进：按分钟前进；动作可以消耗时间（睡觉+8h、工作+6h、旅行+3天）。"""

    @staticmethod
    def advance(state: GameState, minutes: int = 0, hours: int = 0, days: int = 0) -> None:
        total = minutes + hours * 60 + days * 24 * 60
        state.world.date.advance_minutes(total)

    @staticmethod
    def sleep(state: GameState) -> None:
        """睡觉：+8 小时，进入次日早晨（若当前已是下午/夜晚），恢复部分体力。"""
        TimeSystem.advance(state, hours=8)
        if state.world.date.hour < 7 or state.world.date.hour > 12:
            # 睡到早七点附近
            target = 7 * 60 - (state.world.date.hour * 60 + state.world.date.minute)
            TimeSystem.advance(state, minutes=target % (24 * 60))

    @staticmethod
    def work(state: GameState) -> None:
        """工作：+6 小时。"""
        TimeSystem.advance(state, hours=6)

    @staticmethod
    def travel(state: GameState, days: int = 3) -> None:
        """旅行：+3 天。"""
        TimeSystem.advance(state, days=days)


class WorldTick:
    """编排一次世界推进。

    run(state) 依次执行：
        1. 时间推进（TimeSystem）
        2. NPC 行动（NPCSystem）
        3. 地点变化（LocationSystem）
        4. 经济结算（EconomySystem）
        5. 关系演化（RelationshipSystem）
        6. 事件检查（EventSystem）
        7. 世界状态提交（SaveSystem/回调）

    系统可通过 hooks 注入；缺省时使用引擎传入的组件。
    """

    def __init__(
        self,
        *,
        npc_system: Any,
        location_system: Any | None = None,
        economy_system: Any | None = None,
        relation_system: Any | None = None,
        event_system: Any,
        commit: Callable[[GameState], None] | None = None,
        seed: int | None = None,
    ) -> None:
        self.npc_system = npc_system
        self.location_system = location_system
        self.economy_system = economy_system
        self.relation_system = relation_system
        self.event_system = event_system
        self.commit = commit or (lambda _s: None)

    def run(self, state: GameState, *, minutes: int = 0, hours: int = 0, days: int = 0) -> None:
        # 1. 时间推进
        TimeSystem.advance(state, minutes=minutes, hours=hours, days=days)

        # 2. NPC 行动
        self.npc_system.tick(state)

        # 3. 地点变化
        if self.location_system is not None:
            self.location_system.tick(state)

        # 4. 经济变化
        if self.economy_system is not None:
            self.economy_system.tick(state)

        # 5. 关系演化（每日一次：自然升温/降温）
        if self.relation_system is not None:
            self.relation_system.tick(state)

        # 6. 事件检查
        self.event_system.auto_advance(state)

        # 7. 状态提交（存档由外层 Engine 统一处理）
        self.commit(state)