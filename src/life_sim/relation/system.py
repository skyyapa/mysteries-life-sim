"""关系系统：由事件驱动的关系变化 + 每日自然演化。

原则：
- 关系维度：trust（信任） / friendship（友谊） / fear（畏惧）
- 事件通过 trust_effects / 选择产生关系变化（已在 EventSystem.apply 支持）
- 每日演化：与玩家同地的 NPC 友谊自然微涨；长时间不见的信任微弱回落
"""

from __future__ import annotations

from ..models import GameState


class RelationshipSystem:
    def __init__(self) -> None:
        pass

    def change(self, npc_id: str, state: GameState, **deltas: int) -> None:
        npc = state.npcs.get(npc_id)
        if npc is None:
            return
        for key, delta in deltas.items():
            if key in npc.relationship:
                npc.relationship[key] = max(0, min(100, npc.relationship[key] + delta))
        npc.trust = npc.relationship.get("trust", npc.trust)
        npc.clamp()

    def tick(self, state: GameState) -> None:
        """每日自然演化（规则驱动）。

        - trust（信任）：一旦建立相对稳定，不因日子流逝自动掉分（由事件/关系驱动）
        - friendship（友谊）：长期不互动会缓慢降温
        - fear（畏惧）：随时间衰减
        """
        for npc in state.npcs.values():
            if npc.disappeared:
                continue
            rel = npc.relationship
            rel["friendship"] = max(0, min(100, rel.get("friendship", 0) - 1))
            rel["fear"] = max(0, min(100, rel.get("fear", 0) - 1))