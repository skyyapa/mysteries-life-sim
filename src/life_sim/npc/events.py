"""NPC 世界事件钩子系统（V0.15.6）。

规格目标：NPC 行为/异常产生"世界事件"，未来 V0.16 事件图可监听——
    NPC_MISSING → 失踪案件事件图 → 朋友发现 → 警察调查 → 玩家可能接触。

设计：
- WorldEventBus：发布 + 订阅（V0.16 事件图可注册监听器）
- 每次要紧行为/异常发布事件，记录事件日志（可调试）
- 异常基线：NPC 本该工作却缺勤（生病/压力爆表）→ NPC_ABSENT_FROM_WORK
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

# 事件名常量
EV_NPC_ARRIVED = "NPC_ARRIVED"
EV_NPC_WORKED = "NPC_WORKED"
EV_NPC_ABSENT = "NPC_ABSENT_FROM_WORK"
EV_NPC_MISSING = "NPC_MISSING"
EV_NPC_SICK = "NPC_SICK"
EV_NPC_INTERACTION = "NPC_INTERACTION"
EV_NPC_NEW_GOAL = "NPC_NEW_GOAL"


@dataclass
class WorldEvent:
    """一条事件钩子记录（可调试 + V0.16 事件图消费）。

    事件会写明：谁、什么时候、在哪、为什么、附加数据。
    """

    kind: str
    npc_id: str
    day: int
    location: str | None = None
    reason: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        loc = f"@{self.location}" if self.location else ""
        why = f" [{self.reason}]" if self.reason else ""
        return f"[{self.day}天] {self.kind} {self.npc_id}{loc}{why}"


class WorldEventBus:
    """世界事件总线：NPC/系统发布事件，V0.16 事件图订阅。"""

    def __init__(self) -> None:
        self._history: list[WorldEvent] = []
        self._listeners: dict[str, list[Callable[[WorldEvent], None]]] = {}

    def publish(self, event: WorldEvent) -> None:
        self._history.append(event)
        if len(self._history) > 500:
            self._history = self._history[-500:]
        for listener in self._listeners.get(event.kind, []):
            try:
                listener(event)
            except Exception:
                pass  # 监听器失败不阻断世界

    def subscribe(self, kind: str, listener: Callable[[WorldEvent], None]) -> None:
        self._listeners.setdefault(kind, []).append(listener)

    def history(self, kind: str | None = None, limit: int = 50) -> list[WorldEvent]:
        events = self._history if kind is None else [e for e in self._history if e.kind == kind]
        return events[-limit:]

    def recent(self, npc_id: str, limit: int = 20) -> list[WorldEvent]:
        return [e for e in self._history if e.npc_id == npc_id][-limit:]

    def clear(self) -> None:
        self._history.clear()


# 全局单例（一个世界一个总线；WorldEngine 持有）
_bus: WorldEventBus | None = None


def get_bus() -> WorldEventBus:
    global _bus
    if _bus is None:
        _bus = WorldEventBus()
    return _bus


def reset_bus() -> None:
    global _bus
    _bus = WorldEventBus()