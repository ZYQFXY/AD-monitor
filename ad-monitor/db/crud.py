from datetime import datetime, timedelta, timezone
from typing import Optional
from db.database import get_db


# ── global_config ─────────────────────────────────────────────────────────────

def get_config(key: str) -> str:
    conn = get_db()
    row = conn.execute("SELECT value FROM global_config WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else ""


def set_config(key: str, value: str) -> None:
    conn = get_db()
    conn.execute(
        "INSERT INTO global_config(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )
    conn.commit()
    conn.close()


# ── categories ────────────────────────────────────────────────────────────────

def get_all_categories() -> list:
    conn = get_db()
    rows = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category(category_id: int) -> Optional[dict]:
    conn = get_db()
    row = conn.execute("SELECT * FROM categories WHERE id=?", (category_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_category(data: dict) -> int:
    conn = get_db()
    cur = conn.execute(
        """INSERT INTO categories
           (name,pitcher_userid,designer_userid,min_roas,scale_roas,
            min_spend_trigger,ctr_threshold,ctr_min_impressions,ctr_window_days)
           VALUES(:name,:pitcher_userid,:designer_userid,:min_roas,:scale_roas,
                  :min_spend_trigger,:ctr_threshold,:ctr_min_impressions,:ctr_window_days)""",
        data,
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def update_category(category_id: int, data: dict) -> None:
    data["id"] = category_id
    conn = get_db()
    conn.execute(
        """UPDATE categories SET
           name=:name, pitcher_userid=:pitcher_userid, designer_userid=:designer_userid,
           min_roas=:min_roas, scale_roas=:scale_roas, min_spend_trigger=:min_spend_trigger,
           ctr_threshold=:ctr_threshold, ctr_min_impressions=:ctr_min_impressions,
           ctr_window_days=:ctr_window_days
           WHERE id=:id""",
        data,
    )
    conn.commit()
    conn.close()


def delete_category(category_id: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM categories WHERE id=?", (category_id,))
    conn.commit()
    conn.close()


# ── campaign_bindings ──────────────────────────────────────────────────────────

def get_bindings_by_category(category_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM campaign_bindings WHERE category_id=? ORDER BY id",
        (category_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_bindings() -> list:
    conn = get_db()
    rows = conn.execute("SELECT * FROM campaign_bindings").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_binding(campaign_id: str, platform: str, category_id: int) -> None:
    conn = get_db()
    conn.execute(
        "INSERT OR IGNORE INTO campaign_bindings(campaign_id,platform,category_id) VALUES(?,?,?)",
        (campaign_id, platform, category_id),
    )
    conn.commit()
    conn.close()


def delete_binding(binding_id: int) -> None:
    conn = get_db()
    conn.execute("DELETE FROM campaign_bindings WHERE id=?", (binding_id,))
    conn.commit()
    conn.close()


# ── snapshots ─────────────────────────────────────────────────────────────────

def upsert_adset_snapshot(data: dict) -> None:
    conn = get_db()
    conn.execute(
        """INSERT INTO adset_snapshots
           (adset_id,campaign_id,platform,category_id,name,spend,roas,daily_budget,remaining_budget)
           VALUES(:adset_id,:campaign_id,:platform,:category_id,:name,:spend,:roas,:daily_budget,:remaining_budget)""",
        data,
    )
    conn.commit()
    conn.close()


def upsert_ad_snapshot(data: dict) -> None:
    conn = get_db()
    conn.execute(
        """INSERT INTO ad_snapshots
           (ad_id,adset_id,campaign_id,platform,category_id,name,ctr,impressions)
           VALUES(:ad_id,:adset_id,:campaign_id,:platform,:category_id,:name,:ctr,:impressions)""",
        data,
    )
    conn.commit()
    conn.close()


def get_latest_adset_snapshots(category_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        """SELECT * FROM adset_snapshots
           WHERE id IN (
               SELECT MAX(id) FROM adset_snapshots
               WHERE category_id=? GROUP BY adset_id
           ) ORDER BY spend DESC""",
        (category_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_latest_ad_snapshots(category_id: int) -> list:
    conn = get_db()
    rows = conn.execute(
        """SELECT * FROM ad_snapshots
           WHERE id IN (
               SELECT MAX(id) FROM ad_snapshots
               WHERE category_id=? GROUP BY ad_id
           ) ORDER BY ctr ASC""",
        (category_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── alert_records ──────────────────────────────────────────────────────────────

def was_alerted_recently(entity_id: str, rule_type: str, hours: int = 24) -> bool:
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    conn = get_db()
    row = conn.execute(
        """SELECT 1 FROM alert_records
           WHERE entity_id=? AND rule_type=? AND triggered_at > ?
           LIMIT 1""",
        (entity_id, rule_type, cutoff.isoformat()),
    ).fetchone()
    conn.close()
    return row is not None


def create_alert_record(entity_id: str, entity_type: str, platform: str, category_id: int, rule_type: str) -> None:
    conn = get_db()
    conn.execute(
        """INSERT INTO alert_records(entity_id,entity_type,platform,category_id,rule_type)
           VALUES(?,?,?,?,?)""",
        (entity_id, entity_type, platform, category_id, rule_type),
    )
    conn.commit()
    conn.close()
