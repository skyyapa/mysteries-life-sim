from __future__ import annotations

import argparse
import sys

from .engine import LifeEngine
from .save import save_game


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="人生模拟器 V0.22")
    parser.add_argument("--auto", type=int, default=0, help="自动模拟指定天数")
    parser.add_argument("--seed", type=int, default=1348, help="随机种子")
    parser.add_argument("--name", default="埃文·莫里斯", help="角色姓名")
    parser.add_argument("--debug", default=None, help="模拟 N 天后打印某 NPC 的调试面板（如 --debug tom_tavern）")
    args = parser.parse_args()

    engine = LifeEngine(seed=args.seed)
    state = engine.new_game(name=args.name)

    print("人生模拟器 V0.22")
    print(f"角色：{state.character.name}，{state.character.age}岁，{state.character.job}")
    print(f"地点：{state.character.location}，时间：{state.date.label()}")
    print()

    if args.debug:
        run_auto(engine, state, args.auto or 30)
        print_debug_panel(engine, state, args.debug)
        return

    if args.auto:
        run_auto(engine, state, args.auto)
    else:
        run_interactive(engine, state)

    path = save_game(state)
    print()
    print(f"存档已保存：{path}")


def print_debug_panel(engine, state, npc_id: str) -> None:
    """V0.15.6 Debug 面板：展示 NPC 状态/需求/日程/行为评分/事件记录。"""
    npc = state.npcs.get(npc_id)
    if npc is None:
        print(f"未找到 NPC：{npc_id}")
        return
    print(f"\n═══ NPC Debug: {npc.name}（{npc.job}）═══")
    print(f"  地点：{npc.location} | 行为：{npc.current_activity} | 时间：{npc.current_time}")
    print(f"  健康 {npc.state.health} | 疲劳 {npc.state.fatigue} | 压力 {npc.state.stress} | "
          f"情绪 {npc.state.mood} | 金钱 {npc.state.money:.1f} | 病 {int(npc.state.sick)}")
    print(f"  需求：饿 {npc.needs.hunger} | 休息 {npc.needs.rest} | 社交 {npc.needs.social} | 安全 {npc.needs.safety}")
    print(f"  日程模板：{npc.schedule_id or '旧数组'} | 失踪 {int(npc.disappeared)}")

    # 当前行为的评分（为何这么做）
    try:
        from life_sim.npc.behavior import generate_candidates

        cands = generate_candidates(
            npc,
            schedule_action=npc.current_activity.lower(),
            needs=npc.needs,
            state=npc.state,
            is_night=state.date.is_night(),
            city_tension=state.world.city.get("tension", 0),
            day_index=state.days_lived,
        )
        ranked = sorted(cands, key=lambda c: -c.score)[:5]
        print("  行为评分（TOP5）：")
        for c in ranked:
            print(f"    {c}")
    except Exception as exc:
        print(f"  （评分查询失败：{exc}）")

    # 该 NPC 最近的钩子事件
    events = engine.event_bus.recent(npc_id, limit=5)
    if events:
        print("  最近事件：")
        for ev in events:
            print(f"    {ev}")
    print("═" * 32)


def run_auto(engine: LifeEngine, state, days: int) -> None:
    for _ in range(days):
        action_id = engine.auto_action(state)
        entry = engine.take_action(state, action_id)
        print(f"[{entry.date}] {entry.action}：{entry.summary}")

    print_status(state)


def run_interactive(engine: LifeEngine, state) -> None:
    """自动生活模式：主角自己过日，玩家按回车继续，输入 q 结束。

    与网页版一致：日常由系统自动选择，玩家只负责在关键时刻停下思考。
    """
    print("（自动生活模式：主角自己安排日常，按回车继续，q 结束）")
    while state.days_lived < 360:
        before = state.days_lived
        action_id = engine.auto_action(state)
        entry = engine.take_action(state, action_id)
        print(f"[{entry.date}] {entry.action}：{entry.summary}")

        if state.days_lived - before >= 7:
            print_status(state)
            raw = input("> 回车继续生活，或输入 q 结束：").strip()
            if raw.lower() == "q":
                break
    print_status(state)


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
