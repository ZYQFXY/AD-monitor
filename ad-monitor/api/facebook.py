from typing import List
from api.base import BaseAdAPI, AdSetData, AdData
import config


class FacebookAPI(BaseAdAPI):
    """
    Facebook Marketing API 接入点。
    当前为占位符实现，返回 mock 数据供逻辑验证。
    接入真实 API 需配置 FACEBOOK_ACCESS_TOKEN / FACEBOOK_AD_ACCOUNT_ID。
    """

    def get_adsets(self, campaign_id: str) -> List[AdSetData]:
        if not config.FACEBOOK_ACCESS_TOKEN:
            raise RuntimeError("Facebook API 未配置（FACEBOOK_ACCESS_TOKEN 为空）")
        # TODO: 接入 facebook_business SDK
        # from facebook_business.api import FacebookAdsApi
        # from facebook_business.adobjects.adset import AdSet
        return _mock_adsets(campaign_id, "facebook")

    def get_ads(self, campaign_id: str, window_days: int = 7) -> List[AdData]:
        if not config.FACEBOOK_ACCESS_TOKEN:
            raise RuntimeError("Facebook API 未配置（FACEBOOK_ACCESS_TOKEN 为空）")
        return _mock_ads(campaign_id, "facebook")


def _mock_adsets(campaign_id: str, platform: str) -> List[AdSetData]:
    return [
        AdSetData(adset_id=f"{platform}_adset_001", campaign_id=campaign_id, platform=platform,
                  name="广告组-A", spend=1200.0, roas=0.8, daily_budget=2000.0, remaining_budget=800.0),
        AdSetData(adset_id=f"{platform}_adset_002", campaign_id=campaign_id, platform=platform,
                  name="广告组-B", spend=500.0, roas=3.2, daily_budget=2000.0, remaining_budget=1500.0),
        AdSetData(adset_id=f"{platform}_adset_003", campaign_id=campaign_id, platform=platform,
                  name="广告组-C", spend=1900.0, roas=1.5, daily_budget=2000.0, remaining_budget=100.0),
    ]


def _mock_ads(campaign_id: str, platform: str) -> List[AdData]:
    return [
        AdData(ad_id=f"{platform}_ad_001", adset_id=f"{platform}_adset_001",
               campaign_id=campaign_id, platform=platform,
               name="素材-视频01", ctr=0.005, impressions=20000),
        AdData(ad_id=f"{platform}_ad_002", adset_id=f"{platform}_adset_002",
               campaign_id=campaign_id, platform=platform,
               name="素材-图片02", ctr=0.025, impressions=15000),
    ]
