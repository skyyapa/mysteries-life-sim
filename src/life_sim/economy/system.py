"""经济系统（轻量）。

不做金融模拟，只回答两个问题：
- 钱从哪里来：职业工资（按日发放）
- 钱到哪里去：住房 / 食物 / 交通

规则（V0.14）：
- 玩家角色：工资由职业决定；日常支出（住房 1/h、食物、交通）逐日结算到钱包。
- 世界层面：经济压力反映在 city/economy —— 支出与收入之差影响压力；
  数字不追求精确，只求"账算得过来"，避免玩家无限攒钱或无限破产。
"""

from __future__ import annotations

from typing import Any

from ..models import GameState


# 职业日收入（镑/天）——与 Web careers 对齐
CAREER_DAILY_INCOME = {
    "文法学校学生": 0,
    "店铺学徒": 4,
    "事务所文员": 7,
    "临时工": 8,
}

# 职业日支出（镑/天）
CAREER_DAILY_EXPENSE = {
    "文法学校学生": 2,
    "店铺学徒": 3,
    "事务所文员": 5,
    "临时工": 4,
}


class EconomySystem:
    def __init__(self) -> None:
        pass

    def tick(self, state: GameState) -> None:
        character = state.character
        job = character.job

        income = CAREER_DAILY_INCOME.get(job, 2)
        expense = CAREER_DAILY_EXPENSE.get(job, 2)

        # 收入：学生/学徒无日薪（靠事件与月结）
        character.money += income

        # 支出：住房+食物+交通占大头；钱不够则影响压力与健康
        actual = min(expense, character.money)
        character.money -= actual
        shortage = expense - actual
        if shortage > 0:
            character.stress = min(100, character.stress + 3)
            character.health = max(0, character.health - 1)

        # 世界经济压力：支出吃紧则上行，宽裕则回落
        economy = state.world.economy
        pressure = economy.get("pressure", 0)
        pressure += 2 if shortage > 0 else -1
        economy["pressure"] = max(0, min(100, pressure))

        # 同步角色属性 clamp（money 单独下限 0）
        character.stress = max(0, min(100, character.stress))