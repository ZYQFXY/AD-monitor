SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS global_config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS categories (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    name                TEXT    NOT NULL UNIQUE,
    pitcher_userid      TEXT    NOT NULL,
    designer_userid     TEXT    NOT NULL DEFAULT '',
    min_roas            REAL    NOT NULL DEFAULT 1.2,
    scale_roas          REAL    NOT NULL DEFAULT 2.5,
    min_spend_trigger   REAL    NOT NULL DEFAULT 500.0,
    ctr_threshold       REAL    NOT NULL DEFAULT 0.012,
    ctr_min_impressions INTEGER NOT NULL DEFAULT 10000,
    ctr_window_days     INTEGER NOT NULL DEFAULT 7,
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS campaign_bindings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id TEXT    NOT NULL,
    platform    TEXT    NOT NULL CHECK(platform IN ('facebook','google','tiktok')),
    category_id INTEGER NOT NULL REFERENCES categories(id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, platform)
);

CREATE TABLE IF NOT EXISTS adset_snapshots (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    adset_id         TEXT  NOT NULL,
    campaign_id      TEXT  NOT NULL,
    platform         TEXT  NOT NULL,
    category_id      INTEGER NOT NULL,
    name             TEXT  NOT NULL DEFAULT '',
    spend            REAL  NOT NULL DEFAULT 0.0,
    roas             REAL  NOT NULL DEFAULT 0.0,
    daily_budget     REAL  NOT NULL DEFAULT 0.0,
    remaining_budget REAL  NOT NULL DEFAULT 0.0,
    snapshot_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ad_snapshots (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_id       TEXT    NOT NULL,
    adset_id    TEXT    NOT NULL,
    campaign_id TEXT    NOT NULL,
    platform    TEXT    NOT NULL,
    category_id INTEGER NOT NULL,
    name        TEXT    NOT NULL DEFAULT '',
    ctr         REAL    NOT NULL DEFAULT 0.0,
    impressions INTEGER NOT NULL DEFAULT 0,
    snapshot_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS alert_records (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_id    TEXT NOT NULL,
    entity_type  TEXT NOT NULL CHECK(entity_type IN ('adset','ad')),
    platform     TEXT NOT NULL,
    category_id  INTEGER NOT NULL,
    rule_type    TEXT NOT NULL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""
