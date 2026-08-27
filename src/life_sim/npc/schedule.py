"""NPC 日程系统（V0.15.2 Schedule 2.0）。

日程从"7 天循环数组"升级为"时刻 → 行为"的规则表：
- weekday / rest_day：工作日与休息日各自的时间表
- special：特殊日期覆盖（节日/纪念日/异常日），如 {"date": "1348-05-01", "timeline": {...}}
- 查找：给定时刻(hour)，返回该时刻应执行的行为（最近不晚于的时刻）

行为 id 与 needs.py 的 ACTIVITY_EFFECTS 对应，位置由行为/模板决定。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# 行为 id → 该行为所属的"位置类型"（未来接 location 联动）
ACTIVITY_LOCATIONS = {
    "wake": "home",
    "breakfast": "home",
    "lunch": "canteen",
    "dinner": "home",
    "work": "workplace",
    "rest": "home",
    "sleep": "home",
    "go_home": "home",
    "shop": "market",
    "socialize": "tavern",
    "wander": "street",
    "visit": "other_home",
    "pray": "church",
    "stay_home": "home",
}

# 人类可读的行为名（日志/界面）
ACTIVITY_NAMES = {
    "wake": "醒来", "breakfast": "吃早餐", "lunch": "吃午饭", "dinner": "吃晚饭",
    "work": "工作", "rest": "休息", "sleep": "入睡", "go_home": "回家",
    "shop": "购物", "socialize": "社交", "wander": "闲逛", "visit": "拜访",
    "pray": "祈祷", "stay_home": "待在家里",
}


@dataclass
class Schedule2:
    """一天的时间表：{时刻: 行为}。时刻/分钟归一，查找最近不晚于的时刻。"""

    timeline: dict[int, str] = field(default_factory=dict)  # {hour: activity_id}

    def activity_at(self, hour: int) -> str | None:
        """返回 hour 时刻应执行的行为（取 ≤ hour 的最近时刻）。"""
        if not self.timeline:
            return None
        keys = sorted(k for k in self.timeline if k <= hour)
        if not keys:
            return None
        return self.timeline[keys[-1]]

    def to_dict(self) -> dict[str, Any]:
        return {str(k): v for k, v in sorted(self.timeline.items())}

    @classmethod
    def from_dict(cls, data: Any) -> "Schedule2":
        if not data:
            return cls()
        timeline: dict[int, str] = {}
        for key, value in (data.items() if isinstance(data, dict) else []):
            try:
                hour = int(key.split(":")[0])
            except (ValueError, AttributeError):
                continue
            timeline[hour] = value
        return cls(timeline=timeline)


@dataclass
class ScheduleTemplate:
    """一整套 NPC 日程：工作日/休息日 + 特殊日覆盖。"""

    id: str
    weekday: Schedule2 = field(default_factory=Schedule2)
    rest_day: Schedule2 = field(default_factory=Schedule2)
    special: dict[str, Schedule2] = field(default_factory=dict)  # {"1348-05-01": Schedule2}

    def for_day(
        self, *, hour: int, is_rest_day: bool, date_key: str | None = None
    ) -> str | None:
        """返回某天某时刻的行为。

        优先级：特殊日覆盖 > 工作日/休息日。
        """
        sched = self.special.get(date_key) if date_key else None
        if sched is None:
            sched = self.rest_day if is_rest_day else self.weekday
        return sched.activity_at(hour)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "weekday": self.weekday.to_dict(),
            "rest_day": self.rest_day.to_dict(),
            "special": {k: v.to_dict() for k, v in self.special.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScheduleTemplate":
        return cls(
            id=data["id"],
            weekday=Schedule2.from_dict(data.get("weekday")),
            rest_day=Schedule2.from_dict(data.get("rest_day")),
            special={
                k: Schedule2.from_dict(v)
                for k, v in data.get("special", {}).items()
            },
        )


def load_schedule_templates(system: Any) -> dict[str, ScheduleTemplate]:
    """从 data/schedules/*.json 加载全部日程模板。"""
    from ..data_loader import load_optional_json

    data = load_optional_json("schedules.json")
    templates: dict[str, ScheduleTemplate] = {}
    if data:
        for item in data:
            tpl = ScheduleTemplate.from_dict(item)
            templates[tpl.id] = tpl
    return templates