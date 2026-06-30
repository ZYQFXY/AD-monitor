import time
import logging
from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from db.crud import (
    get_all_categories, get_category, create_category, update_category, delete_category,
    get_bindings_by_category, add_binding, delete_binding,
    get_latest_adset_snapshots, get_latest_ad_snapshots,
    get_config, set_config,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ping")
async def ping():
    return {"status": "ok"}
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

_refresh_cooldowns: dict = {}
_COOLDOWN_SECS = 300


# ── 全局配置 ────────────────────────────────────────────────────────────────

@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):
    return templates.TemplateResponse(request, "settings.html", {"webhook_url": get_config("wecom_webhook_url"),
        "msg": request.query_params.get("msg", ""),})


@router.post("/settings")
async def save_settings(webhook_url: str = Form(...)):
    set_config("wecom_webhook_url", webhook_url)
    return RedirectResponse("/settings?msg=saved", status_code=303)


# ── 品类列表 ────────────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {"categories": get_all_categories(),
        "msg": request.query_params.get("msg", ""),})


# ── 品类新增 / 编辑 ──────────────────────────────────────────────────────────

@router.get("/categories/new", response_class=HTMLResponse)
async def new_category_page(request: Request):
    return templates.TemplateResponse(request, "category_form.html", {"cat": None})


@router.post("/categories/new")
async def create_category_post(
    name: str = Form(...), pitcher_userid: str = Form(...),
    designer_userid: str = Form(""),
    min_roas: float = Form(1.2), scale_roas: float = Form(2.5),
    min_spend_trigger: float = Form(500.0), ctr_threshold: float = Form(0.012),
    ctr_min_impressions: int = Form(10000), ctr_window_days: int = Form(7),
):
    create_category({
        "name": name, "pitcher_userid": pitcher_userid, "designer_userid": designer_userid,
        "min_roas": min_roas, "scale_roas": scale_roas, "min_spend_trigger": min_spend_trigger,
        "ctr_threshold": ctr_threshold, "ctr_min_impressions": ctr_min_impressions,
        "ctr_window_days": ctr_window_days,
    })
    return RedirectResponse("/?msg=created", status_code=303)


@router.get("/categories/{cat_id}/edit", response_class=HTMLResponse)
async def edit_category_page(request: Request, cat_id: int):
    cat = get_category(cat_id)
    if not cat:
        raise HTTPException(404)
    return templates.TemplateResponse(request, "category_form.html", {"cat": cat})


@router.post("/categories/{cat_id}/edit")
async def update_category_post(
    cat_id: int,
    name: str = Form(...), pitcher_userid: str = Form(...),
    designer_userid: str = Form(""),
    min_roas: float = Form(...), scale_roas: float = Form(...),
    min_spend_trigger: float = Form(...), ctr_threshold: float = Form(...),
    ctr_min_impressions: int = Form(...), ctr_window_days: int = Form(...),
):
    update_category(cat_id, {
        "name": name, "pitcher_userid": pitcher_userid, "designer_userid": designer_userid,
        "min_roas": min_roas, "scale_roas": scale_roas, "min_spend_trigger": min_spend_trigger,
        "ctr_threshold": ctr_threshold, "ctr_min_impressions": ctr_min_impressions,
        "ctr_window_days": ctr_window_days,
    })
    return RedirectResponse("/?msg=updated", status_code=303)


@router.post("/categories/{cat_id}/delete")
async def delete_category_post(cat_id: int):
    delete_category(cat_id)
    return RedirectResponse("/?msg=deleted", status_code=303)


# ── Campaign 绑定 ────────────────────────────────────────────────────────────

@router.get("/categories/{cat_id}/campaigns", response_class=HTMLResponse)
async def campaigns_page(request: Request, cat_id: int):
    cat = get_category(cat_id)
    if not cat:
        raise HTTPException(404)
    return templates.TemplateResponse(request, "campaign_bind.html", {"cat": cat,
        "bindings": get_bindings_by_category(cat_id),
        "msg": request.query_params.get("msg", ""),})


@router.post("/categories/{cat_id}/campaigns")
async def add_binding_post(cat_id: int, campaign_id: str = Form(...), platform: str = Form(...)):
    add_binding(campaign_id.strip(), platform, cat_id)
    return RedirectResponse(f"/categories/{cat_id}/campaigns?msg=added", status_code=303)


@router.post("/categories/{cat_id}/campaigns/{binding_id}/delete")
async def delete_binding_post(cat_id: int, binding_id: int):
    delete_binding(binding_id)
    return RedirectResponse(f"/categories/{cat_id}/campaigns?msg=removed", status_code=303)


# ── 数据展示 + 手动刷新 ───────────────────────────────────────────────────────

@router.get("/categories/{cat_id}/data", response_class=HTMLResponse)
async def category_data_page(request: Request, cat_id: int):
    cat = get_category(cat_id)
    if not cat:
        raise HTTPException(404)
    last_refresh = _refresh_cooldowns.get(cat_id, 0)
    cooldown_remaining = max(0, int(_COOLDOWN_SECS - (time.time() - last_refresh)))
    return templates.TemplateResponse(request, "category_data.html", {"cat": cat,
        "adsets": get_latest_adset_snapshots(cat_id),
        "ads": get_latest_ad_snapshots(cat_id),
        "cooldown_remaining": cooldown_remaining,
        "msg": request.query_params.get("msg", ""),})


@router.post("/categories/{cat_id}/refresh")
async def manual_refresh(cat_id: int):
    last = _refresh_cooldowns.get(cat_id, 0)
    if time.time() - last < _COOLDOWN_SECS:
        remaining = int(_COOLDOWN_SECS - (time.time() - last))
        return RedirectResponse(f"/categories/{cat_id}/data?msg=cooldown_{remaining}", status_code=303)

    _refresh_cooldowns[cat_id] = time.time()
    try:
        from scheduler.jobs import run_category_refresh
        run_category_refresh(cat_id)
    except Exception as exc:
        logger.error("手动刷新失败 cat_id=%s: %s", cat_id, exc)
        return RedirectResponse(f"/categories/{cat_id}/data?msg=error", status_code=303)

    return RedirectResponse(f"/categories/{cat_id}/data?msg=refreshed", status_code=303)
