import requests
from typing import List


def send_wecom_text(webhook_url: str, content: str, mentioned_list: List[str]) -> bool:
    payload = {
        "msgtype": "text",
        "text": {
            "content": content,
            "mentioned_list": mentioned_list,
        },
    }
    try:
        resp = requests.post(webhook_url, json=payload, timeout=5)
        return resp.status_code == 200 and resp.json().get("errcode") == 0
    except Exception:
        return False


def fmt_adset_alert(rule_type: str, platform: str, category_name: str,
                    adset_name: str, adset_id: str, spend: float, roas: float,
                    threshold: float, daily_budget: float, remaining_budget: float) -> str:
    if rule_type == "high_spend_low_roas":
        return (
            f"[广告预警] 高消耗低 ROAS\n"
            f"平台：{platform} | 品类：{category_name}\n"
            f"广告组：{adset_name}（{adset_id}）\n"
            f"今日消耗：¥{spend:.2f} | ROAS：{roas:.2f}（红线：{threshold:.2f}）\n"
            f"建议：立即暂停该广告组"
        )
    if rule_type == "high_roas_scale":
        return (
            f"[广告预警] 高 ROAS 可放量\n"
            f"平台：{platform} | 品类：{category_name}\n"
            f"广告组：{adset_name}（{adset_id}）\n"
            f"今日消耗：¥{spend:.2f} | ROAS：{roas:.2f}（增量线：{threshold:.2f}）\n"
            f"建议：增加预算"
        )
    # budget_low
    return (
        f"[广告预警] 预算即将耗尽\n"
        f"平台：{platform} | 品类：{category_name}\n"
        f"广告组：{adset_name}（{adset_id}）\n"
        f"剩余预算：¥{remaining_budget:.2f}（日预算：¥{daily_budget:.2f}）\n"
        f"建议：决策是否续预算"
    )


def fmt_ad_alert(platform: str, category_name: str, ad_name: str, ad_id: str,
                 ctr: float, ctr_threshold: float, impressions: int,
                 window_days: int) -> str:
    return (
        f"[素材预警] 点击率过低\n"
        f"平台：{platform} | 品类：{category_name}\n"
        f"素材：{ad_name}（{ad_id}）\n"
        f"近 {window_days} 天 CTR：{ctr:.2%}（红线：{ctr_threshold:.2%}）| 展示量：{impressions:,}\n"
        f"建议：更换该素材"
    )
