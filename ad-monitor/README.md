# 跨境广告 AI 监控系统（第一阶段）

跨平台广告数据自动巡检系统，支持 Facebook / Google / TikTok 三平台，通过规则引擎替代人工盯盘，异常时自动推送企业微信通知。

---

## 功能概览

| 功能 | 说明 |
|------|------|
| 多平台数据拉取 | 每小时自动拉取三平台 Ad Set 和 Ad 层级数据 |
| 规则预警引擎 | 4 条预警规则，按品类独立配置阈值 |
| 企微自动通知 | 触发规则时推送群消息，@指定投手或设计师 |
| Web 配置界面 | 内网浏览器操作，无需修改任何配置文件 |
| 手动刷新 | 品类页「立即刷新」按钮，5 分钟冷却 |
| 历史快照入库 | 保留 Ad Set / Ad 双层数据，供后续 AI 决策使用 |
| 告警去重 | 同一广告组同一规则 24 小时内只通知一次 |

---

## 预警规则

| 规则 | 判断层级 | 触发条件 | 通知对象 |
|------|----------|----------|----------|
| 高消耗低 ROAS | Ad Set | 当日消耗 ≥ 最低触发值 且 ROAS ≤ 红线 | @投手 |
| 高 ROAS 可放量 | Ad Set | ROAS ≥ 增量线 且 消耗未达日预算 | @投手 |
| 预算即将耗尽 | Ad Set | 剩余预算 ≤ 日预算 × 10% | @投手 |
| 低点击率素材 | Ad | 近 N 天 CTR ≤ 红线 且 展示量 ≥ 最低展示量 | @投手 + @设计师 |

---

## 项目结构

```
ad-monitor/
├── main.py                     # 入口：FastAPI 应用 + APScheduler 调度器
├── config.py                   # 环境变量加载（API Keys、Webhook URL）
├── requirements.txt
├── .env                        # 密钥文件（不进代码仓库）
│
├── api/                        # 各平台数据拉取
│   ├── base.py                 # 抽象基类 + AdSetData / AdData 数据结构
│   ├── facebook.py             # Facebook Marketing API（含 mock）
│   ├── google.py               # Google Ads API（含 mock）
│   └── tiktok.py               # TikTok Marketing API（含 mock）
│
├── rules/
│   └── engine.py               # 4 条规则引擎，含告警去重
│
├── notify/
│   └── wecom.py                # 企微 Webhook 推送 + 4 种消息格式
│
├── scheduler/
│   └── jobs.py                 # 每小时定时任务 + 手动刷新入口
│
├── db/
│   ├── models.py               # 6 张表 SQL 定义
│   ├── database.py             # SQLite 连接 + 初始化
│   └── crud.py                 # 全部增删改查操作
│
├── web/
│   ├── routes.py               # 所有 FastAPI 路由
│   └── templates/
│       ├── layout.html         # 公共布局
│       ├── index.html          # 品类列表
│       ├── category_form.html  # 品类新增 / 编辑
│       ├── campaign_bind.html  # Campaign 绑定管理
│       ├── category_data.html  # 数据展示 + 手动刷新
│       └── settings.html       # 全局配置（Webhook URL）
│
├── scripts/
│   └── test_notify.py          # 企微通知独立测试脚本
│
└── tests/
    ├── conftest.py
    ├── test_crud.py            # 数据库 CRUD 测试
    ├── test_rules.py           # 规则引擎测试
    ├── test_wecom.py           # 通知格式测试
    └── test_routes.py          # Web 路由测试
```

---

## 数据库表

| 表名 | 用途 |
|------|------|
| `categories` | 品类配置：名称、投手 userid、设计师 userid、各项阈值 |
| `campaign_bindings` | Campaign 绑定：campaign_id、platform、category_id |
| `global_config` | 全局配置（企微 Webhook URL） |
| `adset_snapshots` | Ad Set 层级快照（spend、roas、budget） |
| `ad_snapshots` | Ad 层级快照（ctr、impressions） |
| `alert_records` | 告警去重记录（entity_id + rule_type + 24h 窗口） |

---

## 快速开始

### 1. 安装依赖

```bash
cd ad-monitor
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env`，填写各平台 API 凭据和企微 Webhook：

```env
# Facebook
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_AD_ACCOUNT_ID=act_xxxxxxx

# Google Ads
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_customer_id

# TikTok
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_ADVERTISER_ID=your_advertiser_id

# 企业微信
WECOM_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY
```

### 3. 启动服务

```bash
# 开发模式（自动热重载）
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

浏览器访问 `http://127.0.0.1:8000`

> 注意：Windows 上请使用 `127.0.0.1` 而非 `localhost`，避免 IPv6 解析导致连接挂起。

### 4. 初始配置步骤

1. 进入「系统设置」填写企微群 Webhook URL
2. 在「品类列表」新增品类，填写投手 / 设计师企微 userid 和各项阈值
3. 进入品类的「绑定」页面，添加该品类在各平台的 Campaign ID
4. 点击「立即刷新」验证数据拉取是否正常

---

## 接入真实 API

当前三平台均为 mock 占位符实现。接入真实 API 时，只需替换对应文件中 `TODO` 注释以下的实现，其余代码无需改动：

| 文件 | 替换内容 |
|------|----------|
| `api/facebook.py` | 接入 `facebook_business` SDK |
| `api/google.py` | 接入 `google-ads` Python SDK |
| `api/tiktok.py` | 接入 TikTok Marketing API（HTTP 请求） |

各平台 API 认证方式：

| 平台 | 认证方式 | 说明 |
|------|----------|------|
| Facebook | OAuth 2.0 Long-lived Token | 在 Meta 开发者后台生成，有效期 60 天，需定期刷新 |
| Google Ads | Service Account / OAuth 2.0 | 通过 Google Cloud Console 创建，使用 Refresh Token 自动续期 |
| TikTok | App Access Token | 在 TikTok for Business 后台生成 |

---

## 测试

```bash
# 运行全部自动化测试
python -m pytest tests/ -v

# 单独测试企微通知是否到达
python scripts/test_notify.py
```

测试覆盖情况：42 个测试，覆盖 CRUD、规则引擎、通知格式、全部 Web 路由。

---

## 技术栈

| 组件 | 选型 |
|------|------|
| Web 框架 | FastAPI 0.115 + Jinja2 |
| 定时调度 | APScheduler 3.10（BackgroundScheduler） |
| 数据库 | SQLite（内置，无需额外安装） |
| 企微通知 | 企业微信群机器人 Webhook |
| 测试 | pytest + httpx TestClient |
| 部署 | 内网服务器，uvicorn 直接运行 |

---

## 路线图

**当前：第一阶段（已完成）** — 纯规则预警，零 AI 决策

**第二阶段（待启动）** — 需第一阶段积累 4~8 周数据后迭代

- [ ] AI 给出调价/关停建议，投手企微卡片一键确认执行
- [ ] 小额低风险操作（±10% 调价）允许 AI 自动执行
- [ ] 评测体系：回测准确率 ≥ 85%，仿真期 2 周

---

## 注意事项

- `.env` 文件包含敏感凭据，**不要提交到代码仓库**
- 第一阶段系统只调用平台**读接口**，不执行任何广告操作，零误操作风险
- 告警去重：同一广告组同一规则 24 小时内只推送一次
- 手动刷新冷却：每个品类 5 分钟内只能触发一次，避免打满 API 配额
- 平台数据存在延迟（Facebook/Google 约 1~3 小时，TikTok 约 1 小时），手动刷新拿到的是平台当前最新可用数据
