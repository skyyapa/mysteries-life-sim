"""一年人生总结（V0.23）。

把游戏已跟踪的数据（日记/标签/线索/途径/疯狂/熟人圈/城市见闻）收束成一份
《岁末回顾》：玩家过完一年看到"这一年的人生"叙事式总结。

规则驱动、不 AI：所有句子从数据模板拼装。
"""

from __future__ import annotations

from typing import Any

from .models import GameState


def summarize_life(state: GameState) -> dict[str, Any]:
    """生成一年人生总结报告。"""
    char = state.character

    # 1. 这年你认识的人（social_links 最高的 3 个，按友好度）
    people = _top_contacts(state, 3)

    # 2. 经历轮廓：从标签分类
    tags = list(char.tags)
    experiences = {
        "普通生活": [t for t in tags if t in ("账目无误", "据理力争", "忍气吞声", "开学典礼")],
        "异常与非凡": [t for t in tags if "途径" in t or "组织" in t or "教会" in t or "失控" in t or "神秘" in t or "失踪" in t],
        "抉择": [t for t in tags if "抉择" in t or "选择" in t or "抽身" in t or "加入" in t or "线人" in t],
    }

    # 3. 非凡之路
    pathway = char.pathway
    madness_stage = _madness_stage(char.madness)
    if pathway:
        from .mysticism.pathways import PATHWAYS

        spec = PATHWAYS.get(pathway, {})
        pathway_line = (
            f"这一年你踏上了「{pathway}」之路——{spec.get('trait', '')}。"
            f"心灵在灵性与疯狂间摇摆，岁末时{_madness_stage_text(madness_stage)}。"
        )
    else:
        pathway_line = "这一年你始终是个普通人。有些门打开过又关上了，但你选择了留下。"

    # 4. 神秘侧指标
    mystery_stats = {
        "mysticism_knowledge": char.mysticism_knowledge,
        "spirituality": char.spirituality,
        "corruption": char.corruption,
        "madness": char.madness,
    }

    # 5. 城市回声：一年里城市说过的话（bulletin）
    city_echoes = _city_echoes(state, 3)

    # 6. 一句话总结（规则模板，按状态拼装）
    one_liner = _build_oneliner(state, pathway, madness_stage)

    return {
        "character": {"name": char.name, "age": char.age, "job": char.job},
        "people": people,
        "experiences": experiences,
        "pathway_line": pathway_line,
        "mystery_stats": mystery_stats,
        "madness_stage": madness_stage,
        "city_echoes": city_echoes,
        "one_liner": one_liner,
        "days_lived": state.days_lived,
    }


def _top_contacts(state: GameState, limit: int) -> list[dict[str, Any]]:
    """按'友好度'（friendship 为主）排 top N 联系人。"""
    rows = []
    for npc in state.npcs.values():
        link = getattr(npc, "relationship", {}) or {}
        friendliness = link.get("friendship", 0) + link.get("fear", 0) * 0  # 畏惧不算友好
        if friendliness > 0:
            rows.append(
                {
                    "name": npc.name,
                    "job": npc.job,
                    "trust": link.get("trust", 0),
                    "friendliness": int(friendliness),
                }
            )
    rows.sort(key=lambda r: r["friendliness"], reverse=True)
    return rows[:limit]


def _madness_stage(madness: int) -> str:
    if madness >= 80:
        return "濒危"
    if madness >= 55:
        return "不安"
    if madness >= 30:
        return "恍惚"
    return "平稳"


def _madness_stage_text(stage: str) -> str:
    return {
        "平稳": "心智尚稳，只是偶尔做怪梦",
        "恍惚": "时而恍惚，分不清梦与真",
        "不安": "不安如影随形，夜不能寐",
        "濒危": "你已在失控边缘徘徊",
    }.get(stage, "心智尚稳")


def _city_echoes(state: GameState, limit: int) -> list[str]:
    """城市说过的话：取公告里最有代表性的几句（去重采样）。"""
    bulletin = getattr(state.world, "bulletin", []) or []
    texts: list[str] = []
    seen: set[str] = set()
    for entry in bulletin:
        text = entry.get("text", "") if isinstance(entry, dict) else ""
        if text and text not in seen:
            seen.add(text)
            texts.append(text)
        if len(texts) >= limit:
            break
    return texts


def _build_oneliner(
    state: GameState, pathway: str | None, madness_stage: str
) -> str:
    char = state.character
    parts = [f"{char.name}在廷根度过了{state.days_lived}天"]
    if pathway:
        parts.append(f"以「{pathway}」的身份")
    if char.money > 300:
        parts.append("攒下了一笔可观的积蓄")
    elif char.money < 20:
        parts.append("日子过得紧巴巴")
    if madness_stage in ("不安", "濒危"):
        parts.append(f"带着{_madness_stage_text(madness_stage)}的痕迹")
    if char.tags:
        parts.append("留下了一串只属于自己的故事")
    return "，".join(parts) + "。"