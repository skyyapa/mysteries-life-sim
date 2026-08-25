"""世界状态聚合入口。

V0.14 目标：诡秘相关的世界级属性（mysticism_level / corruption / fate）
统一挂到 WorldState 上，作为未来扩展点。
此处仅提供便捷访问器，具体字段仍在 models.WorldState。
"""

from __future__ import annotations

from ..models import GameState


def world_state(state: GameState):
    return state.world


def get_mysticism_level(state: GameState) -> int:
    return getattr(state.world, "mysticism_level", 0)


def set_mysticism_level(state: GameState, value: int) -> None:
    state.world.mysticism_level = max(0, min(100, value))