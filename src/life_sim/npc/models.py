"""NPC 数据模型（V0.15.1）。

升级 NPC 从"联系人"到"有状态的生命"：
- NPCState：身体/情绪/财务状况
- NPCNeeds：需求（驱赶行为变化的关键）
- NPCRelationship：关系四维（trust/familiarity/affection/fear）

原则：NPC 静态资料（姓名/职业/默认日程）不随存档复制，
存档只保存**发生变化的状态**（见 npc/system.py 与 save.py）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NPCState:
    """NPC 当前状态（0-100 数值，100=完美）。"""

    health: int = 100
    fatigue: int = 0      # 高=累
    stress: int = 0
    mood: int = 50
    money: float = 0.0
    sick: bool = False
    injured: bool = False
    missing: bool = False
    alive: bool = True

    def clamp(self) -> None:
        self.health = max(0, min(100, self.health))
        self.fatigue = max(0, min(100, self.fatigue))
        self.stress = max(0, min(100, self.stress))
        self.mood = max(0, min(100, self.mood))
        self.money = max(0.0, self.money)

    def to_dict(self) -> dict[str, Any]:
        return {
            "health": self.health,
            "fatigue": self.fatigue,
            "stress": self.stress,
            "mood": self.mood,
            "money": self.money,
            "sick": self.sick,
            "injured": self.injured,
            "missing": self.missing,
            "alive": self.alive,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NPCState":
        out = cls(
            health=int(data.get("health", 100)),
            fatigue=int(data.get("fatigue", 0)),
            stress=int(data.get("stress", 0)),
            mood=int(data.get("mood", 50)),
            money=float(data.get("money", 0.0)),
            sick=bool(data.get("sick", False)),
            injured=bool(data.get("injured", False)),
            missing=bool(data.get("missing", False)),
            alive=bool(data.get("alive", True)),
        )
        out.clamp()
        return out


@dataclass
class NPCNeeds:
    """NPC 需求（0=满足，100=非常迫切）。"""

    hunger: int = 20
    rest: int = 30
    social: int = 20
    safety: int = 0
    # 经济安全需求由 state.money 换算，不单独存

    def clamp(self) -> None:
        for key in ("hunger", "rest", "social", "safety"):
            value = getattr(self, key)
            setattr(self, key, max(0, min(100, value)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "hunger": self.hunger,
            "rest": self.rest,
            "social": self.social,
            "safety": self.safety,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NPCNeeds":
        out = cls(
            hunger=int(data.get("hunger", 20)),
            rest=int(data.get("rest", 30)),
            social=int(data.get("social", 20)),
            safety=int(data.get("safety", 0)),
        )
        out.clamp()
        return out


@dataclass
class NPCRelationship:
    """NPC 对某对象（其他 NPC 或玩家）的关系四维。"""

    trust: int = 0
    familiarity: int = 0
    affection: int = 0
    fear: int = 0

    def clamp(self) -> None:
        for key in ("trust", "familiarity", "affection", "fear"):
            value = getattr(self, key)
            setattr(self, key, max(0, min(100, value)))

    def to_dict(self) -> dict[str, Any]:
        return {
            "trust": self.trust,
            "familiarity": self.familiarity,
            "affection": self.affection,
            "fear": self.fear,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NPCRelationship":
        out = cls(
            trust=int(data.get("trust", 0)),
            familiarity=int(data.get("familiarity", 0)),
            affection=int(data.get("affection", 0)),
            fear=int(data.get("fear", 0)),
        )
        out.clamp()
        return out


def migrate_relationship(old: dict[str, int] | None) -> dict[str, int]:
    """把旧版 {trust, friendship, fear} 迁移到 {trust, familiarity, affection, fear}。

    friendship 旧值 → familiarity（熟悉度），affection 用 mood 近似或 0。
    """
    old = old or {}
    return {
        "trust": int(old.get("trust", 0)),
        "familiarity": int(old.get("friendship", old.get("familiarity", 0))),
        "affection": int(old.get("affection", 0)),
        "fear": int(old.get("fear", 0)),
    }