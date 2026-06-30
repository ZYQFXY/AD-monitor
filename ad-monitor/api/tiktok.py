from typing import List
from api.base import BaseAdAPI, AdSetData, AdData
import config


class TikTokAPI(BaseAdAPI):
    """
    TikTok Marketing API 接入点。
    当前为占位符实现，返回 mock 数据供逻辑验证。
    接入真实 API 需配置 TIKTOK_ACCESS_TOKEN / TIKTOK_ADVERTISER_ID。
    """

    def get_adsets(self, campaign_id: str) -> List[AdSetData]:
        if not config.TIKTOK_ACCESS_TOKEN:
            raise RuntimeError("TikTok API 未配置（TIKTOK_ACCESS_TOKEN 为空）")
        # TODO: 接入 TikTok Marketing API (requests + App Access Token)
        return _mock_adsets(campaign_id, "tiktok")

    def get_ads(self, campaign_id: str, window_days: int = 7) -> List[AdData]:
        if not config.TIKTOK_ACCESS_TOKEN:
            raise RuntimeError("TikTok API 未配置（TIKTOK_ACCESS_TOKEN 为空）")
        return _mock_ads(campaign_id, "tiktok")


def _mock_adsets(campaign_id: str, platform: str) -> List[AdSetData]:
    return [
        AdSetData(adset_id=f"{platform}_adgroup_001", campaign_id=campaign_id, platform=platform,
                  name="广告组-信息流A", spend=600.0, roas=1.8, daily_budget=1000.0, remaining_budget=400.0),
        AdSetData(adset_id=f"{platform}_adgroup_002", campaign_id=campaign_id, platform=platform,
                  name="广告组-TopView", spend=200.0, roas=4.1, daily_budget=1000.0, remaining_budget=800.0),
    ]


def _mock_ads(campaign_id: str, platform: str) -> List[AdData]:
    return [
        AdData(ad_id=f"{platform}_ad_001", adset_id=f"{platform}_adgroup_001",
               campaign_id=campaign_id, platform=platform,
               name="视频素材01", ctr=0.004, impressions=50000),
        AdData(ad_id=f"{platform}_ad_002", adset_id=f"{platform}_adgroup_002",
               campaign_id=campaign_id, platform=platform,
               name="视频素材02", ctr=0.032, impressions=30000),
    ]
