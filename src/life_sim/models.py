from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldDate:
    era: str = "第五纪"
    year: int = 1348
    month: int = 1
    day: int = 1
    hour: int = 8
    minute: int = 0

    HOURS_PER_DAY = 24
    MINUTES_PER_HOUR = 60
    DAYS_PER_MONTH = 30

    def advance_days(self, days: int = 1) -> None:
        self.advance_minutes(days * self.HOURS_PER_DAY * self.MINUTES_PER_HOUR)

    def advance_minutes(self, minutes: int) -> None:
        total = (
            ((self.day - 1) * self.HOURS_PER_DAY + self.hour) * self.MINUTES_PER_HOUR
            + self.minute
            + minutes
        )
        if total < 0:
            total = 0
        day_index, minute_of_day = divmod(total, self.HOURS_PER_DAY * self.MINUTES_PER_HOUR)
        self.hour, self.minute = divmod(minute_of_day, self.MINUTES_PER_HOUR)
        # day_index 是自第 1 天开始的增量
        self.day = 1 + day_index
        while self.day > self.DAYS_PER_MONTH:
            self.day -= self.DAYS_PER_MONTH
            self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1

    def advance_hours(self, hours: int) -> None:
        self.advance_minutes(hours * self.MINUTES_PER_HOUR)

    def is_night(self) -> bool:
        return self.hour >= 21 or self.hour < 5

    def label(self) -> str:
        return f"{self.era} {self.year}年{self.month}月{self.day}日"

    def label_full(self) -> str:
        return f"{self.label()} {self.hour:02d}:{self.minute:02d}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "era": self.era,
            "year": self.year,
            "month": self.month,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldDate:
        return cls(
            era=data.get("era", "第五纪"),
            year=int(data.get("year", 1348)),
            month=int(data.get("month", 1)),
            day=int(data.get("day", 1)),
            hour=int(data.get("hour", 8)),
            minute=int(data.get("minute", 0)),
        )


@dataclass
class Character:
    name: str
    age: int
    gender: str
    birthplace: str
    family: str
    job: str = "无业"
    location: str = "廷根"
    health: int = 80
    stamina: int = 70
    intelligence: int = 55
    charisma: int = 50
    money: int = 120
    savings: int = 0
    stress: int = 20
    mysticism_knowledge: int = 0
    spirituality: int = 5
    corruption: int = 0
    madness: int = 0
    tags: list[str] = field(default_factory=list)

    def clamp(self) -> None:
        for field_name in [
            "health",
            "stamina",
            "intelligence",
            "charisma",
            "stress",
            "mysticism_knowledge",
            "spirituality",
            "corruption",
            "madness",
        ]:
            value = getattr(self, field_name)
            setattr(self, field_name, max(0, min(100, value)))
        self.money = max(0, self.money)
        self.savings = max(0, self.savings)

    def apply_changes(self, changes: dict[str, int]) -> None:
        for key, delta in changes.items():
            if not hasattr(self, key):
                continue
            current = getattr(self, key)
            if isinstance(current, int):
                setattr(self, key, current + delta)
        self.clamp()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "birthplace": self.birthplace,
            "family": self.family,
            "job": self.job,
            "location": self.location,
            "health": self.health,
            "stamina": self.stamina,
            "intelligence": self.intelligence,
            "charisma": self.charisma,
            "money": self.money,
            "savings": self.savings,
            "stress": self.stress,
            "mysticism_knowledge": self.mysticism_knowledge,
            "spirituality": self.spirituality,
            "corruption": self.corruption,
            "madness": self.madness,
            "tags": list(self.tags),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Character:
        return cls(
            name=data["name"],
            age=int(data["age"]),
            gender=data["gender"],
            birthplace=data["birthplace"],
            family=data["family"],
            job=data.get("job", "无业"),
            location=data.get("location", "廷根"),
            health=int(data.get("health", 80)),
            stamina=int(data.get("stamina", 70)),
            intelligence=int(data.get("intelligence", 55)),
            charisma=int(data.get("charisma", 50)),
            money=int(data.get("money", 120)),
            savings=int(data.get("savings", 0)),
            stress=int(data.get("stress", 20)),
            mysticism_knowledge=int(data.get("mysticism_knowledge", 0)),
            spirituality=int(data.get("spirituality", 5)),
            corruption=int(data.get("corruption", 0)),
            madness=int(data.get("madness", 0)),
            tags=list(data.get("tags", [])),
        )


@dataclass
class JournalEntry:
    date: str
    action: str
    summary: str
    changes: dict[str, int] = field(default_factory=dict)
    event: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "action": self.action,
            "summary": self.summary,
            "changes": self.changes,
            "event": self.event,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> JournalEntry:
        return cls(
            date=data["date"],
            action=data["action"],
            summary=data["summary"],
            changes=dict(data.get("changes", {})),
            event=data.get("event"),
        )


@dataclass
class NPCScheduleEntry:
    time: str
    location: str
    activity: str
    fatigue_change: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "time": self.time,
            "location": self.location,
            "activity": self.activity,
            "fatigue_change": self.fatigue_change,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NPCScheduleEntry:
        return cls(
            time=data["time"],
            location=data["location"],
            activity=data["activity"],
            fatigue_change=int(data.get("fatigue_change", 0)),
        )


@dataclass
class NPC:
    id: str
    name: str
    job: str
    goal: str
    home: str
    location: str
    job_location: str | None = None   # 工作地点（Schedule 2.0 用）
    fatigue: int = 30
    money: int = 0
    current_time: str = "08:00"
    current_activity: str = "开始一天"
    schedule: list[NPCScheduleEntry] = field(default_factory=list)
    weekend_schedule: list[NPCScheduleEntry] = field(default_factory=list)
    disappeared: bool = False
    disappeared_day: int | None = None
    relationship: dict[str, int] = field(
        default_factory=lambda: {"trust": 0, "friendship": 0, "fear": 0}
    )
    trust: int = field(default=0, init=False, repr=False)
    state: Any = None      # NPCState（延迟赋值避免循环 import）
    needs: Any = None      # NPCNeeds
    schedule_id: str | None = None  # V0.15.2：ScheduleTemplate id（若设置则用时间片日程）

    @property
    def friendship(self) -> int:
        return self.relationship.get("friendship", 0)

    @property
    def fear(self) -> int:
        return self.relationship.get("fear", 0)

    @property
    def trust(self) -> int:
        return self.relationship.get("trust", 0)

    @trust.setter
    def trust(self, value: int) -> None:
        self.relationship["trust"] = max(0, min(100, int(value)))

    def __post_init__(self) -> None:
        if "trust" not in self.relationship or self.relationship["trust"] == 0:
            self.relationship["trust"] = max(0, min(100, self.trust))
        # V0.15.1：初始化状态/需求（延迟 import 避免循环）
        if self.state is None:
            from .npc.models import NPCState

            self.state = NPCState(health=100, fatigue=self.fatigue, money=float(self.money))
        if self.needs is None:
            from .npc.models import NPCNeeds

            self.needs = NPCNeeds(rest=self.fatigue if self.fatigue > 30 else 30)

    def clamp(self) -> None:
        self.fatigue = max(0, min(100, self.fatigue))
        for key in ("trust", "friendship", "fear"):
            self.relationship[key] = max(0, min(100, self.relationship.get(key, 0)))

    def set_trust(self, amount: int) -> None:
        """同步信任到 relationship（便捷）。"""
        self.relationship["trust"] = max(0, min(100, amount))

    def add_trust(self, amount: int) -> None:
        self.relationship["trust"] = max(
            0, min(100, self.relationship.get("trust", 0) + amount)
        )

    def add_friendship(self, amount: int) -> None:
        self.relationship["friendship"] = max(
            0, min(100, self.relationship.get("friendship", 0) + amount)
        )

    def add_fear(self, amount: int) -> None:
        self.relationship["fear"] = max(
            0, min(100, self.relationship.get("fear", 0) + amount)
        )

    def is_weekend(self, day: int) -> bool:
        """day 0-6 对应周一..周日；5(周六)、6(周日) 为休息日。"""
        return day in (5, 6)

    def apply_schedule_entry(self, entry: NPCScheduleEntry) -> None:
        self.current_time = entry.time
        self.location = entry.location
        self.current_activity = entry.activity
        # V0.15.1：日程疲劳变化写入 state.fatigue（源头），旧字段同步
        if self.state is not None:
            self.state.fatigue = max(
                0, min(100, self.state.fatigue + entry.fatigue_change)
            )
        self.fatigue += entry.fatigue_change
        if self.state is not None:
            self.fatigue = self.state.fatigue
        self.clamp()

    def to_dict(self) -> dict[str, Any]:
        result = {
            "id": self.id,
            "name": self.name,
            "job": self.job,
            "goal": self.goal,
            "home": self.home,
            "location": self.location,
            "fatigue": self.fatigue,
            "money": self.money,
            "trust": self.trust,
            "current_time": self.current_time,
            "current_activity": self.current_activity,
            "schedule": [entry.to_dict() for entry in self.schedule],
            "weekend_schedule": [entry.to_dict() for entry in self.weekend_schedule],
            "disappeared": self.disappeared,
            "disappeared_day": self.disappeared_day,
            "relationship": dict(self.relationship),
        }
        if self.job_location is not None:
            result["job_location"] = self.job_location
        if self.state is not None:
            result["state"] = self.state.to_dict()
        if self.needs is not None:
            result["needs"] = self.needs.to_dict()
        if self.schedule_id is not None:
            result["schedule_id"] = self.schedule_id
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NPC:
        from .npc.models import NPCNeeds, NPCState

        obj = cls(
            id=data["id"],
            name=data["name"],
            job=data["job"],
            goal=data["goal"],
            home=data["home"],
            location=data.get("location", data["home"]),
            job_location=data.get("job_location"),
            fatigue=int(data.get("fatigue", 30)),
            money=int(data.get("money", 0)),
            trust=int(data.get("trust", 0)),
            current_time=data.get("current_time", "08:00"),
            current_activity=data.get("current_activity", "开始一天"),
            schedule=[
                NPCScheduleEntry.from_dict(entry) for entry in data.get("schedule", [])
            ],
            weekend_schedule=[
                NPCScheduleEntry.from_dict(entry)
                for entry in data.get("weekend_schedule", [])
            ],
            disappeared=bool(data.get("disappeared", False)),
            disappeared_day=data.get("disappeared_day"),
            relationship=dict(
                data.get(
                    "relationship",
                    {"trust": data.get("trust", 0), "friendship": 0, "fear": 0},
                )
            ),
            schedule_id=data.get("schedule_id"),
        )
        # V0.15.1：读档优先取存档里的 state/needs，缺省用迁移默认
        if "state" in data:
            obj.state = NPCState.from_dict(data["state"])
            obj.state.money = float(data.get("money", obj.state.money))
        if "needs" in data:
            obj.needs = NPCNeeds.from_dict(data["needs"])
        # 旧存档：fatigue/money 已由 __post_init__ 迁移进 state
        obj.fatigue = obj.state.fatigue
        obj.money = int(obj.state.money)
        return obj


@dataclass
class WorldState:
    date: WorldDate = field(default_factory=WorldDate)
    weather: str = "阴天"
    economy: dict[str, int] = field(default_factory=lambda: {"pressure": 0})
    city: dict[str, int] = field(default_factory=lambda: {"tension": 0})
    organizations: dict[str, dict[str, int]] = field(
        default_factory=lambda: {
            "黑夜教会": {"attention": 0},
            "暗流组织": {"activity": 0},
        }
    )
    event_nodes: dict[str, str] = field(default_factory=dict)
    event_last_triggered: dict[str, int] = field(default_factory=dict)
    expired_traced: dict[str, int] = field(default_factory=dict)
    locations: dict[str, dict[str, int]] = field(default_factory=dict)
    npcs: dict[str, NPC] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.to_dict(),
            "weather": self.weather,
            "economy": dict(self.economy),
            "city": dict(self.city),
            "organizations": {
                name: dict(values) for name, values in self.organizations.items()
            },
            "event_nodes": dict(self.event_nodes),
            "event_last_triggered": dict(self.event_last_triggered),
            "expired_traced": dict(self.expired_traced),
            "locations": {
                name: dict(values) for name, values in self.locations.items()
            },
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldState:
        result = cls(
            date=WorldDate.from_dict(data.get("date", {})),
            weather=data.get("weather", "阴天"),
            economy=dict(data.get("economy", {"pressure": 0})),
            city=dict(data.get("city", {"tension": 0})),
            organizations=dict(data.get("organizations", {})),
            event_nodes=dict(data.get("event_nodes", {})),
            event_last_triggered=dict(data.get("event_last_triggered", {})),
            expired_traced=dict(data.get("expired_traced", {})),
            locations={
                name: dict(values)
                for name, values in data.get("locations", {}).items()
            },
            npcs={
                npc_id: NPC.from_dict(npc)
                for npc_id, npc in data.get("npcs", {}).items()
            },
        )
        # 兼容旧存档：确保组织键存在
        for org, default in (
            ("黑夜教会", {"attention": 0}),
            ("暗流组织", {"activity": 0}),
        ):
            result.organizations.setdefault(org, dict(default))
        return result


@dataclass
class GameState:
    character: Character
    world: WorldState = field(default_factory=WorldState)
    journal: list[JournalEntry] = field(default_factory=list)
    days_lived: int = 0
    clues: list[str] = field(default_factory=list)
    deductions: list[str] = field(default_factory=list)
    focused_contact: str | None = None

    @property
    def date(self) -> WorldDate:
        return self.world.date

    @property
    def event_nodes(self) -> dict[str, str]:
        return self.world.event_nodes

    @property
    def npcs(self) -> dict[str, NPC]:
        return self.world.npcs

    def to_dict(self) -> dict[str, Any]:
        return {
            "character": self.character.to_dict(),
            "world": self.world.to_dict(),
            "journal": [entry.to_dict() for entry in self.journal],
            "days_lived": self.days_lived,
            "clues": list(self.clues),
            "deductions": list(self.deductions),
            "focused_contact": self.focused_contact,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> GameState:
        world_data = data.get("world", {})
        if "date" in data and "date" not in world_data:
            world_data = {
                **world_data,
                "date": data.get("date", {}),
                "event_nodes": data.get("event_nodes", {}),
                "npcs": data.get("npcs", {}),
            }
        return cls(
            character=Character.from_dict(data["character"]),
            world=WorldState.from_dict(world_data),
            journal=[
                JournalEntry.from_dict(entry) for entry in data.get("journal", [])
            ],
            days_lived=int(data.get("days_lived", 0)),
            clues=list(data.get("clues", [])),
            deductions=list(data.get("deductions", [])),
            focused_contact=data.get("focused_contact"),
        )
