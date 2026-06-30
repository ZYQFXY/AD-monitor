from notify.wecom import fmt_adset_alert, fmt_ad_alert


def test_high_spend_low_roas_format():
    msg = fmt_adset_alert("high_spend_low_roas", "facebook", "女装",
                          "广告组A", "adset_001", 1200.0, 0.8, 1.2, 2000.0, 800.0)
    assert "高消耗低 ROAS" in msg
    assert "facebook" in msg
    assert "女装" in msg
    assert "1200.00" in msg
    assert "0.80" in msg
    assert "红线：1.20" in msg


def test_high_roas_scale_format():
    msg = fmt_adset_alert("high_roas_scale", "google", "3C数码",
                          "广告组B", "adset_002", 500.0, 3.2, 2.5, 1500.0, 1000.0)
    assert "高 ROAS 可放量" in msg
    assert "增量线：2.50" in msg


def test_budget_low_format():
    msg = fmt_adset_alert("budget_low", "tiktok", "家居",
                          "广告组C", "adset_003", 900.0, 1.5, 1.2, 1000.0, 80.0)
    assert "预算即将耗尽" in msg
    assert "80.00" in msg
    assert "1000.00" in msg


def test_low_ctr_format():
    msg = fmt_ad_alert("tiktok", "女装", "视频素材01", "ad_001",
                       0.005, 0.012, 20000, 7)
    assert "点击率过低" in msg
    assert "0.50%" in msg
    assert "1.20%" in msg
    assert "20,000" in msg
    assert "7" in msg
