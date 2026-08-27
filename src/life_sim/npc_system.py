from __future__ import annotations

from .models import GameState, NPC, NPCScheduleEntry


class NPCSystem:
    def __init__(self, npcs: dict[str, NPC], schedule_templates: dict | None = None) -> None:
        self.templates = npcs
        self.schedule_templates = schedule_templates or {}

    @classmethod
    def from_data(cls, data: list[dict]) -> NPCSystem:
        return cls({npc.id: npc for npc in (npc_from_data(item) for item in data)})

    def load_schedules(self) -> None:
        """V0.15.2：加载 data/schedules.json 时间片日程模板。"""
        from .npc.schedule import load_schedule_templates

        self.schedule_templates = load_schedule_templates(self)

    def create_state(self) -> dict[str, NPC]:
        return {
            npc_id: NPC(
                id=npc.id,
                name=npc.name,
                job=npc.job,
                goal=npc.goal,
                home=npc.home,
                location=npc.location,
                job_location=npc.job_location,
                fatigue=npc.fatigue,
                money=npc.money,
                trust=npc.trust,
                current_time=npc.current_time,
                current_activity=npc.current_activity,
                schedule=list(npc.schedule),
                weekend_schedule=list(npc.weekend_schedule),
                relationship=dict(npc.relationship),
                state=npc.state,
                needs=npc.needs,
                schedule_id=npc.schedule_id,
            )
            for npc_id, npc in self.templates.items()
        }

    def tick(self, state: GameState) -> None:
        self.ensure_npcs(state)
        week_index = state.days_lived % 7
        hour = state.date.hour
        date_key = (
            f"{state.date.year}-{state.date.month:02d}-{state.date.day:02d}"
        )
        for npc in state.npcs.values():
            if npc.disappeared:
                continue  # 失踪者不再按日程活动
            # V0.15.2：使用时间片日程（若该 NPC 配了 schedule_id）
            if npc.schedule_id and npc.schedule_id in self.schedule_templates:
                self._apply_schedule2(npc, state, week_index, hour, date_key)
                continue
            # 旧 7 天循环日程（兼容）
            if npc.is_weekend(week_index) and npc.weekend_schedule:
                entries = npc.weekend_schedule
            else:
                entries = npc.schedule
            if not entries:
                continue
            entry = entries[week_index % len(entries)]
            npc.apply_schedule_entry(entry)
            self.evolve_needs(npc, days=1)

    def _apply_schedule2(
        self, npc: NPC, state: GameState, week_index: int, hour: int, date_key: str
    ) -> None:
        """按时间片日程 + 行为候选推进 NPC（V0.15.2 + V0.15.3）。

        一天 = 模板时间线上所有关键时刻依次执行；
        每个时刻先查日程默认行为，再经 Behavior Candidate 决策（需求/状态/目标/世界加权）——
        NPC 可能因疲劳过高、生病、缺钱而改变计划。
        """
        from .npc.behavior import decide_behavior
        from .npc.schedule import ACTIVITY_LOCATIONS, ACTIVITY_NAMES
        from .npc.effects import apply_result, build_result

        template = self.schedule_templates[npc.schedule_id]
        is_rest = npc.is_weekend(week_index)
        timeline = template.rest_day if is_rest else template.weekday
        special = template.special.get(date_key)
        if special is not None:
            timeline = special

        timeline_hours = sorted(timeline.timeline.keys())
        if not timeline_hours:
            return
        for t_hour in timeline_hours:
            scheduled = timeline.timeline[t_hour]  # 日程默认
            action_id, _candidates = decide_behavior(
                npc,
                schedule_action=scheduled,
                needs=npc.needs,
                state=npc.state,
                is_night=state.date.is_night(),
                city_tension=state.world.city.get("tension", 0),
                day_index=state.days_lived,
            )

            npc.current_time = f"{t_hour:02d}:00"
            npc.current_activity = ACTIVITY_NAMES.get(action_id, action_id)
            # 行为结果统一走 EffectSystem 风格：build → apply
            loc_name_map = {"market": "市场区", "tavern": "北区", "street": "北区",
                            "church": "黑夜教堂", "canteen": "市场区", "other_home": "东区"}
            result = build_result(
                npc, action_id,
                prev_location=npc.location,
                hours=1.0,
                loc_type_map=ACTIVITY_LOCATIONS,
                loc_name_map=loc_name_map,
            )
            # 未落到具体位置时按类型映射兜底
            if result.to_location is None:
                loc_type = ACTIVITY_LOCATIONS.get(action_id)
                result.to_location = self._loc_for_type(loc_type) or npc.home
            # work/shop 等提高对应地点活跃度
            if action_id in ("work", "shop", "socialize", "visit"):
                result.location_activity_delta = 3
            apply_result(state, npc, result)
            self.evolve_needs(npc, days=0.2, guarantee_meal=False)

    _LOC_TYPE_MAP = None

    def _loc_for_type(self, loc_type: str | None) -> str | None:
        if loc_type is None:
            return None
        if self._LOC_TYPE_MAP is None:
            self._LOC_TYPE_MAP = {
                "market": "市场区",
                "tavern": "北区",
                "street": "北区",
                "church": "黑夜教堂",
                "canteen": "市场区",
                "other_home": "东区",
            }
        return self._LOC_TYPE_MAP.get(loc_type)

    def evolve_needs(self, npc: NPC, days: float = 1.0, guarantee_meal: bool = True) -> None:
        """需求每日演化：需求随时间增长，日常活动满足对应需求。

        - drift：饥饿/休息/社交自然累积（会饿会累）
        - satisfy：当天日程里的进食/休息/社交活动返还需求
        - guarantee_meal：整日结算时若当天无进食活动，兜底吃一顿（防饿死）；
          时刻级调用（Schedule 2.0 逐步推进）不兜底，只按真实活动满足。
        """
        from .npc.needs import apply_activity, drift_needs

        if npc.needs is None:
            return
        drift_needs(npc.needs, hours=days * 6)
        activity = npc.current_activity or ""
        mapped = None
        if any(k in activity for k in ("吃", "午", "晚", "饭", "餐")):
            mapped = "eat"
        elif any(k in activity for k in ("睡", "休息", "回家", "睡下", "补觉", "打烊")):
            mapped = "rest"
        elif any(k in activity for k in ("聊", "社交", "朋友", "酒", "客人")):
            mapped = "socialize"
        elif any(k in activity for k in ("买", "市场", "采买")):
            mapped = "shop"
        # 兜底：整日结算且当天无进食活动时，补一次进食（无人会饿死）
        if mapped is None and guarantee_meal:
            mapped = "eat"
        if mapped:
            apply_activity(npc.needs, None, mapped, hours=1)
        # 睡眠是刚需：当 rest 需求过高时强制补休
        if npc.needs.rest > 85:
            apply_activity(npc.needs, None, "rest", hours=2)

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
    trust = int(data.get("trust", 0))
    relationship = dict(
        data.get(
            "relationship",
            {"trust": trust, "friendship": 0, "fear": 0},
        )
    )
    relationship.setdefault("trust", trust)
    return NPC(
        id=data["id"],
        name=data["name"],
        job=data["job"],
        goal=data["goal"],
        home=data["home"],
        location=data.get("location", data["home"]),
        job_location=data.get("job_location"),
        fatigue=int(data.get("fatigue", 30)),
        money=int(data.get("money", 0)),
        trust=trust,
        current_time=current.time if current else data.get("current_time", "08:00"),
        current_activity=current.activity if current else data.get("current_activity", "开始一天"),
        schedule=schedule,
        weekend_schedule=weekend_schedule,
        disappeared=bool(data.get("disappeared", False)),
        disappeared_day=data.get("disappeared_day"),
        relationship=relationship,
        schedule_id=data.get("schedule_id"),
    )
