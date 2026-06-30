import logging
from api.base import AdSetData, AdData
from db.crud import was_alerted_recently, create_alert_record
from notify.wecom import send_wecom_text, fmt_adset_alert, fmt_ad_alert

logger = logging.getLogger(__name__)


def check_adset_rules(adset: AdSetData, category: dict, wecom_url: str) -> list:
    """检查 Ad Set 层级的三条规则，返回触发的 rule_type 列表"""
    triggered = []

    # Rule 1: 高消耗低 ROAS
    if adset.spend >= category["min_spend_trigger"] and adset.roas <= category["min_roas"]:
        if not was_alerted_recently(adset.adset_id, "high_spend_low_roas"):
            msg = fmt_adset_alert(
                "high_spend_low_roas", adset.platform, category["name"],
                adset.name, adset.adset_id, adset.spend, adset.roas,
                category["min_roas"], adset.daily_budget, adset.remaining_budget,
            )
            send_wecom_text(wecom_url, msg, [category["pitcher_userid"]])
            create_alert_record(adset.adset_id, "adset", adset.platform, category["id"], "high_spend_low_roas")
            triggered.append("high_spend_low_roas")

    # Rule 2: 高 ROAS 可放量
    if adset.roas >= category["scale_roas"] and adset.spend < adset.daily_budget:
        if not was_alerted_recently(adset.adset_id, "high_roas_scale"):
            msg = fmt_adset_alert(
                "high_roas_scale", adset.platform, category["name"],
                adset.name, adset.adset_id, adset.spend, adset.roas,
                category["scale_roas"], adset.daily_budget, adset.remaining_budget,
            )
            send_wecom_text(wecom_url, msg, [category["pitcher_userid"]])
            create_alert_record(adset.adset_id, "adset", adset.platform, category["id"], "high_roas_scale")
            triggered.append("high_roas_scale")

    # Rule 3: 预算即将耗尽
    if adset.daily_budget > 0 and adset.remaining_budget <= adset.daily_budget * 0.1:
        if not was_alerted_recently(adset.adset_id, "budget_low"):
            msg = fmt_adset_alert(
                "budget_low", adset.platform, category["name"],
                adset.name, adset.adset_id, adset.spend, adset.roas,
                category["min_roas"], adset.daily_budget, adset.remaining_budget,
            )
            send_wecom_text(wecom_url, msg, [category["pitcher_userid"]])
            create_alert_record(adset.adset_id, "adset", adset.platform, category["id"], "budget_low")
            triggered.append("budget_low")

    return triggered


def check_ad_rules(ad: AdData, category: dict, wecom_url: str) -> list:
    """检查 Ad 层级的低 CTR 规则，返回触发的 rule_type 列表"""
    triggered = []

    # Rule 4: 低点击率素材
    if ad.ctr <= category["ctr_threshold"] and ad.impressions >= category["ctr_min_impressions"]:
        if not was_alerted_recently(ad.ad_id, "low_ctr"):
            msg = fmt_ad_alert(
                ad.platform, category["name"], ad.name, ad.ad_id,
                ad.ctr, category["ctr_threshold"], ad.impressions, category["ctr_window_days"],
            )
            mentioned = [category["pitcher_userid"]]
            if category.get("designer_userid"):
                mentioned.append(category["designer_userid"])
            send_wecom_text(wecom_url, msg, mentioned)
            create_alert_record(ad.ad_id, "ad", ad.platform, category["id"], "low_ctr")
            triggered.append("low_ctr")

    return triggered
