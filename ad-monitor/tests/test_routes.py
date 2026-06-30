import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_db):
    import importlib
    import db.database as dbmod
    importlib.reload(dbmod)
    from web.routes import router
    client = TestClient(router, raise_server_exceptions=True)
    return client


CAT_FORM = {
    "name": "女装", "pitcher_userid": "Zhao", "designer_userid": "designer1",
    "min_roas": "1.2", "scale_roas": "2.5", "min_spend_trigger": "500",
    "ctr_threshold": "0.012", "ctr_min_impressions": "10000", "ctr_window_days": "7",
}


class TestSettingsRoute:
    def test_get_settings(self, client):
        r = client.get("/settings")
        assert r.status_code == 200
        assert "Webhook" in r.text

    def test_save_settings(self, client):
        r = client.post("/settings", data={"webhook_url": "https://example.com/hook"},
                        follow_redirects=True)
        assert r.status_code == 200
        assert "saved" in str(r.url)


class TestCategoryRoutes:
    def test_index_empty(self, client):
        r = client.get("/")
        assert r.status_code == 200
        assert "暂无品类" in r.text

    def test_create_category(self, client):
        r = client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        assert r.status_code == 200
        assert "女装" in r.text

    def test_edit_category(self, client):
        client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        r = client.post("/categories/1/edit",
                        data={**CAT_FORM, "min_roas": "1.5"}, follow_redirects=True)
        assert r.status_code == 200

    def test_delete_category(self, client):
        client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        r = client.post("/categories/1/delete", follow_redirects=True)
        assert r.status_code == 200
        assert "deleted" in str(r.url)


class TestCampaignBindRoutes:
    def test_bind_campaign(self, client):
        client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        r = client.post("/categories/1/campaigns",
                        data={"campaign_id": "camp_001", "platform": "facebook"},
                        follow_redirects=True)
        assert r.status_code == 200
        assert "camp_001" in r.text

    def test_delete_binding(self, client):
        client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        client.post("/categories/1/campaigns",
                    data={"campaign_id": "camp_001", "platform": "facebook"},
                    follow_redirects=True)
        r = client.post("/categories/1/campaigns/1/delete", follow_redirects=True)
        assert r.status_code == 200


class TestDataAndRefreshRoutes:
    def test_data_page(self, client):
        client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        r = client.get("/categories/1/data")
        assert r.status_code == 200
        assert "立即刷新" in r.text

    def test_manual_refresh(self, client):
        client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        client.post("/categories/1/campaigns",
                    data={"campaign_id": "camp_fb_001", "platform": "facebook"},
                    follow_redirects=False)
        r = client.post("/categories/1/refresh", follow_redirects=True)
        assert r.status_code == 200

    def test_refresh_cooldown(self, client):
        import time
        from web import routes as rt
        client.post("/categories/new", data=CAT_FORM, follow_redirects=True)
        rt._refresh_cooldowns[1] = time.time()  # 模拟刚刚刷新过
        r = client.post("/categories/1/refresh", follow_redirects=True)
        assert "cooldown" in str(r.url)
