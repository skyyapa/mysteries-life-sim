from __future__ import annotations

import random
from typing import Any

from .data_loader import load_json
from .models import Character, GameState, JournalEntry, WorldDate


class LifeEngine:
    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)
        self.actions: dict[str, dict[str, Any]] = load_json("actions.json")
        self.events: list[dict[str, Any]] = load_json("events.json")

    def new_game(self, name: str = "埃文·莫里斯") -> GameState:
        character = Character(
            name=name,
            age=17,
            gender="男",
            birthplace="鲁恩王国",
            family="下层中产",
            job="文法学校学生",
            location="廷根",
        )
        return GameState(date=WorldDate(), character=character)

    def available_actions(self) -> list[str]:
        return list(self.actions.keys())

    def take_action(self, state: GameState, action_id: str) -> JournalEntry:
        if action_id not in self.actions:
            raise ValueError(f"未知行动：{action_id}")

        action = self.actions[action_id]
        changes = dict(action.get("effects", {}))
        state.character.apply_changes(changes)

        event_text = self._maybe_trigger_event(state)
        summary = self._build_summary(action, event_text)
        entry = JournalEntry(
            date=state.date.label(),
            action=action["name"],
            summary=summary,
            changes=changes,
            event=event_text,
        )

        state.journal.append(entry)
        state.days_lived += 1
        state.date.advance_days(action.get("days", 1))
        return entry

    def auto_action(self, state: GameState) -> str:
        character = state.character
        if character.health < 45 or character.stamina < 35:
            return "rest"
        if character.money < 60:
            return "work"
        if character.stress > 70:
            return "social"
        return self.random.choice(["study", "work", "rest", "social", "wander"])

    def _maybe_trigger_event(self, state: GameState) -> str | None:
        candidates = [
            event for event in self.events if self._event_conditions_met(event, state)
        ]
        if not candidates:
            return None

        weighted = []
        for event in candidates:
            weighted.extend([event] * int(event.get("weight", 1)))
        event = self.random.choice(weighted)
        chance = int(event.get("chance", 20))
        if self.random.randint(1, 100) > chance:
            return None

        state.character.apply_changes(event.get("effects", {}))
        for tag in event.get("add_tags", []):
            if tag not in state.character.tags:
                state.character.tags.append(tag)
        return event["text"]

    def _event_conditions_met(self, event: dict[str, Any], state: GameState) -> bool:
        conditions = event.get("conditions", {})
        character = state.character

        min_day = conditions.get("min_day")
        if min_day is not None and state.days_lived < min_day:
            return False

        max_day = conditions.get("max_day")
        if max_day is not None and state.days_lived > max_day:
            return False

        location = conditions.get("location")
        if location is not None and character.location != location:
            return False

        required_tag = conditions.get("tag")
        if required_tag is not None and required_tag not in character.tags:
            return False

        return True

    def _build_summary(self, action: dict[str, Any], event_text: str | None) -> str:
        text = action["summary"]
        if event_text:
            return f"{text} {event_text}"
        return text
