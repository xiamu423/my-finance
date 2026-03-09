============================================================
  金融非结构化数据处理平台 — 业绩超预期信号挖掘模块
  README（快速上手指南）
  版本：v1.0   日期：2026-03-08
============================================================

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
目录结构（D:\finance）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

D:\finance\
├── backend\               Django 项目主模块（配置/路由）
│   ├── settings.py        全局配置（数据库、DRF、CORS）
│   └── urls.py            全局 URL 路由
├── signal_app\            核心业务应用
│   ├── models.py          数据库模型定义
│   ├── serializers.py     API 序列化器
│   ├── views.py           API 视图（含30天过滤、排序逻辑）
│   ├── urls.py            应用路由
│   └── pagination.py      自定义分页器
├── crawler\               数据采集模块
│   └── fetch_real_data.py 东方财富全量爬取 + NLP评分脚本
├── frontend\              Vue 3 前端单页应用
│   ├── src\
│   │   ├── App.vue        应用根组件（导航栏/布局）
│   │   ├── router.js      前端路由
│   │   ├── api\index.js   Axios API 封装
│   │   └── views\
│   │       ├── SignalList.vue    信号列表看板
│   │       └── SignalDetail.vue 信号详情页
│   └── package.json
├── db.sqlite3             SQLite 数据库文件（当前运行数据）
├── seed.py                初始测试数据种子脚本
└── manage.py              Django 管理命令入口

D:\finance\data\          ← 当前目录（文档与导出数据）
├── README.txt             本文件
├── 产品介绍.txt           产品功能、逻辑、字段说明、应用场景
├── companies.csv          公司基础信息（3663条）
├── financial_texts.csv    业绩公告文本（3663条）
├── signals.csv            量化信号（3663条）
├── valuations.csv         估值快照（3663条）
└── code\                  可运行代码包（关键源文件备份）
    ├── fetch_real_data.py 爬虫+NLP主脚本（最重要）
    ├── process_nlp.py     早期NLP处理脚本（已迭代）
    ├── models.py          数据模型
    ├── serializers.py     序列化器
    ├── views.py           API视图
    ├── pagination.py      分页器
    ├── signal_app_urls.py 应用路由
    ├── backend_urls.py    全局路由
    ├── settings.py        Django配置
    └── seed.py            种子数据脚本


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
快速启动（本地运行）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

【前置要求】
  - Python 3.11+（已安装 django, djangorestframework, django-cors-headers,
    django-filter, requests）
  - Node.js 20+（已安装 npm）

【第一步：启动后端 Django 服务】
  打开命令行，进入 Django 项目根目录（D:\finance 或原 C: 盘工作区）：
    > cd C:\Users\LiJiaYue\.gemini\antigravity\playground\ancient-andromeda
    > python manage.py runserver
  看到 "Starting development server at http://127.0.0.1:8000/" 即为成功。

【第二步：启动前端 Vue 开发服务】
  新开一个命令行窗口，进入前端目录：
    > D:
    > cd finance\frontend
    > npm run dev
  看到 "Local: http://localhost:5173/" 后，用浏览器打开该地址。

【第三步：更新最新数据（手动执行爬取）】
  新开一个命令行窗口，在后端项目根目录运行：
    > cd C:\Users\LiJiaYue\.gemini\antigravity\playground\ancient-andromeda\crawler
    > python fetch_real_data.py
  脚本执行完毕后，刷新浏览器即可看到最新数据。

【第四步：配置每日自动更新（Windows 任务计划程序）】
  1. 开始菜单搜索"任务计划程序"并打开
  2. 点击"创建基本任务" → 命名"金融业绩每日爬取"
  3. 触发器：每天，时间建议 18:30
  4. 操作：启动程序
     - 程序：python
     - 参数：fetch_real_data.py
     - 起始于：C:\Users\LiJiaYue\.gemini\antigravity\playground\ancient-andromeda\crawler
  5. 完成


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
可用 API 端点（后端运行后可直接访问）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  GET  http://localhost:8000/api/signals/?format=json
       获取近30天信号列表（默认按公告日期降序+评分降序）

  GET  http://localhost:8000/api/signals/?strength=strong&format=json
       仅查看强信号

  GET  http://localhost:8000/api/signals/{id}/?format=json
       获取单条信号详情

  GET  http://localhost:8000/api/companies/?format=json
       获取公司列表

  参数：
    page=1          页码（默认第1页）
    page_size=20    每页条数（默认20，最大200）
    strength=       信号强度过滤（strong / medium / weak / negative）


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
已知限制与后续优化方向
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. 部分极端小盘股或新股，如第三方数据源(akshare/同花顺)暂无覆盖"一致预期"
     或"历史同期"时，系统将智能回退至预设行业基准或对其图表模块进行自适应隐藏。
  2. 东方财富 API 不含 SSL 证书验证（verify=False），生产环境部署时
     建议处理证书问题或使用代理。
  3. 当前为 SQLite，如数据量超过百万条建议迁移至 PostgreSQL 或 MySQL。
  4. NLP 评分逻辑目前基于规则（区间差值），可接入大语言模型（LLM）
     进行更精准的语义理解与置信度打分。

============================================================
