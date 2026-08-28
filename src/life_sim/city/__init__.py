"""城市子系统：感知层（每日见闻）、新闻。"""

from .news import CityTidings, daily_bulletin, generate_tidings

__all__ = ["CityTidings", "daily_bulletin", "generate_tidings"]