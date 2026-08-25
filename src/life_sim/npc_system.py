from __future__ import annotations

from .models import GameState, NPC, NPCScheduleEntry


class NPCSystem:
    def __init__(self, npcs: dict[str, NPC]) -> None:
        self.templates = npcs

    @classmethod
    def from_data(cls, data: list[dict]) -> NPCSystem:
        return cls({npc.id: npc for npc in (npc_from_data(item) for item in data)})

    def create_state(self) -> dict[str, NPC]:
        return {
            npc_id: NPC(
                id=npc.id,
                name=npc.name,
                job=npc.job,
                goal=npc.goal,
                home=npc.home,
                location=npc.location,
                fatigue=npc.fatigue,
                money=npc.money,
                current_time=npc.current_time,
                current_activity=npc.current_activity,
                schedule=list(npc.schedule),
            )
            for npc_id, npc in self.templates.items()
        }

    def tick(self, state: GameState) -> None:
        self.ensure_npcs(state)
        schedule_index = state.days_lived % self.max_schedule_length()
        for npc in state.npcs.values():
            if not npc.schedule:
                continue
            entry = npc.schedule[schedule_index % len(npc.schedule)]
            npc.apply_schedule_entry(entry)

    def ensure_npcs(self, state: GameState) -> None:
        for npc_id, npc in self.create_state().items():
            state.npcs.setdefault(npc_id, npc)

    def max_schedule_length(self) -> int:
        lengths = [len(npc.schedule) for npc in self.templates.values() if npc.schedule]
        return max(lengths, default=1)


def npc_from_data(data: dict) -> NPC:
    schedule = [
        NPCScheduleEntry(
            time=entry["time"],
            location=entry["location"],
            activity=entry["activity"],
            fatigue_change=int(entry.get("fatigue_change", 0)),
        )
        for entry in data.get("schedule", [])
    ]
    current = schedule[0] if schedule else None
    return NPC(
        id=data["id"],
        name=data["name"],
        job=data["job"],
        goal=data["goal"],
        home=data["home"],
        location=data.get("location", data["home"]),
        fatigue=int(data.get("fatigue", 30)),
        money=int(data.get("money", 0)),
        current_time=current.time if current else data.get("current_time", "08:00"),
        current_activity=current.activity if current else data.get("current_activity", "开始一天"),
        schedule=schedule,
    )
