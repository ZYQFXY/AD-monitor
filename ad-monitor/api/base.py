from dataclasses import dataclass
from typing import List
from abc import ABC, abstractmethod


@dataclass
class AdSetData:
    adset_id: str
    campaign_id: str
    platform: str
    name: str
    spend: float
    roas: float
    daily_budget: float
    remaining_budget: float


@dataclass
class AdData:
    ad_id: str
    adset_id: str
    campaign_id: str
    platform: str
    name: str
    ctr: float
    impressions: int


class BaseAdAPI(ABC):
    @abstractmethod
    def get_adsets(self, campaign_id: str) -> List[AdSetData]:
        """拉取 Campaign 下所有 Ad Set 的今日数据"""

    @abstractmethod
    def get_ads(self, campaign_id: str, window_days: int = 7) -> List[AdData]:
        """拉取 Campaign 下所有 Ad 的近 window_days 天 CTR 数据"""
