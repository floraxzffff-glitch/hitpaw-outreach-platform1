# VikPea 部署指南

## 环境要求

- Python 3.10+
- macOS / Linux / Windows
- 磁盘空间: ~500MB（含虚拟环境）

## 快速部署（macOS/Linux）

### 1. 克隆或下载项目

```bash
cd /path/to/VikPea
```

### 2. 运行初始化脚本

```bash
bash scripts/init_project.sh
```

这个脚本会自动：
- ✓ 检查 Python 版本（3.10+）
- ✓ 创建虚拟环境
- ✓ 安装所有依赖
- ✓ 创建配置目录

### 3. 配置邮箱和 API

编辑 `config/config.xlsx`：
- 填入 Aliyun 企业邮箱的 SMTP/IMAP 信息
- 填入邮箱账号和密码
- 配置产品名、URL 等

编辑 `config/blacklist.xlsx`：
- 添加垃圾邮箱域名
- 添加竞品公司名（可选）

### 4. 启动工作台

```bash
source venv/bin/activate
python -m src.ui.cli_menu
```

或使用快速脚本：

```bash
bash scripts/run_cli.sh
```

## Windows 部署

### 1. 安装 Python 3.10+

从 [python.org](https://www.python.org) 下载并安装

### 2. 打开 PowerShell 或 CMD

```cmd
cd C:\path\to\VikPea
```

### 3. 创建虚拟环境

```cmd
python -m venv venv
venv\Scripts\activate
```

### 4. 安装依赖

```cmd
pip install -r requirements.txt
```

### 5. 配置和启动

```cmd
python -m src.ui.cli_menu
```

## Docker 部署

### 构建镜像

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install -r requirements.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 运行工作台
CMD ["python", "-m", "src.ui.cli_menu"]
```

### 运行容器

```bash
docker build -t vikpea:latest .
docker run -it -v $(pwd)/config:/app/config -v $(pwd)/data:/app/data vikpea:latest
```

## 定时任务部署（Cron）

### macOS/Linux

编辑 crontab：
```bash
crontab -e
```

添加定时任务：
```bash
# 每天 8:00 自动发信
0 8 * * * cd /path/to/VikPea && source venv/bin/activate && python -m src.outreach.sender >> logs/cron.log 2>&1

# 每天 10:00 读取回复
0 10 * * * cd /path/to/VikPea && source venv/bin/activate && python -m src.email_tracking.reply_reader >> logs/cron.log 2>&1

# 每天 18:00 自动跟进
0 18 * * * cd /path/to/VikPea && source venv/bin/activate && python -m src.outreach.followup >> logs/cron.log 2>&1
```

### Windows

使用任务计划程序：
1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器设置为每日
4. 操作：`python -m src.outreach.sender`

## 云服务器部署（示例: Heroku）

### 1. 创建 Procfile

```
web: python -m src.ui.cli_menu
```

### 2. 创建 runtime.txt

```
python-3.10.0
```

### 3. 部署

```bash
heroku login
heroku create vikpea-app
git push heroku main
```

## 配置管理

### 环境变量配置

复制 `.env.example` 为 `.env`：

```bash
cp .env.example .env
```

编辑 `.env`：
```
SMTP_SERVER=smtp.qiye.aliyun.com
SMTP_PORT=465
FROM_EMAIL=hannah@hitpaw.com
PASSWORD=your_password
...
```

代码中加载：
```python
from dotenv import load_dotenv
import os

load_dotenv()
smtp_server = os.getenv('SMTP_SERVER')
```

### Excel 配置文件

两种方式配置：
1. **Excel 文件** - `config/config.xlsx`（推荐，用户友好）
2. **环境变量** - `.env` 文件（适合容器/云服务）

优先级：`命令行参数 > 环境变量 > Excel文件 > 代码默认值`

## 依赖和系统要求

### Python 依赖

```
openpyxl>=3.10.0      # Excel 处理
requests>=2.31.0      # HTTP 请求
beautifulsoup4>=4.12  # HTML 解析
yt-dlp>=2024.1.1      # YouTube 抓取
certifi>=2023.7.22    # SSL 证书
```

### 系统要求

| 项目 | 要求 |
|------|------|
| Python | 3.10+ |
| RAM | 256MB+ |
| 磁盘 | 500MB+（含venv） |
| 网络 | 稳定 HTTPS |

## 故障排查

### 问题: SSL 证书错误

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED]
```

**解决：** 脚本有自动兜底逻辑，会在首次执行时切换到兼容模式

### 问题: SMTP 连接失败

```
smtplib.SMTPAuthenticationError: 535 Authentication failed
```

**解决：**
1. 检查邮箱账号和密码
2. 确保已在邮箱客户端授权
3. 检查防火墙是否阻止 465 端口

### 问题: YouTube API 限速（HTTP 429）

```
urllib.error.HTTPError: HTTP Error 429
```

**解决：** 在 config.xlsx 增加 `YOUTUBE_API_DELAY_SEC`

### 问题: 依赖安装失败

```
ERROR: Could not find a version that satisfies the requirement
```

**解决：**
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

## 升级和维护

### 更新依赖

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### 检查过期配置

```bash
python -m src.inspection.pre_delivery_check
```

### 备份数据

建议每周备份：
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz \
  config/ data/ \
  VikPea_*.xlsx logs/
```

## 性能优化

### 并行处理

如需加速（不建议初期使用）：
```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    results = executor.map(process_channel, channels)
```

### 缓存优化

使用 Redis 缓存（可选）：
```bash
pip install redis
# 或使用 Docker: docker run -d -p 6379:6379 redis
```

### 数据库优化

对于大量数据，考虑迁移到数据库：
```bash
pip install sqlalchemy sqlite3
# 或 PostgreSQL/MySQL
```

## 许可证

MIT License - 详见 LICENSE

## 支持

- 📧 邮件: team@example.com
- 💬 社区: GitHub Issues
- 📖 文档: docs/

---

**最后更新：** 2026-08-13
