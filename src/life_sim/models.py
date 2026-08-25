from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldDate:
    era: str = "第五纪"
    year: int = 1348
    month: int = 1
    day: int = 1

    def advance_days(self, days: int = 1) -> None:
        for _ in range(days):
            self.day += 1
            if self.day > 30:
                self.day = 1
                self.month += 1
            if self.month > 12:
                self.month = 1
                self.year += 1

    def label(self) -> str:
        return f"{self.era} {self.year}年{self.month}月{self.day}日"

    def to_dict(self) -> dict[str, Any]:
        return {
            "era": self.era,
            "year": self.year,
            "month": self.month,
            "day": self.day,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldDate:
        return cls(
            era=data.get("era", "第五纪"),
            year=int(data.get("year", 1348)),
            month=int(data.get("month", 1)),
            day=int(data.get("day", 1)),
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
    fatigue: int = 30
    money: int = 0
    trust: int = 0
    current_time: str = "08:00"
    current_activity: str = "开始一天"
    schedule: list[NPCScheduleEntry] = field(default_factory=list)

    def clamp(self) -> None:
        self.fatigue = max(0, min(100, self.fatigue))
        self.trust = max(0, min(100, self.trust))

    def apply_schedule_entry(self, entry: NPCScheduleEntry) -> None:
        self.current_time = entry.time
        self.location = entry.location
        self.current_activity = entry.activity
        self.fatigue += entry.fatigue_change
        self.clamp()

    def to_dict(self) -> dict[str, Any]:
        return {
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
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> NPC:
        return cls(
            id=data["id"],
            name=data["name"],
            job=data["job"],
            goal=data["goal"],
            home=data["home"],
            location=data.get("location", data["home"]),
            fatigue=int(data.get("fatigue", 30)),
            money=int(data.get("money", 0)),
            trust=int(data.get("trust", 0)),
            current_time=data.get("current_time", "08:00"),
            current_activity=data.get("current_activity", "开始一天"),
            schedule=[
                NPCScheduleEntry.from_dict(entry) for entry in data.get("schedule", [])
            ],
        )


@dataclass
class WorldState:
    date: WorldDate = field(default_factory=WorldDate)
    weather: str = "阴天"
    economy: dict[str, int] = field(default_factory=lambda: {"pressure": 0})
    city: dict[str, int] = field(default_factory=lambda: {"tension": 0})
    organizations: dict[str, dict[str, int]] = field(
        default_factory=lambda: {"黑夜教会": {"attention": 0}}
    )
    event_nodes: dict[str, str] = field(default_factory=dict)
    event_last_triggered: dict[str, int] = field(default_factory=dict)
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
            "npcs": {npc_id: npc.to_dict() for npc_id, npc in self.npcs.items()},
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> WorldState:
        return cls(
            date=WorldDate.from_dict(data.get("date", {})),
            weather=data.get("weather", "阴天"),
            economy=dict(data.get("economy", {"pressure": 0})),
            city=dict(data.get("city", {"tension": 0})),
            organizations=dict(data.get("organizations", {"黑夜教会": {"attention": 0}})),
            event_nodes=dict(data.get("event_nodes", {})),
            event_last_triggered=dict(data.get("event_last_triggered", {})),
            npcs={
                npc_id: NPC.from_dict(npc)
                for npc_id, npc in data.get("npcs", {}).items()
            },
        )


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
