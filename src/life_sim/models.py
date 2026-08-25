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
    stress: int = 20
    mysticism_knowledge: int = 0
    spirituality: int = 5
    corruption: int = 0
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
        ]:
            value = getattr(self, field_name)
            setattr(self, field_name, max(0, min(100, value)))
        self.money = max(0, self.money)

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
            "stress": self.stress,
            "mysticism_knowledge": self.mysticism_knowledge,
            "spirituality": self.spirituality,
            "corruption": self.corruption,
            "tags": list(self.tags),
        }


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


@dataclass
class GameState:
    date: WorldDate
    character: Character
    journal: list[JournalEntry] = field(default_factory=list)
    days_lived: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date.to_dict(),
            "character": self.character.to_dict(),
            "journal": [entry.to_dict() for entry in self.journal],
            "days_lived": self.days_lived,
        }
