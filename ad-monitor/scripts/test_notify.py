"""
直接测试四种企微通知是否能到达群组。
绕过规则引擎和去重表，只验证消息推送本身。
运行：python scripts/test_notify.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from notify.wecom import send_wecom_text, fmt_adset_alert, fmt_ad_alert
import config

WEBHOOK = config.WECOM_WEBHOOK_URL
PITCHER  = "Zhao"


def run(label: str, msg: str, mentioned: list) -> None:
    ok = send_wecom_text(WEBHOOK, msg, mentioned)
    status = "[OK] 发送成功" if ok else "[FAIL] 发送失败（检查 Webhook 地址或网络）"
    print(f"[{label}] {status}")


def test_high_spend_low_roas():
    msg = fmt_adset_alert(
        "high_spend_low_roas", "Facebook", "女装",
        "广告组-夏季连衣裙A", "fb_adset_001",
        spend=1500.0, roas=0.9, threshold=1.2,
        daily_budget=2000.0, remaining_budget=500.0,
    )
    run("高消耗低ROAS", msg, [PITCHER])


def test_high_roas_scale():
    msg = fmt_adset_alert(
        "high_roas_scale", "Google", "3C数码",
        "广告组-搜索B", "gg_adset_002",
        spend=800.0, roas=3.5, threshold=2.5,
        daily_budget=2000.0, remaining_budget=1200.0,
    )
    run("高ROAS可放量", msg, [PITCHER])


def test_budget_low():
    msg = fmt_adset_alert(
        "budget_low", "TikTok", "家居",
        "广告组-信息流C", "tt_adset_003",
        spend=1850.0, roas=1.5, threshold=1.2,
        daily_budget=2000.0, remaining_budget=150.0,
    )
    run("预算即将耗尽", msg, [PITCHER])


def test_low_ctr():
    msg = fmt_ad_alert(
        "TikTok", "女装",
        "视频素材-春季上新01", "tt_ad_001",
        ctr=0.005, ctr_threshold=0.012,
        impressions=25000, window_days=7,
    )
    run("低CTR素材", msg, [PITCHER])


if __name__ == "__main__":
    if not WEBHOOK:
        print("错误：WECOM_WEBHOOK_URL 未配置，请检查 .env 或系统设置页")
        sys.exit(1)
    print(f"Webhook: {WEBHOOK[:60]}...")
    print(f"投手 userid: {PITCHER}")
    print("-" * 40)
    test_high_spend_low_roas()
    test_high_roas_scale()
    test_budget_low()
    test_low_ctr()
    print("-" * 40)
    print("完成。请检查企微群是否收到 4 条消息。")
