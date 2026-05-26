# ApplyPilot 中文开发文档

ApplyPilot 是一个 AI-powered Graduate Application OS，中文名可以叫“AI 申研操作台”。它的目标是把硕士申请流程里的资料填写、GPA 转换、项目数据库、项目匹配、材料清单、申请进度、邮件追踪、浏览器助手和面试准备放到一个统一工作台里。

当前版本已经从纯静态 Demo 进化为可交互 MVP：Profile 页面保存到 MySQL，Dashboard、Matches、Applications、Documents、Browser Agent 和 Portal Assistant 会读取同一个 applicant 数据并联动更新。

## 当前状态

已实现：

- Next.js App Router 前端，支持 `/en` 和 `/zh`。
- FastAPI 后端，MySQL 8 数据库，SQLAlchemy 2，Alembic migration。
- Demo applicant、学校、项目、材料、申请、邮件 seed 数据。
- Profile 真实保存到 MySQL，并自动计算 `gpa_converted_4`。
- Profile 规则分析接口 `POST /api/applicants/{id}/analyze`。
- Dashboard 聚合接口 `GET /api/dashboard/{applicant_id}`。
- Program Database 真实读取 MySQL，并支持搜索、国家、方向、学校、审核状态、置信度筛选。
- Program Match 真实根据 applicant 和 programs 计算，并写入 `program_matches`。
- Add to Application List 真实创建 application，并做去重。
- Applications Kanban 真实读取和更新状态。
- Documents 支持真实文件上传、文件校验、本地存储、下载、软删除、版本 metadata、材料状态更新，并可按项目生成 checklist。
- Crawler 支持 25 所学校官方入口 seed、robots 检查、限速、dry-run discovery、允许页面抓取、raw_pages 保存。
- Program Discovery 面向普通用户的项目发现器，支持按地区/学校/方向查找和分析官方链接，自动抓取并抽取结构化项目数据。
- Crawler Admin 面向开发者的爬虫管理后台，保留 seed、discover、fetch、extract、full pipeline 技术控制台。
- Discovery 后端支持多引擎路由（native_static/playwright + Jina Reader/Firecrawl/Apify fallback），零外部 API key 可运行。
- URL 官方域名校验，拒绝第三方中介、社交平台、login/portal/payment 页面。
- Extraction 支持 mock/rule extractor 从 raw_pages 写入 programs、program_documents、program_deadlines、program_requirements、extraction_runs。
- Recommendations 支持 mock AI recommendation，基于 reviewed 或高置信项目生成带 evidence 的推荐结果。
- Crawler 页面包含 Review Queue，可标记 reviewed / rejected 并打开 source URL。
- Browser Agent 支持 Mock、Playwright local demo、OpenCLI adapter 三种 executor。
- OpenCLI 是外部 CLI，不混入后端源码。
- Browser Agent 执行动作前经过 `risk_guard` 风险判断。
- Portal Assistant Human Approval Gate 已实现：AI/rule planner 先生成 `pending_actions`，RiskGuard 分类后再决定自动执行、等待确认或永久阻断。
- `audit_logs` 会记录 Portal Assistant 的 action proposal、approval、reject、manual completion 和 executor execution。
- Email Tracker 使用 seed/mock 邮件，但已经按 `applicant_id` 读取。
- 后端测试覆盖核心链路，当前 `pytest` 通过。
- 前端 `pnpm build` 通过。

未实现或仍是 Mock：

- 真实 OpenAI / Claude / DeepSeek 文书生成和背景分析。当前 AI 服务是规则或 mock。
- 真实邮箱 OAuth 授权、Gmail/Outlook 拉取、邮件 webhook。当前邮件来自 seed_demo_data。
- 真实学校官网登录、真实申请提交、真实付款。这些在 MVP 中明确禁用。
- Browser Agent 不会真实 final submit，不会付款，不会绕过验证码，不会保存学校账号密码。
- OpenCLI/Playwright 真正驱动复杂学校 portal 的字段识别和文件上传仍在增强中；当前已完成 pending action、人类确认闸门和 executor-backed 的基础执行闭环。
- 爬虫 pipeline 已能跑 25 所大学官方入口，但仍是 MVP 级别，没有大规模调度、代理池、增量抓取。
- Program Discovery 前端已完成，用户可自助按地区/学校/方向查找项目，后端多引擎路由已实现。
- 项目抽取仍以 mock/rule extractor 为主，没有接入真实 LLM structured extraction。
- 文书中心已有真实文件上传和 metadata，但还没有 AI 改写、版本 diff、导出 PDF/DOCX、云存储。
- 面试准备页仍是 mock 内容，没有真实问答评分或语音面试。
- Settings 页面仍是界面原型，没有完整账号、权限、通知持久化。
- 前端 server state 目前使用手写 `fetch + loading/error/success`，还没有引入 TanStack Query。
- 还没有登录/多用户权限系统。当前默认使用 demo applicant。

## 一键启动

在项目根目录运行：

```bash
./scripts/dev.sh
```

这个脚本会做这些事：

- 启动 MySQL Docker 容器。
- 安装或确认后端依赖。
- 执行 Alembic migration。
- 执行 demo seed。
- 安装或确认前端依赖。
- 启动 FastAPI。
- 启动 Next.js。
- 等待后端和前端 ready。

启动后访问：

```text
前端英文：http://localhost:3000/en
前端中文：http://localhost:3000/zh
Program Discovery：http://localhost:3000/zh/program-discovery
Profile：http://localhost:3000/zh/profile
Dashboard：http://localhost:3000/zh/dashboard
Programs：http://localhost:3000/zh/programs
Matches：http://localhost:3000/zh/matches
Browser Agent：http://localhost:3000/zh/browser-agent
Portal Assistant：http://localhost:3000/zh/portal-assistant
Crawler Admin：http://localhost:3000/zh/crawler-admin
Swagger：http://localhost:8000/docs
Health：http://localhost:8000/api/health
```

停止前后端开发服务：

```bash
./scripts/stop-dev.sh
```

注意：`stop-dev.sh` 只停止 FastAPI 和 Next.js，不会停止 MySQL。停止 MySQL：

```bash
docker compose down
```

如果你想让一键脚本启动后直接退回终端，可以使用 detached 模式：

```bash
APPLYPILOT_DETACH=1 ./scripts/dev.sh
```

## 手动启动

### 1. 启动 MySQL

```bash
docker compose up -d
```

默认 `.env.example` 使用 `3306`。如果你本机 `3306` 被占用，可以在 `.env` 里设置：

```text
MYSQL_HOST_PORT=3307
DATABASE_URL=mysql+pymysql://applypilot:applypilot_dev_password@localhost:3307/applypilot?charset=utf8mb4
```

### 2. 启动后端

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.scripts.seed_universities
python -m app.scripts.seed_demo_data
uvicorn main:app --reload
```

### 3. 启动前端

```bash
cd frontend
corepack pnpm install
corepack pnpm dev
```

## 测试命令

后端测试：

```bash
cd backend
source .venv/bin/activate
pytest
```

前端构建：

```bash
cd frontend
corepack pnpm build
```

OpenCLI 状态检查：

```bash
cd backend
source .venv/bin/activate
python -m app.scripts.check_opencli
```

Playwright 本地表单 demo：

```bash
cd backend
source .venv/bin/activate
python -m playwright install chromium
python -m app.scripts.run_playwright_demo
```

爬虫 dry run：

```bash
cd backend
source .venv/bin/activate
python -m app.scripts.crawl_programs --dry-run --max-pages-per-domain 10
```

## 技术栈

前端：

- Next.js App Router
- TypeScript
- Tailwind CSS
- lucide-react
- pnpm

后端：

- FastAPI
- Python 3.11+
- SQLAlchemy 2
- Alembic
- Pydantic
- PyMySQL
- requests
- BeautifulSoup
- Playwright Python
- python-dotenv

数据库：

- MySQL 8.4 Docker
- `utf8mb4`
- `utf8mb4_unicode_ci`
- SQLAlchemy dialect: `mysql+pymysql`

Browser Agent：

- MockExecutor
- PlaywrightExecutor
- OpenCLIExecutor
- RiskGuard

## 总体流程图

```mermaid
flowchart TD
  User["用户"] --> Frontend["Next.js 前端 /en /zh"]
  Frontend --> Profile["Profile 页面填写背景"]
  Profile --> SaveProfile["PUT /api/applicants/{id}"]
  SaveProfile --> MySQL[("MySQL applypilot")]
  SaveProfile --> GPA["后端 GPA Converter"]
  GPA --> MySQL
  Profile --> Analyze["POST /api/applicants/{id}/analyze"]
  Analyze --> ProfileAnalysis["规则背景分析 JSON"]
  Frontend --> Dashboard["Dashboard 页面"]
  Dashboard --> DashboardAPI["GET /api/dashboard/{applicant_id}"]
  DashboardAPI --> MySQL
  Frontend --> Programs["Program Database"]
  Programs --> ProgramsAPI["GET /api/programs"]
  ProgramsAPI --> MySQL
  Frontend --> Matches["Matches 页面"]
  Matches --> GenerateMatches["POST /api/matches/generate/{applicant_id}"]
  GenerateMatches --> MatchingService["Matching Service"]
  MatchingService --> MySQL
  Matches --> AddApplication["POST /api/applications"]
  AddApplication --> MySQL
  Frontend --> Documents["Documents 页面"]
  Documents --> Checklist["POST /api/documents/checklist/{program_id}"]
  Checklist --> MySQL
  Frontend --> BrowserAgent["Browser Agent 页面"]
  BrowserAgent --> StartTask["POST /api/browser-agent/start-task"]
  StartTask --> AgentService["BrowserAgentService"]
  AgentService --> RiskGuard["RiskGuard"]
  AgentService --> MockExecutor["MockExecutor"]
  AgentService --> PlaywrightExecutor["PlaywrightExecutor 本地表单"]
  AgentService --> OpenCLIExecutor["OpenCLIExecutor 外部 CLI"]
  AgentService --> MySQL
```

## 真实交互闭环

当前最重要的数据链路是：

```text
用户在 Profile 填资料
  -> PUT /api/applicants/{id}
  -> 保存 applicant 到 MySQL
  -> 后端计算 gpa_converted_4
  -> POST /api/applicants/{id}/analyze
  -> Dashboard 读取 /api/dashboard/{id}
  -> Matches 读取/生成 program_matches
  -> Add to Application List 创建 applications
  -> Documents checklist 对比 program requirements 和 user documents
  -> Browser Agent start-task 读取 applicant + program context
```

## 目录结构总览

```text
applypilot/
  README.md                  中文主文档
  docker-compose.yml         MySQL Docker Compose
  .env.example               环境变量模板
  .gitignore                 Git 忽略规则
  scripts/                   本地一键启动/停止脚本
  frontend/                  Next.js 前端
  backend/                   FastAPI 后端
  docs/                      架构和开发说明
  tools/opencli/             OpenCLI 集成文档和示例，不包含 OpenCLI 源码
```

本 README 只说明源码、配置、脚本、文档文件。以下本地生成物不逐个解释：

- `.env`
- `.DS_Store`
- `.dev-logs/`
- `.dev-pids/`
- `frontend/node_modules/`
- `frontend/.next/`
- `backend/.venv/`
- `backend/.pytest_cache/`
- `__pycache__/`
- `*.pyc`

## 根目录文件说明

| 文件 | 作用 |
|---|---|
| `README.md` | 当前中文主文档，包含启动、架构、文件说明、未实现功能。 |
| `docker-compose.yml` | 定义 MySQL 8.4 服务、端口、账号密码、数据库名、utf8mb4 字符集。 |
| `.env.example` | 环境变量模板，包含 `DATABASE_URL`、CORS、Crawler、Browser Executor、API key 占位。 |
| `.gitignore` | 忽略本地环境、依赖、构建产物、缓存和 OpenCLI 源码目录。 |

## scripts 文件说明

| 文件 | 作用 |
|---|---|
| `scripts/dev.sh` | 一键启动脚本。启动 MySQL、安装依赖、迁移数据库、seed demo 数据、启动后端和前端。 |
| `scripts/stop-dev.sh` | 停止 `dev.sh` 启动的 FastAPI 和 Next.js，保留 MySQL 容器运行。 |

## frontend 文件说明

### frontend 根配置

| 文件 | 作用 |
|---|---|
| `frontend/package.json` | 前端依赖和脚本，包含 Next.js、React、Tailwind、lucide-react。 |
| `frontend/pnpm-lock.yaml` | pnpm 锁文件，保证依赖版本一致。 |
| `frontend/pnpm-workspace.yaml` | pnpm workspace 配置。 |
| `frontend/next.config.ts` | Next.js 配置。 |
| `frontend/tailwind.config.ts` | Tailwind CSS 配置，定义颜色、阴影、基础主题。 |
| `frontend/postcss.config.mjs` | PostCSS 配置，用于 Tailwind 编译。 |
| `frontend/tsconfig.json` | TypeScript 配置。 |
| `frontend/next-env.d.ts` | Next.js 自动生成的 TypeScript 类型声明。 |

### frontend/app

| 文件 | 作用 |
|---|---|
| `frontend/app/layout.tsx` | 全局 root layout，提供 `<html>` 和 `<body>`，避免 Next root layout 错误。 |
| `frontend/app/page.tsx` | 根路径 `/`，默认跳转到 `/en` 或展示入口。 |
| `frontend/app/globals.css` | 全局 CSS 和 Tailwind 基础样式。 |
| `frontend/app/[locale]/layout.tsx` | locale 级 layout，处理 `/en`、`/zh` 下的页面结构。 |
| `frontend/app/[locale]/page.tsx` | Landing page，英文和中文入口页。 |
| `frontend/app/[locale]/dashboard/page.tsx` | Dashboard 页面入口，使用 `DashboardClient` 从真实 dashboard API 读取数据。 |
| `frontend/app/[locale]/profile/page.tsx` | Profile 页面入口，挂载真实可保存的 `ProfileClient`。 |
| `frontend/app/[locale]/programs/page.tsx` | Program Database 页面，真实调用 `/api/programs` 并支持筛选。 |
| `frontend/app/[locale]/programs/[id]/page.tsx` | Program Detail 页面，读取单个 program 详情。 |
| `frontend/app/[locale]/matches/page.tsx` | Matches 页面，支持生成真实匹配和添加申请。 |
| `frontend/app/[locale]/documents/page.tsx` | Documents 页面，支持材料状态更新和项目 checklist。 |
| `frontend/app/[locale]/applications/page.tsx` | Applications Kanban 页面，读取真实 applications 并更新状态。 |
| `frontend/app/[locale]/email-tracker/page.tsx` | Email Tracker 页面，按 applicant 读取 mock email 数据。 |
| `frontend/app/[locale]/browser-agent/page.tsx` | Browser Agent 页面，展示 executor selector、任务日志、安全提示。 |
| `frontend/app/[locale]/portal-assistant/page.tsx` | Portal Assistant 页面，展示 pending action、风险等级、批准/拒绝/手动完成和审计反馈。 |
| `frontend/app/[locale]/crawler/page.tsx` | 重定向到 `/program-discovery`。 |
| `frontend/app/[locale]/program-discovery/page.tsx` | Program Discovery 页面入口，用户友好的项目发现器。 |
| `frontend/app/[locale]/crawler-admin/page.tsx` | Crawler Admin 页面入口，开发者爬虫管理后台。 |
| `frontend/app/[locale]/interview-prep/page.tsx` | Interview Prep 页面，当前为 mock 面试准备内容。 |
| `frontend/app/[locale]/settings/page.tsx` | Settings 页面，当前为设置界面原型。 |

### frontend/components/layout

| 文件 | 作用 |
|---|---|
| `AppShell.tsx` | 主应用布局，组合 sidebar、topbar、右侧 copilot panel 和页面内容。 |
| `Sidebar.tsx` | 左侧导航菜单，支持中英文菜单。 |
| `Topbar.tsx` | 顶部栏，包含语言切换等全局入口。 |
| `LanguageSwitcher.tsx` | 中英文切换组件，负责在 `/en` 和 `/zh` 路由间切换。 |
| `CopilotPanel.tsx` | 右侧 AI Copilot 面板，目前主要展示辅助提示。 |

### frontend/components/common

| 文件 | 作用 |
|---|---|
| `ActionResult.tsx` | 显示 API 操作结果、JSON、错误信息，常用于调试真实交互。 |
| `Badge.tsx` | 状态标签组件，支持 brand、success、warning、danger 等 tone。 |
| `Button.tsx` | 通用按钮组件，统一圆角、颜色、disabled 状态。 |
| `Card.tsx` | 通用卡片容器，统一白底、圆角、边框、阴影。 |
| `EmptyState.tsx` | 空状态展示组件。 |

### frontend/components/dashboard

| 文件 | 作用 |
|---|---|
| `DashboardClient.tsx` | Dashboard 真实数据客户端组件，调用 default applicant 和 dashboard API。 |
| `StatCard.tsx` | Dashboard 顶部统计卡片。 |
| `DeadlineList.tsx` | 旧版 deadline 列表组件，部分场景仍可复用。 |
| `TaskList.tsx` | 旧版 task 列表组件，部分场景仍可复用。 |
| `ProgramMatchPreview.tsx` | 旧版匹配预览组件，部分场景仍可复用。 |

### frontend/components/profile

| 文件 | 作用 |
|---|---|
| `ProfileClient.tsx` | 真实 Profile 表单，加载 default applicant、保存到 MySQL、触发分析、显示 GPA 转换。 |
| `GpaConverterCard.tsx` | 显示后端保存后的 `gpa_converted_4` 估算结果。 |
| `ProfileStepForm.tsx` | 旧版静态 profile form，目前保留作为可复用 UI 草稿。 |

### frontend/components/programs

| 文件 | 作用 |
|---|---|
| `ProgramFilters.tsx` | Program Database 筛选器，输出 search、country、field、university、review_status、min_confidence。 |
| `ProgramCard.tsx` | 项目卡片，显示项目字段，并支持真实 Add Application。 |
| `ProgramDetailPanel.tsx` | 项目详情 UI，展示 overview、requirements、deadline、tuition、source、raw snapshot。 |

### frontend/components/matches

| 文件 | 作用 |
|---|---|
| `MatchActionPanel.tsx` | 旧版匹配操作面板，早期用于 JSON 反馈；当前主要逻辑已迁入 matches page。 |

### frontend/components/documents

| 文件 | 作用 |
|---|---|
| `DocumentCard.tsx` | 旧版材料卡片组件，可复用展示单个 document。 |
| `DocumentStatusBadge.tsx` | 材料状态 badge。 |
| `ChecklistPanel.tsx` | 旧版静态 checklist panel，当前真实 checklist 逻辑已在 documents page。 |

### frontend/components/applications

| 文件 | 作用 |
|---|---|
| `ApplicationKanban.tsx` | 旧版静态 Kanban，可复用为 UI 草稿。当前真实 Kanban 在 applications page。 |
| `ApplicationCard.tsx` | 旧版申请卡片组件，可复用展示单个申请项目。 |

### frontend/components/browser-agent

| 文件 | 作用 |
|---|---|
| `BrowserExecutorPanel.tsx` | Browser Agent 核心控制台，选择 Mock/Playwright/OpenCLI，启动任务、下一步、批准、停止、看日志。 |
| `BrowserAgentConsole.tsx` | Browser Agent 三栏操作台 UI，展示 task steps、browser preview、action log。 |
| `ActionLog.tsx` | Browser Agent 动作日志展示组件。 |
| `HumanApprovalCard.tsx` | 人工批准卡片，强调高风险动作需要用户确认。 |

### frontend/components/crawler

| 文件 | 作用 |
|---|---|
| `CrawlerControlPanel.tsx` | 爬虫控制按钮区，调用 crawler API 做 seed、discover、fetch、extract、full pipeline。 |
| `CrawlerRunTable.tsx` | 爬虫运行记录表格。 |
| `ReviewQueuePanel.tsx` | 项目审核队列面板。 |

### frontend/components/discovery

| 文件 | 作用 |
|---|---|
| `RegionUniversitySelector.tsx` | 地区-大学级联选择器，从 discovery API 加载数据。 |
| `FieldSelector.tsx` | 专业方向选择器。 |
| `UrlAnalyzer.tsx` | URL 输入和分析按钮，调用 analyze-url API 校验官方域名。 |
| `ProgressTimeline.tsx` | 6 步执行进度时间线。 |
| `ProgramResultCard.tsx` | 项目结果卡片，仅展示用户可见字段，支持展开高级详情。 |

### frontend/lib

| 文件 | 作用 |
|---|---|
| `api.ts` | 前端 API 客户端，封装 applicant、dashboard、programs、matches、applications、documents、browser-agent、emails 请求。 |
| `types.ts` | 前端 TypeScript 类型，定义 Program、Applicant、ProfileAnalysis、ProgramMatch、ApplicationItem、DocumentItem、DashboardData。 |
| `i18n.ts` | locale 和 dictionary 工具。 |
| `display.ts` | 把数据库英文值映射成中文展示值，例如国家、方向、状态、材料名。 |
| `mock.ts` | 早期 mock 数据。当前页面应优先使用真实 API，mock 只作为历史/开发参考。 |
| `dictionaries/en.ts` | 英文字典。 |
| `dictionaries/zh.ts` | 中文字典。 |

## backend 文件说明

### backend 根配置

| 文件 | 作用 |
|---|---|
| `backend/main.py` | FastAPI 应用入口，注册 CORS 和所有 `/api` router。 |
| `backend/requirements.txt` | 后端 Python 依赖。 |
| `backend/alembic.ini` | Alembic 配置文件。 |

### backend/alembic

| 文件 | 作用 |
|---|---|
| `backend/alembic/env.py` | Alembic migration 运行环境，读取 SQLAlchemy metadata。 |
| `backend/alembic/versions/0001_initial_schema.py` | 初始数据库 migration。 |
| `backend/alembic/versions/0002_documents_recommendations.py` | Documents metadata 列和 AI recommendations 表。 |
| `backend/alembic/versions/0003_agent_portal_actions.py` | Application plans、agent tasks、audit logs、portal sessions 等表。 |
| `backend/alembic/versions/0004_discovery_sources.py` | crawl_sources 新增 region、source_name、official_domain、status 列。 |

### backend/app/core

| 文件 | 作用 |
|---|---|
| `backend/app/core/__init__.py` | core package 标记文件。 |
| `backend/app/core/config.py` | 读取环境变量，包含数据库、CORS、crawler、browser executor 配置。 |
| `backend/app/core/database.py` | SQLAlchemy engine、SessionLocal、Base、get_db。 |
| `backend/app/core/logging.py` | 后端 logging 基础配置。 |

### backend/app/models

| 文件 | 作用 |
|---|---|
| `backend/app/models/__init__.py` | 导出所有 model，方便 router/service import。 |
| `backend/app/models/entities.py` | 当前主要 SQLAlchemy ORM 定义集中在这里。 |
| `backend/app/models/university.py` | re-export University。 |
| `backend/app/models/crawl_source.py` | re-export CrawlSource。 |
| `backend/app/models/raw_page.py` | re-export RawPage。 |
| `backend/app/models/program.py` | re-export Program。 |
| `backend/app/models/program_requirement.py` | re-export ProgramRequirement。 |
| `backend/app/models/program_deadline.py` | re-export ProgramDeadline。 |
| `backend/app/models/program_document.py` | re-export ProgramDocument。 |
| `backend/app/models/extraction_run.py` | re-export ExtractionRun。 |
| `backend/app/models/crawler_run.py` | re-export CrawlerRun。 |
| `backend/app/models/applicant.py` | re-export Applicant。 |
| `backend/app/models/program_match.py` | re-export ProgramMatch。 |
| `backend/app/models/document.py` | re-export Document。 |
| `backend/app/models/application.py` | re-export Application。 |
| `backend/app/models/email_item.py` | re-export EmailItem。 |
| `backend/app/models/browser_task.py` | re-export BrowserTask。 |

备注：目前 model 实体集中在 `entities.py`，其他 model 文件主要是为了保持清晰 import 路径。后续可以把实体定义真正拆分到各自文件。

### backend/app/schemas

| 文件 | 作用 |
|---|---|
| `backend/app/schemas/__init__.py` | schemas package 标记文件。 |
| `backend/app/schemas/applicant.py` | Applicant update/out Pydantic schema。 |
| `backend/app/schemas/application.py` | Application input/output schema。 |
| `backend/app/schemas/document.py` | Document input/output schema。 |
| `backend/app/schemas/program.py` | Program schema。 |
| `backend/app/schemas/university.py` | University schema。 |
| `backend/app/schemas/discovery.py` | Discovery 请求/响应 schema。 |
| `backend/app/schemas/crawler.py` | Crawler 请求/响应 schema。 |
| `backend/app/schemas/email_item.py` | Email item schema。 |
| `backend/app/schemas/browser_task.py` | Browser task schema。 |
| `backend/app/schemas/browser_executor.py` | Browser Agent executor API 请求 schema，例如 start-task、approve、stop。 |

### backend/app/routers

| 文件 | 作用 |
|---|---|
| `backend/app/routers/__init__.py` | routers package 标记文件。 |
| `backend/app/routers/health.py` | `GET /api/health` 健康检查。 |
| `backend/app/routers/universities.py` | universities 查询和创建 API。 |
| `backend/app/routers/programs.py` | programs 查询、详情、更新、review API。 |
| `backend/app/routers/applicants.py` | default applicant、profile 保存、GPA 转换、profile analysis。 |
| `backend/app/routers/dashboard.py` | Dashboard 聚合 API，聚合 applicant、analysis、matches、applications、documents、tasks。 |
| `backend/app/routers/matches.py` | 生成和读取 program matches。 |
| `backend/app/routers/applications.py` | 创建申请、去重、查询申请、更新状态。 |
| `backend/app/routers/documents.py` | 查询/创建/更新材料，生成 program checklist。 |
| `backend/app/routers/emails.py` | 按 applicant 查询 mock email，保留 analyze mock。 |
| `backend/app/routers/browser_agent.py` | Browser Agent executors、OpenCLI status、start-task、run-next-step、approve、stop、logs。 |
| `backend/app/routers/portal_assistant.py` | Portal Assistant API，负责 session、fill plan、pending action approve/reject/execute、audit logs。 |
| `backend/app/routers/discovery.py` | Discovery API，regions/universities/sources/fields/find-programs/analyze-url/results。 |
| `backend/app/routers/crawler.py` | Crawler 控制 API，seed/discover/fetch/extract/full pipeline/runs/raw-pages/extractions。 |
| `backend/app/routers/ai.py` | AI mock API，例如背景分析、SOP outline、面试准备。 |

### backend/app/services/matching

| 文件 | 作用 |
|---|---|
| `backend/app/services/matching/__init__.py` | matching package 标记文件。 |
| `backend/app/services/matching/gpa_converter.py` | GPA 转换规则，支持 4.0、5.0、100 分制。 |
| `backend/app/services/matching/matching_service.py` | 项目匹配规则，按 GPA、field、country、test score、experience 计算分数和类别。 |

### backend/app/services/browser_agent

| 文件 | 作用 |
|---|---|
| `backend/app/services/browser_agent/__init__.py` | browser_agent package 标记文件。 |
| `browser_executor_base.py` | BrowserExecutorBase 抽象类，定义 open、state、click、fill、select、extract、screenshot、wait、close 等方法。 |
| `mock_executor.py` | Mock executor，不依赖真实浏览器，用于 UI 演示和测试。 |
| `playwright_executor.py` | Playwright executor，只操作本地 sample application form，填表并点击 Save Draft，不点击 Submit。 |
| `opencli_command_builder.py` | OpenCLI 命令构建器，只返回 list command，不执行 subprocess，避免 shell 注入。 |
| `opencli_health.py` | 检查 OpenCLI 是否安装，以及 `opencli doctor` 是否通过。 |
| `opencli_executor.py` | OpenCLI executor，通过 subprocess shell=False 调用外部 `opencli`。 |
| `risk_guard.py` | 浏览器动作风险分类，低风险可自动执行，中风险需确认，final submit/payment/captcha/delete/withdraw 等会 blocked。 |
| `browser_agent_service.py` | Browser Agent 任务编排服务，创建任务、读取 applicant/program context、写 logs_json、选择 executor。 |

### backend/app/services/agent_orchestrator

| 文件 | 作用 |
|---|---|
| `audit_log_service.py` | 写入 `audit_logs`，记录系统、AI、用户、browser_agent 的关键动作。 |
| `approval_gate.py` | Human Approval Gate，创建 `pending_actions` 并限制 approve/reject/manual/execute 状态流转。 |
| `action_registry.py` | 一键 Agent 动作类型分组。 |
| `task_planner.py` | 一键申请计划任务规划占位服务。 |
| `application_orchestrator.py` | 后续 ApplicationPlan 总编排入口。 |

### backend/app/services/portal_assistant

| 文件 | 作用 |
|---|---|
| `portal_assistant_service.py` | Portal Assistant 核心服务，创建 portal session、生成 fill plan、执行 action、写 audit log。 |
| `portal_field_mapper.py` | Portal 字段映射占位。 |
| `portal_snapshot_parser.py` | 检测 login/captcha 等页面状态。 |
| `portal_upload_planner.py` | 文档上传类型规划。 |
| `portal_safety_guard.py` | Portal 安全闸门别名，复用 RiskGuard。 |

### backend/app/services/crawler

| 文件 | 作用 |
|---|---|
| `backend/app/services/crawler/__init__.py` | crawler package 标记文件。 |
| `robots_service.py` | 检查 robots.txt 是否允许抓取。 |
| `fetcher_static.py` | requests + BeautifulSoup 静态页面抓取。 |
| `fetcher_playwright.py` | Playwright 动态页面抓取预留。 |
| `page_cleaner.py` | HTML 清洗为 text_content。 |
| `link_discovery.py` | 从页面中发现候选项目 URL。 |
| `program_url_classifier.py` | 判断 URL 是否像硕士项目页面。 |
| `crawl_pipeline.py` | 串联 robots、fetch、clean、discover、save 的 crawler pipeline。 |

### backend/app/services/extraction

| 文件 | 作用 |
|---|---|
| `backend/app/services/extraction/__init__.py` | extraction package 标记文件。 |
| `program_extraction_schema.py` | ProgramExtraction Pydantic schema。 |
| `mock_llm_extractor.py` | 规则/regex 抽取器，MVP 不依赖真实 LLM。 |
| `llm_extractor.py` | 真实 LLM extractor 预留接口。 |
| `extraction_pipeline.py` | 从 raw_page 抽取 structured program，并写 extraction_runs/programs 的 pipeline。 |

### backend/app/services/ai

| 文件 | 作用 |
|---|---|
| `backend/app/services/ai/__init__.py` | ai package 标记文件。 |
| `mock_ai_service.py` | AI mock 服务，用于背景分析、SOP outline、interview prep 的占位能力。 |

### backend/app/scripts

| 文件 | 作用 |
|---|---|
| `backend/app/scripts/__init__.py` | scripts package 标记文件。 |
| `seed_universities.py` | 写入香港、新加坡、英国、澳洲 demo 学校。 |
| `seed_demo_data.py` | 写入 demo applicant、programs、documents、applications、emails。 |
| `seed_crawl_sources.py` | 写入 crawler source URL。 |
| `crawl_programs.py` | 命令行运行 crawler pipeline，支持 dry run。 |
| `extract_programs.py` | 命令行运行 extraction pipeline。 |
| `review_stats.py` | 查看项目抽取/review 状态统计。 |
| `check_opencli.py` | 命令行检查 OpenCLI 安装和 doctor 状态。 |
| `run_playwright_demo.py` | 命令行运行本地 Playwright sample form demo。 |

### backend/app/demo_pages

| 文件 | 作用 |
|---|---|
| `sample_application_form.html` | 本地申请表 demo，用于 PlaywrightExecutor 填写，不会真实提交。 |

### backend/tests

| 文件 | 作用 |
|---|---|
| `backend/tests/conftest.py` | 测试路径配置，让 pytest 能 import backend app。 |
| `test_health.py` | 测试 `/api/health`。 |
| `test_database.py` | 测试数据库连接。 |
| `test_programs_api.py` | 测试 programs API 基本 shape。 |
| `test_gpa_converter.py` | 测试 GPA 4.0、5.0、100 分制转换。 |
| `test_matching_service.py` | 测试 matching service 能生成分数。 |
| `test_browser_agent_mock.py` | 测试 MockExecutor 和 BrowserAgentService mock flow。 |
| `test_opencli_command_builder.py` | 测试 OpenCLI command builder 返回 list 且命令正确。 |
| `test_risk_guard.py` | 测试低风险、高风险、blocked、requires approval 判断。 |
| `test_interaction_flow.py` | 集成测试：Profile 保存、分析、匹配、申请、checklist、dashboard、browser task 全链路。 |
| `test_url_validation_service.py` | Discovery URL 校验测试：官方域名允许、子域名允许、第三方拒绝、login/payment 拒绝。 |
| `test_crawler_engine_router.py` | 多引擎路由测试：native_static 默认、外部引擎降级、配置禁用。 |
| `test_discovery_result_mapper.py` | 结果映射测试：隐藏技术字段、timeline 映射、无 stack trace 暴露。 |
| `test_discovery_service.py` | Discovery 服务测试：analyze_url 拒绝非官网。 |

## docs 文件说明

| 文件 | 作用 |
|---|---|
| `docs/architecture.md` | 架构说明和 Mermaid 架构图。 |
| `docs/frontend-flow.md` | 前端页面流转说明。 |
| `docs/backend-flow.md` | 后端 API 和数据流说明。 |
| `docs/browser-agent-safety.md` | Browser Agent 安全边界。 |
| `docs/local-dev.md` | 本地开发说明。 |
| `docs/roadmap.md` | 后续迭代计划。 |

## tools/opencli 文件说明

| 文件 | 作用 |
|---|---|
| `tools/opencli/README.md` | OpenCLI 在 ApplyPilot 中的集成概览。 |
| `tools/opencli/OPENCLI_INTEGRATION.md` | OpenCLI 定位、安装、doctor、测试命令、安全边界详细说明。 |
| `tools/opencli/examples/browser_state_example.md` | OpenCLI browser state 示例。 |
| `tools/opencli/examples/fill_form_example.md` | OpenCLI fill form 示例。 |

## 核心 API

Applicant：

```text
GET  /api/applicants/default
GET  /api/applicants/{id}
PUT  /api/applicants/{id}
POST /api/applicants/{id}/analyze
```

Dashboard：

```text
GET /api/dashboard/{applicant_id}
```

Programs：

```text
GET  /api/programs
GET  /api/programs/{id}
PUT  /api/programs/{id}
POST /api/programs/{id}/review
```

Matches：

```text
POST /api/matches/generate/{applicant_id}
GET  /api/matches/{applicant_id}
```

Applications：

```text
GET  /api/applications?applicant_id=1
POST /api/applications
PUT  /api/applications/{id}
PUT  /api/applications/{id}/status
```

Documents：

```text
GET  /api/documents?applicant_id=1
POST /api/documents
PUT  /api/documents/{id}
POST /api/documents/checklist/{program_id}
```

Browser Agent：

```text
GET  /api/browser-agent/executors
GET  /api/browser-agent/opencli/status
POST /api/browser-agent/start-task
POST /api/browser-agent/run-next-step
POST /api/browser-agent/approve-action
POST /api/browser-agent/stop-task
GET  /api/browser-agent/logs?task_id=1
```

Discovery：

```text
GET  /api/discovery/regions
GET  /api/discovery/universities?region=Hong Kong
GET  /api/discovery/sources?university_id=1
GET  /api/discovery/fields
GET  /api/discovery/engines
POST /api/discovery/find-programs
POST /api/discovery/analyze-url
GET  /api/discovery/results/{run_id}
```

Crawler：

```text
POST /api/crawler/seed
POST /api/crawler/discover
POST /api/crawler/fetch
POST /api/crawler/extract
POST /api/crawler/run-full-pipeline
GET  /api/crawler/runs
GET  /api/crawler/raw-pages
GET  /api/crawler/extraction-runs
```

AI Mock：

```text
POST /api/ai/background-analysis
POST /api/ai/generate-sop-outline
POST /api/ai/interview-prep
```

## 数据库说明

MySQL 由 `docker-compose.yml` 启动：

```text
database: applypilot
username: applypilot
password: applypilot_dev_password
root password: applypilot_root_password
charset: utf8mb4
collation: utf8mb4_unicode_ci
```

主要表：

- `universities`
- `crawl_sources`
- `raw_pages`
- `programs`
- `program_requirements`
- `program_deadlines`
- `program_documents`
- `extraction_runs`
- `crawler_runs`
- `applicants`
- `program_matches`
- `documents`
- `applications`
- `email_items`
- `browser_tasks`
- `application_plans`
- `agent_tasks`
- `audit_logs`
- `portal_sessions`
- `email_tracking_rules`
- `pending_actions`

长文本字段使用 `LONGTEXT`，例如 raw HTML、raw text snapshot、JSON string。

## Browser Agent 安全边界

当前 MVP 的原则：

- 不保存真实学校账号密码。
- 不自动 final submit。
- 不自动付款。
- 不绕过验证码。
- 不绕过学校官网限制。
- 不登录学校后台。
- 不抓取个人隐私数据。
- 不抓取付费墙内容。
- 所有 Portal Assistant browser action 必须先进入 `pending_actions`，再由 `risk_guard` 分类。
- 低风险动作可以自动执行，但必须写入 `audit_logs`。
- 中风险动作必须用户点击 approve 后才能执行。
- `final submit`、`payment`、`declaration`、`captcha`、`delete`、`withdraw` 等动作直接 blocked，只能用户本人手动完成。
- 所有 Browser Agent 动作写入 `browser_tasks.logs_json`。
- Portal Assistant 动作写入 `audit_logs`。
- 用户可以随时 stop task。

## OpenCLI 集成方式

ApplyPilot 不把 OpenCLI 当主后端，也不把 OpenCLI 源码复制进 `backend/app`。

正确边界：

```text
ApplyPilot Backend
  -> BrowserAgentService
  -> OpenCLIExecutor
  -> subprocess.run(["opencli", ...], shell=False)
  -> 用户本地 OpenCLI / Browser Bridge
```

安装 OpenCLI：

```bash
npm install -g @jackwener/opencli
opencli doctor
```

如果未安装 OpenCLI，项目仍可运行，只会在 Browser Agent 页面显示 unavailable。

## 开发注意事项

- 新页面优先从 `frontend/lib/api.ts` 调后端 API。
- 不要在新业务页面直接使用 `frontend/lib/mock.ts`。
- 所有后端新增表结构必须走 Alembic migration。
- MySQL 不要换成 SQLite/PostgreSQL。
- Browser Agent 新动作必须经过 `risk_guard.py`。
- OpenCLI 命令必须用 list 参数，不允许拼 shell string。
- 涉及真实学校网页的功能必须尊重 robots.txt、限速、验证码和官网规则。

## 已验证命令

最近一次验证通过：

```text
pytest: 65 passed (36 existing + 29 discovery)
pnpm build: passed
seed_crawl_sources: 25 official sources across 4 regions
GET /api/discovery/regions: ["Hong Kong","Singapore","United Kingdom","Australia"]
GET /api/discovery/universities?region=Hong+Kong: 6 universities
POST /api/discovery/analyze-url (HKU): is_official=true
POST /api/discovery/analyze-url (agent): is_official=false
HKU dry-run crawler: discovered candidate links
HKU fetch: saved raw_pages
mock extraction: raw_page -> program/extraction_run
mock recommendation: generated evidence-backed recommendations
GET /api/health: OK
GET /api/dashboard/1: OK
/zh: 200
/zh/program-discovery: 200
/zh/crawler-admin: 200
/zh/crawler: 307 -> /zh/program-discovery
/zh/profile: 200
/zh/dashboard: 200
/zh/browser-agent: 200
```

## 后续建议

优先级从高到低：

1. 引入 TanStack Query，统一 server state、loading、error、invalidateQueries。
2. Profile 增加更完整表单校验和保存 toast。
3. Documents 增加文件上传、版本管理和按 application 关联材料。
4. Matches 增加 portfolio balance、筛选和解释详情。
5. Browser Agent 增加更多分步 action，不只 mock fill first_name。
6. OpenCLI 做真实 logged-in Chrome 端到端试验，但必须继续保留安全边界。
7. Crawler 加人工 review 工作台和抽取质量评分。
8. AI 文书和面试准备接入真实 LLM API，并加成本控制和权限开关。
