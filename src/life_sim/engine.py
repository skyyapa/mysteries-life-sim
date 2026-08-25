from __future__ import annotations

import random
from typing import Any

from .data_loader import load_json, load_optional_json
from .event_system import EventGraph, EventNode, EventSystem
from .models import Character, GameState, JournalEntry, WorldState
from .npc_system import NPCSystem


class WorldEngine:
    """Coordinates world time, actions, and event checks."""

    def __init__(self, seed: int | None = None) -> None:
        self.random = random.Random(seed)
        self.actions: dict[str, dict[str, Any]] = load_json("actions.json")
        event_graphs = load_optional_json("event_graphs.json")
        if event_graphs is None:
            self.event_system = EventSystem.from_raw_events(load_json("events.json"))
        else:
            self.event_system = EventSystem.from_graph_data(event_graphs)
        self.npc_system = NPCSystem.from_data(load_optional_json("npcs.json") or [])

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
        return GameState(
            character=character,
            world=WorldState(npcs=self.npc_system.create_state()),
        )

    def available_actions(self) -> list[str]:
        return list(self.actions.keys())

    def tick(self, state: GameState, days: int = 1) -> None:
        for _ in range(days):
            state.days_lived += 1
            previous_year = state.date.year
            state.date.advance_days(1)
            self.update_world(state, previous_year=previous_year)

    def process_action(self, state: GameState, action_id: str) -> JournalEntry:
        if action_id not in self.actions:
            raise ValueError(f"未知行动：{action_id}")

        action = self.actions[action_id]
        changes = self.apply_action_effects(state, action)

        event_text = self.trigger_event(state)
        summary = self._build_summary(action, event_text)
        entry = JournalEntry(
            date=state.date.label(),
            action=action["name"],
            summary=summary,
            changes=changes,
            event=event_text,
        )

        state.journal.append(entry)
        self.tick(state, days=int(action.get("days", 1)))
        return entry

    def update_world(self, state: GameState, *, previous_year: int | None = None) -> None:
        if previous_year is not None and state.date.year > previous_year:
            state.character.age += 1
        self.update_weather(state)
        self.update_economy(state)
        self.update_city(state)
        self.event_system.auto_advance(state)
        self.npc_system.tick(state)

    def update_weather(self, state: GameState) -> None:
        weathers = ["阴天", "小雨", "雾", "晴朗"]
        state.world.weather = weathers[state.days_lived % len(weathers)]

    def update_economy(self, state: GameState) -> None:
        pressure = state.world.economy.get("pressure", 0)
        if state.character.money < 40:
            pressure += 1
        else:
            pressure -= 1
        state.world.economy["pressure"] = max(0, min(100, pressure))

    def update_city(self, state: GameState) -> None:
        pressure = state.world.economy.get("pressure", 0)
        church_attention = state.world.organizations["黑夜教会"].get("attention", 0)
        state.world.city["tension"] = max(
            0,
            min(100, int(pressure * 0.5 + state.character.stress * 0.3 + church_attention * 0.2)),
        )

    def trigger_event(self, state: GameState) -> str | None:
        selected = self.select_event(state)
        if selected is None:
            return None

        graph, node = selected
        return self.apply_event_effects(state, graph, node)

    def auto_action(self, state: GameState) -> str:
        character = state.character
        if character.health < 45 or character.stamina < 35:
            return "rest"
        if character.money < 60:
            return "work"
        if character.stress > 70:
            return "social"
        return self.random.choice(["study", "work", "rest", "social", "wander"])

    def apply_action_effects(
        self, state: GameState, action: dict[str, Any]
    ) -> dict[str, int]:
        changes = dict(action.get("effects", {}))
        state.character.apply_changes(changes)
        return changes

    def select_event(self, state: GameState) -> tuple[EventGraph, EventNode] | None:
        candidates = self.event_system.available_nodes(state)
        if not candidates:
            return None

        weighted = []
        for graph, node in candidates:
            if node.chance <= 0:
                continue
            weighted.extend([(graph, node)] * node.weight)
        if not weighted:
            return None

        graph, node = self.random.choice(weighted)
        chance = node.chance
        if self.random.randint(1, 100) > chance:
            return None

        return graph, node

    def apply_event_effects(
        self, state: GameState, graph: EventGraph, node: EventNode
    ) -> str:
        return self.event_system.apply(graph, node, state)

    def _build_summary(self, action: dict[str, Any], event_text: str | None) -> str:
        text = action["summary"]
        if event_text:
            return f"{text} {event_text}"
        return text


class LifeEngine(WorldEngine):
    def take_action(self, state: GameState, action_id: str) -> JournalEntry:
        return self.process_action(state, action_id)
