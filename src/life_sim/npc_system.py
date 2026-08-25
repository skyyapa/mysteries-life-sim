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
                trust=npc.trust,
                current_time=npc.current_time,
                current_activity=npc.current_activity,
                schedule=list(npc.schedule),
                weekend_schedule=list(npc.weekend_schedule),
            )
            for npc_id, npc in self.templates.items()
        }

    def tick(self, state: GameState) -> None:
        self.ensure_npcs(state)
        week_index = state.days_lived % 7
        for npc in state.npcs.values():
            if npc.disappeared:
                continue  # 失踪者不再按日程活动
            if npc.is_weekend(week_index) and npc.weekend_schedule:
                entries = npc.weekend_schedule
            else:
                entries = npc.schedule
            if not entries:
                continue
            entry = entries[week_index % len(entries)]
            npc.apply_schedule_entry(entry)

    def disappear(self, state: GameState, npc_id: str) -> bool:
        """让 NPC 失踪：之后不再移动（诡秘消失），返回是否成功。"""
        npc = state.npcs.get(npc_id)
        if npc is None or npc.disappeared:
            return False
        npc.disappeared = True
        npc.disappeared_day = state.days_lived
        npc.current_activity = "（失踪）"
        return True

    def missing_npcs(self, state: GameState) -> list[NPC]:
        return [npc for npc in state.npcs.values() if npc.disappeared]

    def ensure_npcs(self, state: GameState) -> None:
        for npc_id, npc in self.create_state().items():
            state.npcs.setdefault(npc_id, npc)

    def max_schedule_length(self) -> int:
        lengths = [len(npc.schedule) for npc in self.templates.values() if npc.schedule]
        return max(lengths, default=1)


def npc_from_data(data: dict) -> NPC:
    def parse_entries(raw):
        return [
            NPCScheduleEntry(
                time=entry["time"],
                location=entry["location"],
                activity=entry["activity"],
                fatigue_change=int(entry.get("fatigue_change", 0)),
            )
            for entry in raw
        ]

    schedule = parse_entries(data.get("schedule", []))
    weekend_schedule = parse_entries(data.get("weekend_schedule", []))
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
        trust=int(data.get("trust", 0)),
        current_time=current.time if current else data.get("current_time", "08:00"),
        current_activity=current.activity if current else data.get("current_activity", "开始一天"),
        schedule=schedule,
        weekend_schedule=weekend_schedule,
        disappeared=bool(data.get("disappeared", False)),
        disappeared_day=data.get("disappeared_day"),
    )
