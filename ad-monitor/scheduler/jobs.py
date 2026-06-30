import logging
from api.facebook import FacebookAPI
from api.google import GoogleAPI
from api.tiktok import TikTokAPI
from db.crud import (
    get_all_categories, get_all_bindings, get_config,
    upsert_adset_snapshot, upsert_ad_snapshot,
)
from rules.engine import check_adset_rules, check_ad_rules

logger = logging.getLogger(__name__)

_APIS = {
    "facebook": FacebookAPI,
    "google": GoogleAPI,
    "tiktok": TikTokAPI,
}


def run_monitoring_job() -> None:
    """每小时定时任务：拉取全部绑定 Campaign → 更新快照 → 执行规则 → 发告警"""
    wecom_url = get_config("wecom_webhook_url")
    categories = {c["id"]: c for c in get_all_categories()}
    bindings = get_all_bindings()

    for binding in bindings:
        campaign_id = binding["campaign_id"]
        platform = binding["platform"]
        category_id = binding["category_id"]
        category = categories.get(category_id)
        if not category:
            continue

        api = _APIS[platform]()
        try:
            adsets = api.get_adsets(campaign_id)
        except Exception as exc:
            logger.warning("拉取 AdSet 失败 [%s %s]: %s", platform, campaign_id, exc)
            adsets = []

        for adset in adsets:
            upsert_adset_snapshot({
                "adset_id": adset.adset_id, "campaign_id": adset.campaign_id,
                "platform": adset.platform, "category_id": category_id,
                "name": adset.name, "spend": adset.spend, "roas": adset.roas,
                "daily_budget": adset.daily_budget, "remaining_budget": adset.remaining_budget,
            })
            if wecom_url:
                check_adset_rules(adset, category, wecom_url)

        try:
            ads = api.get_ads(campaign_id, window_days=category["ctr_window_days"])
        except Exception as exc:
            logger.warning("拉取 Ad 失败 [%s %s]: %s", platform, campaign_id, exc)
            ads = []

        for ad in ads:
            upsert_ad_snapshot({
                "ad_id": ad.ad_id, "adset_id": ad.adset_id, "campaign_id": ad.campaign_id,
                "platform": ad.platform, "category_id": category_id,
                "name": ad.name, "ctr": ad.ctr, "impressions": ad.impressions,
            })
            if wecom_url:
                check_ad_rules(ad, category, wecom_url)


def run_category_refresh(category_id: int) -> None:
    """手动刷新单个品类（Web 界面触发）"""
    wecom_url = get_config("wecom_webhook_url")
    from db.crud import get_category, get_bindings_by_category
    category = get_category(category_id)
    if not category:
        return
    bindings = get_bindings_by_category(category_id)

    for binding in bindings:
        campaign_id = binding["campaign_id"]
        platform = binding["platform"]
        api = _APIS[platform]()

        try:
            adsets = api.get_adsets(campaign_id)
        except Exception as exc:
            logger.warning("手动刷新 AdSet 失败 [%s %s]: %s", platform, campaign_id, exc)
            adsets = []

        for adset in adsets:
            upsert_adset_snapshot({
                "adset_id": adset.adset_id, "campaign_id": adset.campaign_id,
                "platform": adset.platform, "category_id": category_id,
                "name": adset.name, "spend": adset.spend, "roas": adset.roas,
                "daily_budget": adset.daily_budget, "remaining_budget": adset.remaining_budget,
            })
            if wecom_url:
                check_adset_rules(adset, category, wecom_url)

        try:
            ads = api.get_ads(campaign_id, window_days=category["ctr_window_days"])
        except Exception as exc:
            logger.warning("手动刷新 Ad 失败 [%s %s]: %s", platform, campaign_id, exc)
            ads = []

        for ad in ads:
            upsert_ad_snapshot({
                "ad_id": ad.ad_id, "adset_id": ad.adset_id, "campaign_id": ad.campaign_id,
                "platform": ad.platform, "category_id": category_id,
                "name": ad.name, "ctr": ad.ctr, "impressions": ad.impressions,
            })
            if wecom_url:
                check_ad_rules(ad, category, wecom_url)
