from typing import List
from api.base import BaseAdAPI, AdSetData, AdData
import config


class GoogleAPI(BaseAdAPI):
    """
    Google Ads API 接入点。
    当前为占位符实现，返回 mock 数据供逻辑验证。
    接入真实 API 需配置 GOOGLE_ADS_DEVELOPER_TOKEN / GOOGLE_ADS_REFRESH_TOKEN 等。
    """

    def get_adsets(self, campaign_id: str) -> List[AdSetData]:
        if not config.GOOGLE_ADS_DEVELOPER_TOKEN:
            raise RuntimeError("Google Ads API 未配置（GOOGLE_ADS_DEVELOPER_TOKEN 为空）")
        # TODO: 接入 google-ads SDK
        # from google.ads.googleads.client import GoogleAdsClient
        return _mock_adsets(campaign_id, "google")

    def get_ads(self, campaign_id: str, window_days: int = 7) -> List[AdData]:
        if not config.GOOGLE_ADS_DEVELOPER_TOKEN:
            raise RuntimeError("Google Ads API 未配置（GOOGLE_ADS_DEVELOPER_TOKEN 为空）")
        return _mock_ads(campaign_id, "google")


def _mock_adsets(campaign_id: str, platform: str) -> List[AdSetData]:
    return [
        AdSetData(adset_id=f"{platform}_adgroup_001", campaign_id=campaign_id, platform=platform,
                  name="广告组-搜索A", spend=800.0, roas=0.7, daily_budget=1500.0, remaining_budget=700.0),
        AdSetData(adset_id=f"{platform}_adgroup_002", campaign_id=campaign_id, platform=platform,
                  name="广告组-展示B", spend=300.0, roas=2.8, daily_budget=1500.0, remaining_budget=1200.0),
    ]


def _mock_ads(campaign_id: str, platform: str) -> List[AdData]:
    return [
        AdData(ad_id=f"{platform}_ad_001", adset_id=f"{platform}_adgroup_001",
               campaign_id=campaign_id, platform=platform,
               name="文字广告01", ctr=0.008, impressions=12000),
    ]
