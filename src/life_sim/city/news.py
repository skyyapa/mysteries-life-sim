"""城市感知层：廷根每日见闻（V0.20）。

目标：让"城市自己运行"被玩家看得见——
每天由世界状态（经济压力/组织活跃/失踪事件/地点人气/季节/疯狂）生成一条"城市动态"，
写入世界公告牌，玩家打开即感受到城市在呼吸。

设计：多个"观察源"各自产出候选动态，按当日最突出者胜出，避免机械堆砌。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..models import GameState

# 城市公告历史保留条数
BULLETIN_MAX = 200


def _emphasized(text: str) -> str:
    return text


# ---- 观察源：根据世界状态生成候选动态 ----

def _economy_news(state: GameState) -> str | None:
    pressure = state.world.economy.get("pressure", 0)
    if pressure >= 70:
        return "煤价与面包价又涨了一截，市场里到处是压低的抱怨声。"
    if pressure >= 45:
        return "最近物价不太稳，摊贩们说货运越来越不好走。"
    if pressure <= 15:
        return "集市里难得人人都还有余钱，卖货的吆喝声都响亮了几分。"
    return None


def _org_news(state: GameState) -> str | None:
    secret = state.world.organizations.get("暗流组织", {}).get("activity", 0)
    church = state.world.organizations.get("黑夜教会", {}).get("attention", 0)
    if secret >= 60:
        return "夜里东区多了些不该有的动静，守夜人一遍遍巡查看不出端倪。"
    if church >= 65:
        return "教堂的信徒今早多了许多，教士们低声说着什么。"
    if secret >= 35:
        return "有人传说东区最近不太平，但没人说得清到底发生了什么。"
    return None


def _npc_missing_news(state: GameState) -> str | None:
    """失踪新闻只在刚发生时（3 天内）是头条，之后淡出——城市会继续运转。"""
    recent_missing = [
        n
        for n in state.npcs.values()
        if n.disappeared
        and n.state
        and n.state.alive
        and (n.disappeared_day is not None)
        and (state.days_lived - n.disappeared_day) <= 3
    ]
    if not recent_missing:
        return None
    names = "、".join(n.name for n in recent_missing[:2])
    return f"街坊们小声议论：{names}已经好几天不见人影了。"


def _season_news(state: GameState) -> str | None:
    month = state.date.month
    if month in (12, 1, 2):
        weather = state.world.weather
        if weather == "阴天" or "雨" in weather:
            return "湿冷的冬天，屋檐下晾的衣服三天都不干。"
    if month in (3, 4, 5):
        return "开春了，街道上的雪水化成泥，马车夫都在骂路难走。"
    if month in (9, 10, 11):
        return "秋天的集市堆满苹果与熏鱼，难得有点丰收的样子。"
    return None


def _crime_news(state: GameState) -> str | None:
    danger = state.world.locations.get("东区", {}).get("danger", 0)
    if danger >= 65:
        return "巡警说东区最近不太平，劝人夜里少走深巷。"
    if danger >= 40:
        return "报上登了一则失窃案，丢失的东西有些古怪。"
    return None


_NEWS_SOURCES = [
    _npc_missing_news,
    _economy_news,
    _org_news,
    _crime_news,
    _season_news,
]


@dataclass
class CityTidings:
    """当日城市见闻。"""

    day: int
    date: str
    text: str
    source: str

    def to_dict(self) -> dict[str, Any]:
        return {"day": self.day, "date": self.date, "text": self.text, "source": self.source}


def generate_tidings(state: GameState, rng: Any | None = None) -> CityTidings | None:
    """生成一条城市见闻（每日至多一条，取最突出观察源）。

    事件驱动的来源（失踪）优先；其余源取并列最高者；无料时返回 None（城市平静）。
    """
    candidates: list[tuple[str, str]] = []  # (text, source)
    for source in _NEWS_SOURCES:
        text = source(state)
        if text:
            candidates.append((text, source.__name__.strip("_")))

    if not candidates:
        return None
    if rng is None:
        import random

        rng = random.Random()
    # 失踪/犯罪这类"大事"优先，其余随机选一条
    priority = [pair for pair in candidates if pair[1] in ("npc_missing_news", "crime_news")]
    pool = priority or candidates
    text, source = rng.choice(pool)

    return CityTidings(
        day=state.days_lived,
        date=state.date.label(),
        text=text,
        source=source,
    )


def daily_bulletin(state: GameState, *, force: bool = False) -> str | None:
    """按日生成城市见闻写入世界公告牌。force=True 时即使平静也记录。

    返回当日文本（若有）。
    """
    tidings = generate_tidings(state)
    if tidings is None and not force:
        return None
    if tidings is None:
        tidings = CityTidings(
            day=state.days_lived,
            date=state.date.label(),
            text="廷根的风平浪静，和昨天没什么两样。",
            source="quiet",
        )
    if not hasattr(state.world, "bulletin"):
        state.world.bulletin = []
    state.world.bulletin.append(tidings.to_dict())
    state.world.bulletin = state.world.bulletin[-BULLETIN_MAX:]
    state.world.daily_bulletin = tidings.to_dict()
    return tidings.text