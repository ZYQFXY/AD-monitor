import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from db.database import init_db
from db.crud import get_config, set_config
from web.routes import router
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

scheduler = BackgroundScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # 写入默认 Webhook URL（首次启动时）
    if not get_config("wecom_webhook_url") and config.WECOM_WEBHOOK_URL:
        set_config("wecom_webhook_url", config.WECOM_WEBHOOK_URL)

    from scheduler.jobs import run_monitoring_job
    scheduler.add_job(run_monitoring_job, "interval", hours=1, id="monitoring", replace_existing=True)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="广告监控系统", lifespan=lifespan)
app.include_router(router)
