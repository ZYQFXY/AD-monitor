import pytest
from unittest.mock import patch, MagicMock
from api.base import AdSetData, AdData
from rules.engine import check_adset_rules, check_ad_rules

CATEGORY = {
    "id": 1, "name": "女装", "pitcher_userid": "Zhao",
    "designer_userid": "designer1",
    "min_roas": 1.2, "scale_roas": 2.5, "min_spend_trigger": 500.0,
    "ctr_threshold": 0.012, "ctr_min_impressions": 10000, "ctr_window_days": 7,
}
WEBHOOK = "http://mock-webhook"


def make_adset(**kwargs) -> AdSetData:
    defaults = dict(adset_id="adset_001", campaign_id="camp_001", platform="facebook",
                    name="测试广告组", spend=600.0, roas=0.8,
                    daily_budget=1000.0, remaining_budget=400.0)
    defaults.update(kwargs)
    return AdSetData(**defaults)


def make_ad(**kwargs) -> AdData:
    defaults = dict(ad_id="ad_001", adset_id="adset_001", campaign_id="camp_001",
                    platform="facebook", name="测试素材", ctr=0.005, impressions=15000)
    defaults.update(kwargs)
    return AdData(**defaults)


@patch("rules.engine.create_alert_record")
@patch("rules.engine.send_wecom_text")
@patch("rules.engine.was_alerted_recently", return_value=False)
class TestAdSetRules:
    def test_high_spend_low_roas_triggers(self, mock_dedup, mock_send, mock_record):
        adset = make_adset(spend=600.0, roas=0.8)  # spend≥500, roas≤1.2
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert "high_spend_low_roas" in triggered
        mock_send.assert_called()
        mock_record.assert_called()

    def test_high_spend_low_roas_no_trigger_when_roas_ok(self, mock_dedup, mock_send, mock_record):
        adset = make_adset(spend=600.0, roas=1.5)  # roas > min_roas
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert "high_spend_low_roas" not in triggered

    def test_high_spend_low_roas_no_trigger_when_spend_low(self, mock_dedup, mock_send, mock_record):
        adset = make_adset(spend=100.0, roas=0.5)  # spend < min_spend_trigger
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert "high_spend_low_roas" not in triggered

    def test_high_roas_scale_triggers(self, mock_dedup, mock_send, mock_record):
        adset = make_adset(roas=3.0, spend=500.0, daily_budget=1000.0)  # roas≥2.5, spend<budget
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert "high_roas_scale" in triggered

    def test_high_roas_scale_no_trigger_when_maxed(self, mock_dedup, mock_send, mock_record):
        adset = make_adset(roas=3.0, spend=1000.0, daily_budget=1000.0)  # spend已达预算
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert "high_roas_scale" not in triggered

    def test_budget_low_triggers(self, mock_dedup, mock_send, mock_record):
        adset = make_adset(daily_budget=1000.0, remaining_budget=80.0)  # ≤10%
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert "budget_low" in triggered

    def test_budget_low_no_trigger_when_sufficient(self, mock_dedup, mock_send, mock_record):
        adset = make_adset(daily_budget=1000.0, remaining_budget=200.0)  # >10%
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert "budget_low" not in triggered

    def test_dedup_suppresses_alert(self, mock_dedup, mock_send, mock_record):
        mock_dedup.return_value = True  # 已发过
        adset = make_adset(spend=600.0, roas=0.8)
        triggered = check_adset_rules(adset, CATEGORY, WEBHOOK)
        assert triggered == []
        mock_send.assert_not_called()


@patch("rules.engine.create_alert_record")
@patch("rules.engine.send_wecom_text")
@patch("rules.engine.was_alerted_recently", return_value=False)
class TestAdRules:
    def test_low_ctr_triggers(self, mock_dedup, mock_send, mock_record):
        ad = make_ad(ctr=0.005, impressions=15000)  # ctr≤0.012, impressions≥10000
        triggered = check_ad_rules(ad, CATEGORY, WEBHOOK)
        assert "low_ctr" in triggered

    def test_low_ctr_no_trigger_when_ctr_ok(self, mock_dedup, mock_send, mock_record):
        ad = make_ad(ctr=0.02, impressions=15000)
        triggered = check_ad_rules(ad, CATEGORY, WEBHOOK)
        assert triggered == []

    def test_low_ctr_no_trigger_when_impressions_insufficient(self, mock_dedup, mock_send, mock_record):
        ad = make_ad(ctr=0.005, impressions=5000)  # 展示量不足
        triggered = check_ad_rules(ad, CATEGORY, WEBHOOK)
        assert triggered == []

    def test_low_ctr_mentions_designer(self, mock_dedup, mock_send, mock_record):
        ad = make_ad(ctr=0.005, impressions=15000)
        check_ad_rules(ad, CATEGORY, WEBHOOK)
        _, kwargs = mock_send.call_args if mock_send.call_args else (None, {})
        call_args = mock_send.call_args[0]
        mentioned = call_args[2]
        assert "Zhao" in mentioned
        assert "designer1" in mentioned
