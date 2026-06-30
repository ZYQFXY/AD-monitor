import pytest
from db.crud import (
    create_category, get_category, get_all_categories, update_category, delete_category,
    add_binding, get_bindings_by_category, delete_binding,
    upsert_adset_snapshot, get_latest_adset_snapshots,
    upsert_ad_snapshot, get_latest_ad_snapshots,
    was_alerted_recently, create_alert_record,
    get_config, set_config,
)

CAT = {
    "name": "女装", "pitcher_userid": "Zhao", "designer_userid": "designer1",
    "min_roas": 1.2, "scale_roas": 2.5, "min_spend_trigger": 500.0,
    "ctr_threshold": 0.012, "ctr_min_impressions": 10000, "ctr_window_days": 7,
}


class TestCategories:
    def test_create_and_get(self, tmp_db):
        cat_id = create_category(CAT)
        cat = get_category(cat_id)
        assert cat["name"] == "女装"
        assert cat["pitcher_userid"] == "Zhao"
        assert cat["min_roas"] == 1.2

    def test_get_all(self, tmp_db):
        create_category(CAT)
        create_category({**CAT, "name": "3C数码"})
        assert len(get_all_categories()) == 2

    def test_update(self, tmp_db):
        cat_id = create_category(CAT)
        update_category(cat_id, {**CAT, "min_roas": 1.5})
        assert get_category(cat_id)["min_roas"] == 1.5

    def test_delete(self, tmp_db):
        cat_id = create_category(CAT)
        delete_category(cat_id)
        assert get_category(cat_id) is None


class TestBindings:
    def test_add_and_list(self, tmp_db):
        cat_id = create_category(CAT)
        add_binding("camp_fb_001", "facebook", cat_id)
        add_binding("camp_gg_001", "google", cat_id)
        bindings = get_bindings_by_category(cat_id)
        assert len(bindings) == 2

    def test_duplicate_binding_ignored(self, tmp_db):
        cat_id = create_category(CAT)
        add_binding("camp_fb_001", "facebook", cat_id)
        add_binding("camp_fb_001", "facebook", cat_id)  # 重复
        assert len(get_bindings_by_category(cat_id)) == 1

    def test_delete_binding(self, tmp_db):
        cat_id = create_category(CAT)
        add_binding("camp_fb_001", "facebook", cat_id)
        b_id = get_bindings_by_category(cat_id)[0]["id"]
        delete_binding(b_id)
        assert len(get_bindings_by_category(cat_id)) == 0


class TestSnapshots:
    def test_adset_snapshot(self, tmp_db):
        cat_id = create_category(CAT)
        upsert_adset_snapshot({"adset_id": "a1", "campaign_id": "c1", "platform": "facebook",
                                "category_id": cat_id, "name": "广告组A",
                                "spend": 500.0, "roas": 1.5, "daily_budget": 1000.0, "remaining_budget": 500.0})
        rows = get_latest_adset_snapshots(cat_id)
        assert len(rows) == 1
        assert rows[0]["roas"] == 1.5

    def test_ad_snapshot(self, tmp_db):
        cat_id = create_category(CAT)
        upsert_ad_snapshot({"ad_id": "ad1", "adset_id": "a1", "campaign_id": "c1",
                             "platform": "tiktok", "category_id": cat_id, "name": "素材01",
                             "ctr": 0.005, "impressions": 20000})
        rows = get_latest_ad_snapshots(cat_id)
        assert len(rows) == 1
        assert rows[0]["ctr"] == 0.005


class TestAlertRecords:
    def test_not_alerted_initially(self, tmp_db):
        create_category(CAT)
        assert not was_alerted_recently("adset_001", "high_spend_low_roas")

    def test_alerted_after_record(self, tmp_db):
        cat_id = create_category(CAT)
        create_alert_record("adset_001", "adset", "facebook", cat_id, "high_spend_low_roas")
        assert was_alerted_recently("adset_001", "high_spend_low_roas")

    def test_different_rule_not_deduped(self, tmp_db):
        cat_id = create_category(CAT)
        create_alert_record("adset_001", "adset", "facebook", cat_id, "high_spend_low_roas")
        assert not was_alerted_recently("adset_001", "budget_low")


class TestConfig:
    def test_set_and_get(self, tmp_db):
        set_config("wecom_webhook_url", "https://example.com/webhook")
        assert get_config("wecom_webhook_url") == "https://example.com/webhook"

    def test_get_missing_returns_empty(self, tmp_db):
        assert get_config("nonexistent_key") == ""

    def test_update_existing(self, tmp_db):
        set_config("key1", "v1")
        set_config("key1", "v2")
        assert get_config("key1") == "v2"
