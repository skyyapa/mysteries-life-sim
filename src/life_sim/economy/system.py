"""经济系统（轻量）。

不做金融模拟，只回答两个问题：
- 钱从哪里来：职业工资（按日发放）
- 钱到哪里去：住房 / 食物 / 交通

V0.15.4：NPC 也纳入经济微循环——
  NPC 工作赚日薪、购物/吃饭花钱；
  没钱 → 压力上升 → behavior 里更倾向工作（涌现循环起点）。
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

# NPC 职业日工资（按 job 关键词匹配）
NPC_DAILY_WAGE = {
    "酒馆老板": 6,
    "报童": 2,
    "黑夜教士": 4,
    "邻居": 1,
    "房东": 5,
    "事务所主管": 8,
    "杂货店主": 5,
    "面包师": 4,
    "搬运工": 4,
    "出租马车夫": 5,
    "洗衣女工": 2,
    "工厂工人": 4,
    "诊所医生": 7,
    "巡警": 5,
    "学校教师": 5,
    "图书管理员": 4,
    "裁缝": 4,
    "信使": 3,
    "流浪者": 0,
    "旧书贩": 3,
    "守夜人": 4,
}
NPC_DAILY_WAGE_DEFAULT = 3

# NPC 日常开销（住房+食物）
NPC_DAILY_EXPENSE = 2


def npc_wage(job: str) -> int:
    return NPC_DAILY_WAGE.get(job, NPC_DAILY_WAGE_DEFAULT)


class EconomySystem:
    def __init__(self) -> None:
        pass

    def tick(self, state: GameState) -> None:
        self._tick_character(state)
        self._tick_npcs(state)

    def _tick_character(self, state: GameState) -> None:
        character = state.character
        job = character.job

        income = CAREER_DAILY_INCOME.get(job, 2)
        expense = CAREER_DAILY_EXPENSE.get(job, 2)

        character.money += income

        actual = min(expense, character.money)
        character.money -= actual
        shortage = expense - actual
        if shortage > 0:
            character.stress = min(100, character.stress + 3)
            character.health = max(0, character.health - 1)

        economy = state.world.economy
        pressure = economy.get("pressure", 0)
        pressure += 2 if shortage > 0 else -1
        economy["pressure"] = max(0, min(100, pressure))

        character.stress = max(0, min(100, character.stress))

    def _tick_npcs(self, state: GameState) -> None:
        """NPC 经济微循环：日常开销；没钱的压力与情绪影响。

        工资由 work 行为按职业发放（见 npc.effects.build_result）——
        上班才有钱，休息日没工资，经济压力才会涌现。
        """
        for npc in state.npcs.values():
            if npc.disappeared or not npc.state.alive:
                continue
            actual = min(NPC_DAILY_EXPENSE, npc.state.money)
            npc.state.money -= actual
            shortage = NPC_DAILY_EXPENSE - actual
            if shortage > 0:
                npc.state.stress = min(100, npc.state.stress + 3)
                npc.state.mood = max(0, npc.state.mood - 2)
            npc.money = int(npc.state.money)
            npc.state.clamp()