#!/bin/bash
# VikPea 项目架构和模块说明

cat << 'EOF'
VikPea 项目结构说明
====================

1. 核心架构
----------

src/
├── config/              配置管理（Excel、环境变量加载）
├── core/                核心库（邮箱验证、黑名单、日志）
├── searchers/           搜索模块
│   ├── youtube_search.py        - YouTube KOL 搜索
│   ├── article_search.py        - 文章站点搜索
│   └── seo_scanner.py           - SEO 渠道扫描
├── email_finder/        邮箱查找
│   └── deep_finder.py           - 深度邮箱查找
├── outreach/            邮件发送
│   ├── sender.py                - 发送开发信
│   └── followup.py              - 自动跟进
├── email_tracking/      邮件追踪
│   ├── reply_reader.py          - 读取回复
│   ├── sent_updater.py          - 补录已发送
│   └── status_recorder.py       - 补录回复状态
├── analysis/            数据分析
│   ├── keyword_review.py        - 关键词复盘
│   └── keyword_clustering.py    - 关键词聚类
├── inspection/          质量检查
│   └── pre_delivery_check.py    - 交付前自检
├── ui/                  用户界面
│   ├── cli_menu.py              - CLI 菜单
│   └── gui_app.py               - GUI 应用（Tkinter）
└── utils/               工具库
    ├── workbook_handler.py      - Excel 处理
    └── logger.py                - 日志记录


2. 模块功能映射
--------------

搜索流程:
  YouTube搜索 → 文章搜索 → SEO扫描 → 去重 → 深度找邮箱

发信流程:
  发信队列 → 发信 → 自动入库追踪 → 自动跟进 → 读回复 → 补录状态

分析流程:
  关键词表 → 复盘分析 → 聚类整理 → 指导下一轮


3. 文件格式
----------

config/ 目录：
  config.xlsx             - 配置文件（SMTP、邮箱、API KEY等）
  blacklist.xlsx          - 黑名单（邮箱、域名、公司名）
  config_template.xlsx    - 配置文件模板

data/ 目录：
  config_template.xlsx    - 黑名单模板

每个脚本自动读取的队列/追踪表：
  VikPea_发信名单.xlsx            - 待发队列（绿=有邮箱，黄=无邮箱）
  VikPea_邮件开发追踪.xlsx        - 发信/回复追踪表（主表）
  VikPea_搜索关键词.xlsx          - YouTube 搜索关键词
  VikPea_文章搜索关键词.xlsx      - 文章搜索关键词
  VikPea_无邮箱候选.xlsx          - 深度查过但未找到邮箱的候选
  VikPea_待确认邮箱.xlsx          - 等待人工确认的邮箱候选
  VikPea_黑名单.xlsx              - 垃圾邮箱/域名/公司名
  VikPea_关键词搜索记录.xlsx      - 搜索表现统计


4. 使用流程
----------

基础工作流:
  1. 交付前自检 → 检查环境、依赖、队列
  2. YouTube搜索 / 文章搜索 → 生成候选名单
  3. 深度找邮箱 → 提取邮箱
  4. 邮箱体检 → 清理垃圾邮箱
  5. 发送开发信 → 批量发信
  6. 读取回复 → 自动更新回复状态
  7. 自动跟进 → 发送跟进信
  8. 关键词复盘 → 分析表现
  9. 关键词聚类 → 优化关键词

可选流程（补录/修复）:
  - 补录已发送邮件 → 倒查遗漏的外联邮件
  - 补录回复状态 → 修复漏报的回复
  - SEO渠道扫描 → 另一种发现高价值机会的方式


5. 配置说明
----------

关键配置项（config/config.xlsx）:

邮箱配置:
  SMTP_SERVER         smtp.qiye.aliyun.com
  SMTP_PORT           465
  FROM_EMAIL          hannah@hitpaw.com
  PASSWORD            (邮箱密码)
  IMAP_SERVER         imap.qiye.aliyun.com
  IMAP_PORT           993

发信策略:
  DAILY_SEND_LIMIT    80          (每天最多发信数)
  DELAY_SEC           8           (邮件间隔秒数)
  FOLLOWUP1_AFTER_DAYS 5          (第1次跟进时间)
  FOLLOWUP2_AFTER_DAYS 7          (第2次跟进时间)

搜索策略:
  YOUTUBE_RESULTS_PER_KEYWORD     35      (每个词取几个视频)
  YOUTUBE_MIN_VIDEO_VIEWS         800     (最少播放数)
  ARTICLE_RESULTS_PER_QUERY       30      (每个词取几条文章)
  ARTICLE_MIN_SITE_SCORE          3       (最少网站评分)

可选 API:
  YOUTUBE_API_KEY                 (YouTube API Key)
  SERPER_API_KEY                  (Serper 搜索 API)
  SERPAPI_KEY                     (SerpAPI Key)
  DATAFORSEO_LOGIN                (DataForSEO 账户)


6. 扩展开发
----------

添加新的搜索来源:
  1. src/searchers/ 下创建 new_source.py
  2. 实现搜索 → 邮箱提取 → 写入队列的逻辑
  3. 在 cli_menu.py 添加菜单项

添加新的数据分析:
  1. src/analysis/ 下创建 new_analysis.py
  2. 从追踪表/队列读取数据、生成分析表
  3. 集成到工作台菜单

集成第三方 API:
  1. 新增配置项到 config.xlsx
  2. 在模块中调用 apply_config() 加载
  3. 添加错误处理和速率限制

EOF
