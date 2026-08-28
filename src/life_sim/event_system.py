from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .models import GameState


@dataclass(frozen=True)
class EventNode:
    id: str
    text: str
    chance: int = 20
    weight: int = 1
    effects: dict[str, int] = field(default_factory=dict)
    conditions: dict[str, Any] = field(default_factory=dict)
    add_tags: list[str] = field(default_factory=list)
    add_clues: list[str] = field(default_factory=list)
    trust_effects: dict[str, int] = field(default_factory=dict)
    cooldown: int = 0
    on_world_event: str | None = None  # V0.16：监听的世界事件类型（如 NPC_MISSING）
    # 激活条件：事件附带信息（如失踪的是 street_friend 等）
    on_world_event_cond: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EventEdge:
    from_node: str
    to_node: str
    condition: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EventGraph:
    id: str
    nodes: dict[str, EventNode]
    edges: list[EventEdge] = field(default_factory=list)
    start_node: str = "start"

    @property
    def is_pool(self) -> bool:
        """池图（普通生活）没有边，任意满足条件的节点都可触发且不推进。"""
        return not self.edges


EFFECT_ALIASES = {
    "mysticism": "mysticism_knowledge",
}


LOCATION_ALIASES = {
    "north": "北区",
    "market": "市场区",
    "church": "黑夜教堂",
    "east": "东区",
    "station": "廷根车站",
}

SEASONS = {
    "winter": {12, 1, 2},
    "spring": {3, 4, 5},
    "summer": {6, 7, 8},
    "autumn": {9, 10, 11},
}


def season_of_month(month: int) -> str:
    for season, months in SEASONS.items():
        if month in months:
            return season
    return "winter"


def get_relationship_tier(trust: int) -> str:
    if trust >= 80:
        return "挚友"
    if trust >= 60:
        return "密友"
    if trust >= 40:
        return "朋友"
    if trust >= 20:
        return "熟人"
    return "生面孔"


def map_effect_keys(effects: dict[str, int]) -> dict[str, int]:
    """把 Web 版效果键映射到规则引擎的属性名（如 mysticism → mysticism_knowledge）。"""
    mapped: dict[str, int] = {}
    for key, value in effects.items():
        mapped[EFFECT_ALIASES.get(key, key)] = value
    return mapped


class EventSystem:
    def __init__(self, event_graphs: list[EventGraph]) -> None:
        self.graphs = {graph.id: graph for graph in event_graphs}

    @classmethod
    def from_raw_events(cls, raw_events: list[dict[str, Any]]) -> EventSystem:
        graphs = [legacy_event_to_graph(event) for event in raw_events]
        return cls(graphs)

    @classmethod
    def from_graph_data(cls, graph_data: list[dict[str, Any]]) -> EventSystem:
        graphs = [event_graph_from_data(graph) for graph in graph_data]
        return cls(graphs)

    def available_nodes(self, state: GameState) -> list[tuple[EventGraph, EventNode]]:
        available: list[tuple[EventGraph, EventNode]] = []
        for graph in self.graphs.values():
            if graph.is_pool:
                for node in graph.nodes.values():
                    if node.id == graph.start_node and node.chance <= 0:
                        continue  # chance=0 的占位节点（如链图的 start）
                    if not self.on_cooldown(node, state) and self.conditions_met(
                        node.conditions, state
                    ):
                        available.append((graph, node))
                continue
            node = self.current_node(graph, state)
            if node is not None and not self.on_cooldown(node, state):
                if self.conditions_met(node.conditions, state):
                    available.append((graph, node))
        return available

    def handle_world_event(self, event: Any, state: GameState) -> bool:
        """V0.16：世界事件驱动事件图。

        当 bus 发布事件（如 NPC_MISSING）时，找到监听该类型的链图节点：
        - 若链图尚未推进（无记录）且触发节点即入口 → 激活（标记已开始）
        - 若非入口节点 → 直接推进链至该节点
        满足 on_world_event_cond（如失踪 NPC 的地点）才激活。
        """
        kind = getattr(event, "kind", None)
        if not kind:
            return False
        triggered = False
        for graph in self.graphs.values():
            for node in graph.nodes.values():
                if node.on_world_event != kind:
                    continue
                extra = getattr(event, "extra", {}) or {}
                if not self._event_cond_met(node.on_world_event_cond, event, extra):
                    continue
                if graph.id not in state.event_nodes:
                    # 链尚未开始：事件激活入口（记录已开始）
                    state.event_nodes[graph.id] = node.id
                    triggered = True
                    break
                current_id = state.event_nodes.get(graph.id)
                if current_id == "done" or current_id == node.id:
                    continue
                if self._is_before(graph, current_id, node.id):
                    # 事件目标节点在当前链位置之后 → 往前推进到它
                    state.event_nodes[graph.id] = node.id
                    triggered = True
                    break
        return triggered

    def _is_before(self, graph: EventGraph, current_id: str, target_id: str) -> bool:
        """target 是否在链中 current 之后（按边拓扑）。"""
        order = []
        seen = {current_id}
        queue = [current_id]
        for e in graph.edges:
            if e.from_node == current_id:
                order.append(e.to_node)
        # 简化：沿边找 target 可达性
        frontier = [current_id]
        visited = set()
        while frontier:
            nxt = frontier.pop(0)
            if nxt in visited:
                continue
            visited.add(nxt)
            if nxt == target_id:
                return True
            for e in graph.edges:
                if e.from_node == nxt:
                    frontier.append(e.to_node)
        return False

    def _event_cond_met(self, cond: dict[str, Any], event: Any, extra: dict[str, Any]) -> bool:
        for key, expected in cond.items():
            # 事件核心字段（npc_id/location/kind）或 extra 只要其一匹配即可
            actual = getattr(event, key, None)
            if actual is None:
                actual = extra.get(key)
            if actual != expected:
                return False
        return True

    def on_cooldown(self, node: EventNode, state: GameState) -> bool:
        if node.cooldown <= 0:
            return False
        last = state.world.event_last_triggered.get(node.id)
        if last is None:
            return False
        return state.days_lived - last < node.cooldown

    def current_node(self, graph: EventGraph, state: GameState) -> EventNode | None:
        node_id = state.event_nodes.get(graph.id, graph.start_node)
        return graph.nodes.get(node_id)

    def advance(self, graph: EventGraph, state: GameState) -> None:
        if graph.is_pool:
            return
        current_id = state.event_nodes.get(graph.id, graph.start_node)
        for edge in graph.edges:
            if edge.from_node != current_id:
                continue
            if self.conditions_met(edge.condition, state):
                state.event_nodes[graph.id] = edge.to_node
                return
        state.event_nodes[graph.id] = "done"

    def auto_advance(self, state: GameState) -> bool:
        """推进链图中的占位节点（chance<=0）。

        占位节点不参与随机事件触发，只作为链条的入口：
        一旦其出边条件满足，世界更新时自动进入下一节点。
        """
        advanced = False
        for graph in self.graphs.values():
            if graph.is_pool:
                continue
            node = self.current_node(graph, state)
            if node is None or node.chance > 0:
                continue
            for edge in graph.edges:
                if edge.from_node != node.id:
                    continue
                if self.conditions_met(edge.condition, state):
                    state.event_nodes[graph.id] = edge.to_node
                    advanced = True
                    break
        return advanced

    def apply(self, graph: EventGraph, node: EventNode, state: GameState) -> str:
        state.character.apply_changes(map_effect_keys(node.effects))
        # V0.21：特效键 _pathway 设置非凡途径
        pathway = node.effects.get("_pathway")
        if pathway:
            state.character.pathway = pathway
            tag = f"途径：{pathway}"
            if tag not in state.character.tags:
                state.character.tags.append(tag)
        for tag in node.add_tags:
            if tag not in state.character.tags:
                state.character.tags.append(tag)
        for clue in node.add_clues:
            if clue not in state.clues:
                state.clues.append(clue)
        for npc_id, amount in node.trust_effects.items():
            npc = state.npcs.get(npc_id)
            if npc is not None:
                npc.add_trust(amount)
        if node.cooldown > 0:
            state.world.event_last_triggered[node.id] = state.days_lived
        self.advance(graph, state)
        return node.text

    def conditions_met(self, conditions: dict[str, Any], state: GameState) -> bool:
        character = state.character

        min_day = conditions.get("min_day")
        if min_day is not None and state.days_lived < min_day:
            return False

        max_day = conditions.get("max_day")
        if max_day is not None and state.days_lived > max_day:
            return False

        season = conditions.get("season")
        if season is not None:
            if season_of_month(state.date.month) != season:
                return False

        months = conditions.get("months")
        if months is not None and state.date.month not in months:
            return False

        jobs = conditions.get("job")
        if jobs is not None:
            allowed = jobs if isinstance(jobs, list) else [jobs]
            if character.job not in allowed:
                return False

        location = conditions.get("location")
        if location is not None:
            allowed = location if isinstance(location, list) else [location]
            allowed_names = {LOCATION_ALIASES.get(item, item) for item in allowed}
            if character.location not in allowed_names:
                # 角色位于城市级地点（如“廷根”）时，区域级条件视为满足：
                # 角色可以在城市内各区域活动（对应网页版地图移动语义）。
                if character.location == "廷根":
                    pass
                else:
                    return False

        tag = conditions.get("tag")
        if tag is not None and tag not in character.tags:
            return False

        any_tag = conditions.get("any_tag")
        if any_tag is not None and not any(t in character.tags for t in any_tag):
            return False

        required_clue = conditions.get("clue")
        if required_clue is not None:
            needed = required_clue if isinstance(required_clue, list) else [required_clue]
            if not all(c in state.clues for c in needed):
                return False

        any_clue = conditions.get("any_clue")
        if any_clue is not None and not any(c in state.clues for c in any_clue):
            return False

        contact = conditions.get("contacts")
        if contact is not None:
            for npc_id, min_trust in contact.items():
                npc = state.npcs.get(npc_id)
                if npc is None or npc.trust < min_trust:
                    return False

        min_stat = conditions.get("min_stat", {})
        for stat_name, value in min_stat.items():
            if getattr(character, stat_name, 0) < value:
                return False

        return True


def legacy_event_to_graph(event: dict[str, Any]) -> EventGraph:
    node = EventNode(
        id="start",
        text=event["text"],
        chance=int(event.get("chance", 20)),
        weight=int(event.get("weight", 1)),
        effects=dict(event.get("effects", {})),
        conditions=dict(event.get("conditions", {})),
        add_tags=list(event.get("add_tags", [])),
    )
    return EventGraph(
        id=event["id"],
        nodes={"start": node},
        edges=[],
        start_node="start",
    )


def event_graph_from_data(graph: dict[str, Any]) -> EventGraph:
    nodes = {}
    for node in graph.get("nodes", []):
        effects = dict(node.get("effects", {}))
        add_tags = list(node.get("add_tags", []))
        add_clues = [clue["id"] for clue in node.get("add_clues", [])]
        trust_effects = dict(node.get("trust_effects", {}))
        cooldown = int(node.get("cooldown", 0))
        on_world_event = node.get("on_world_event")
        on_world_event_cond = dict(node.get("on_world_event_cond", {}))
        choices = node.get("choices", [])
        if choices and not effects:
            primary = choices[0]
            effects = dict(primary.get("effects", {}))
            add_tags = list(primary.get("add_tags", []))
            add_clues = [clue["id"] for clue in primary.get("add_clues", [])]
            trust_effects = dict(primary.get("trust_effects", {}))
        nodes[node["id"]] = EventNode(
            id=node["id"],
            text=node["text"],
            chance=int(node.get("chance", 20)),
            weight=int(node.get("weight", 1)),
            effects=effects,
            conditions=normalize_conditions(node),
            add_tags=add_tags,
            add_clues=add_clues,
            trust_effects=trust_effects,
            cooldown=cooldown,
            on_world_event=on_world_event,
            on_world_event_cond=on_world_event_cond,
        )
    edges = [
        EventEdge(
            from_node=edge["from"],
            to_node=edge["to"],
            condition=dict(edge.get("condition", {})),
        )
        for edge in graph.get("edges", [])
    ]
    return EventGraph(
        id=graph["id"],
        nodes=nodes,
        edges=edges,
        start_node=graph.get("start_node", "start"),
    )


def normalize_conditions(node: dict[str, Any]) -> dict[str, Any]:
    """把 Web 版事件字段转换为引擎条件。

    Web 版节点字段：locations / min_day / requires_clues / requires_any_clue /
    requires_tags_any / requires_contacts / choices（内部 effects/add_tags/add_clues）。
    引擎条件：location（或列表）、min_day、clue（或列表）、any_clue、any_tag。
    """
    conditions: dict[str, Any] = {}

    if "locations" in node:
        conditions["location"] = list(node["locations"])
    elif "location" in node:
        conditions["location"] = node["location"]

    if "min_day" in node:
        conditions["min_day"] = int(node["min_day"])
    if "max_day" in node:
        conditions["max_day"] = int(node["max_day"])

    if "requires_clues" in node:
        conditions["clue"] = list(node["requires_clues"])
    if "requires_any_clue" in node:
        conditions["any_clue"] = list(node["requires_any_clue"])
    if "requires_tags_any" in node:
        conditions["any_tag"] = list(node["requires_tags_any"])
    if "requires_contacts" in node:
        # 信任门槛：{npc_id: min_trust} 保留完整映射，conditions_met 按真实信任校验。
        conditions["contacts"] = dict(node["requires_contacts"])

    # 统计门槛：min_stat 下游统一用 {"属性": 阈值} 处理
    if "min_madness" in node:
        conditions.setdefault("min_stat", {})["madness"] = int(node["min_madness"])
    if "min_spirituality" in node:
        conditions.setdefault("min_stat", {})["spirituality"] = int(
            node["min_spirituality"]
        )

    if "season" in node:
        conditions["season"] = node["season"]
    if "months" in node:
        conditions["months"] = list(node["months"])
    if "jobs" in node:
        conditions["job"] = list(node["jobs"])
    elif "job" in node:
        conditions["job"] = node["job"]

    if "conditions" in node:
        for key, value in node["conditions"].items():
            conditions.setdefault(key, value)

    return conditions