from __future__ import annotations

import argparse
import sys

from .engine import LifeEngine
from .save import save_game


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="人生模拟器 V0.17.1")
    parser.add_argument("--auto", type=int, default=0, help="自动模拟指定天数")
    parser.add_argument("--seed", type=int, default=1348, help="随机种子")
    parser.add_argument("--name", default="埃文·莫里斯", help="角色姓名")
    args = parser.parse_args()

    engine = LifeEngine(seed=args.seed)
    state = engine.new_game(name=args.name)

    print("人生模拟器 V0.17.1")
    print(f"角色：{state.character.name}，{state.character.age}岁，{state.character.job}")
    print(f"地点：{state.character.location}，时间：{state.date.label()}")
    print()

    if args.auto:
        run_auto(engine, state, args.auto)
    else:
        run_interactive(engine, state)

    path = save_game(state)
    print()
    print(f"存档已保存：{path}")


def run_auto(engine: LifeEngine, state, days: int) -> None:
    for _ in range(days):
        action_id = engine.auto_action(state)
        entry = engine.take_action(state, action_id)
        print(f"[{entry.date}] {entry.action}：{entry.summary}")

    print_status(state)


def run_interactive(engine: LifeEngine, state) -> None:
    while state.days_lived < 30:
        print_status(state)
        actions = engine.available_actions()
        for index, action_id in enumerate(actions, start=1):
            action = engine.actions[action_id]
            print(f"{index}. {action['name']} - {action['description']}")

        raw = input("> 选择今天的行动，或输入 q 结束：").strip()
        if raw.lower() == "q":
            break
        if not raw.isdigit() or not 1 <= int(raw) <= len(actions):
            print("请输入有效编号。")
            continue

        action_id = actions[int(raw) - 1]
        entry = engine.take_action(state, action_id)
        print(f"{entry.summary}")
        print()


def print_status(state) -> None:
    character = state.character
    print()
    print(f"{state.date.label()} | 第 {state.days_lived + 1} 天")
    print(
        "状态："
        f"健康 {character.health} | "
        f"体力 {character.stamina} | "
        f"智力 {character.intelligence} | "
        f"魅力 {character.charisma} | "
        f"金钱 {character.money} | "
        f"压力 {character.stress}"
    )
    if character.tags:
        print(f"标签：{'、'.join(character.tags)}")
    print()


if __name__ == "__main__":
    main()
