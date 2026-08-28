from __future__ import annotations

import random
from typing import Any

from .data_loader import load_json, load_optional_json
from .economy.system import EconomySystem
from .event_system import EventGraph, EventNode, EventSystem
from .location.system import LocationSystem
from .models import Character, GameState, JournalEntry, WorldState
from .npc_system import NPCSystem
from .relation.system import RelationshipSystem
from .world.tick import WorldTick


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
        self.npc_system.load_schedules()  # V0.15.2：加载时间片日程模板
        # V0.15.6：世界事件总线
        from .npc.events import WorldEventBus

        self.event_bus = WorldEventBus()
        self.npc_system.set_bus(self.event_bus)
        self.location_system = LocationSystem()
        self.economy_system = EconomySystem()
        self.relation_system = RelationshipSystem()
        # V0.14：世界推进唯一入口（组装各子系统）
        self.world_tick = WorldTick(
            npc_system=self.npc_system,
            location_system=self.location_system,
            economy_system=self.economy_system,
            relation_system=self.relation_system,
            event_system=self.event_system,
            commit=self._commit_state,
            seed=seed,
        )

    def _commit_state(self, state: GameState) -> None:
        """状态提交钩子（存档由外层统一调用 save_game）。"""
        pass

    def set_focused_contact(self, state: GameState, npc_id: str | None) -> bool:
        """设置深交对象；npc_id None 表示取消。返回是否成功。"""
        if npc_id is not None and npc_id not in state.npcs:
            return False
        state.focused_contact = npc_id
        return True

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

    def tick_world(self, state: GameState, *, days: int = 0, hours: int = 0) -> None:
        """V0.14 世界推进唯一入口（WorldTick.run 封装）。

        days/hours 由 TimeSystem 推进；当 days>0 时同时推进 days_lived 与跨年年龄。
        """
        if days or hours:
            for _ in range(days):
                state.days_lived += 1
                previous_year = state.date.year
                self.world_tick.run(state, days=1, hours=hours)
                if previous_year is not None and state.date.year > previous_year:
                    state.character.age += 1
        else:
            self.world_tick.run(state)

    def process_action(self, state: GameState, action_id: str) -> JournalEntry:
        if action_id not in self.actions:
            raise ValueError(f"未知行动：{action_id}")

        action = self.actions[action_id]
        changes = self.apply_action_effects(state, action)

        if action_id == "social":
            changes.update(self.apply_social_effects(state))

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

    def apply_social_effects(self, state: GameState) -> dict[str, int]:
        """社交行动：泛社交封顶 40（朋友）；选中深交对象且同地点则无封顶深交。

        NPC.location 是区域级（北区/市场区），角色在城市级（廷根）——
        玩家可在城市内各区域活动，规则引擎中同地判断一律视为可遇见。
        returns: {"social_trust": 净变化} 用于日志。
        """
        focused_id = state.focused_contact
        focused = state.npcs.get(focused_id) if focused_id else None
        changes: dict[str, int] = {"social_trust": 0}

        if focused is not None:
            focused.add_trust(3)
            changes["social_trust"] = changes.get("social_trust", 0) + 3
            changes["focused"] = 1
        else:
            for npc in state.npcs.values():
                if npc.trust < 40:
                    npc.set_trust(min(40, npc.trust + 1))
                    changes["social_trust"] = changes.get("social_trust", 0) + 1
        return changes

    def update_world(self, state: GameState, *, previous_year: int | None = None) -> None:
        if previous_year is not None and state.date.year > previous_year:
            state.character.age += 1
        self.update_weather(state)
        self.update_economy(state)
        self.update_city(state)
        self.update_madness(state)
        self.update_organizations(state)
        self.location_system.tick(state)
        self.relation_system.tick(state)
        self.tick_expired_events(state)
        self.event_system.auto_advance(state)
        self.npc_system.tick(state)

    def update_organizations(self, state: GameState) -> None:
        """组织行动层：两大组织逐日演化。

        - 黑夜教会注意度：玩家越深入异常调查（线索多、沾染异常）越受注目；
          向教会举报/坦白/求助会显著抬高；每天自然回落。
        - 暗流组织活跃度:玩家越靠近非凡（初涉非凡、做委托、加入组织）组织越活跃；
          活跃会反推城市紧张。
        """
        character = state.character
        church = state.world.organizations.setdefault("黑夜教会", {"attention": 0})
        secret = state.world.organizations.setdefault("暗流组织", {"activity": 0})

        # 教会注意度
        attention = church["attention"]
        attention -= 1  # 自然回落
        attention += min(3, max(0, len(state.clues) - 1))  # 每个线索引起注意
        if character.corruption >= 5:
            attention += 1  # 沾染异常被察觉
        if any(t in character.tags for t in ("向教会举报", "向教士坦白", "成为教会线人")):
            attention += 3
        church["attention"] = max(0, min(100, attention))

        # 暗流组织活跃度
        activity = secret["activity"]
        activity -= 1
        if any(t in character.tags for t in ("初涉非凡", "完成第二件委托", "加入神秘组织")):
            activity += 2
        if character.corruption >= 10:
            activity += 1
        secret["activity"] = max(0, min(100, activity))

        # 组织活跃反推城市紧张
        city = state.world.city
        city["tension"] = max(
            0,
            min(100, city["tension"] + (1 if secret["activity"] > 40 else 0)),
        )

    # 事件过期痕迹：耗尽时效的一次性事件留一句"错过"日志（每事件一次）
    EXPIRED_TRACES = {
        "abnormal_notice": "你后来想起，车站布告栏上那张失踪启事不知何时被撤下了。你错过了第一次读它的机会。",
        "abnormal_overlap": "你翻完旧报纸，发现那条东区失踪的短讯早已过时。线索凉了。",
        "abnormal_symbol": "你再去那条小巷，灰浆已经干透，符号再也看不见了。",
        "abnormal_followed": "那段时间过后，你再也没感受到被注视的目光。你错过了确认被跟踪的机会。",
    }

    def tick_expired_events(self, state: GameState) -> None:
        traced = state.world.expired_traced
        for graph in self.event_system.graphs.values():
            for node in graph.nodes.values():
                max_day = node.conditions.get("max_day")
                if max_day is None or node.id in traced:
                    continue
                if self._node_already_triggered(graph, node, state):
                    continue
                if state.days_lived > max_day:
                    traced[node.id] = state.days_lived
                    text = self.EXPIRED_TRACES.get(node.id)
                    if text:
                        state.journal.append(
                            JournalEntry(
                                date=state.date.label(),
                                action="错过",
                                summary=f"（错过）{text}",
                            )
                        )

    def _node_already_triggered(
        self, graph: EventGraph, node: EventNode, state: GameState
    ) -> bool:
        """节点是否已被触发过。

        - 冷却记录（池图可重复事件）命中即说明触发过
        - 链图：若链条已推进越过该节点（当前节点不是它且不是起点），说明已触发
        """
        if node.id in state.world.event_last_triggered:
            return True
        if not graph.is_pool:
            current_id = state.event_nodes.get(graph.id, graph.start_node)
            if current_id != graph.start_node and current_id != node.id:
                return True
        return False

    def update_madness(self, state: GameState) -> None:
        """非凡代价：疯狂值（隐藏）随污染上涨，压力和灵性（锚）调节。

        规则（每天漂移）：
        - corruption（污染）每 10 点 → 每日 +0.5 疯狂
        - stress 高于 60 → 每日 +0.3
        - spirituality ≥ 25（灵性作为锚）→ 每日 -0.2 压制
        - spirituality ≥ 60（强锚）→ 每日 -0.5
        """
        character = state.character
        drift = character.corruption / 10 * 0.5
        if character.stress > 60:
            drift += 0.3
        if character.spirituality >= 60:
            drift -= 0.5
        elif character.spirituality >= 25:
            drift -= 0.2
        character.madness = max(0, min(100, round(character.madness + drift)))

    def madness_stage(self, state: GameState) -> str:
        """精神状况阶段文案（隐藏数值，只给感受）。"""
        madness = state.character.madness
        if madness >= 70:
            return "濒危"
        if madness >= 40:
            return "不安"
        if madness >= 20:
            return "恍惚"
        return "平稳"

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
