# YouTube KOL 关键词拓展 + 视频搜索工具

一个用于HitPaw的YouTube KOL渠道开发工具。输入种子关键词，自动拓展相关关键词，批量搜索YouTube视频，筛选出适合做insert-link或Dedicated合作的候选视频/博主。

## 功能特点

### 1. 关键词拓展（三个来源并行）
- **YouTube自动补全**：无需key，免费获取搜索建议
- **DataForSEO related_keywords**：相关搜索类关键词
- **DataForSEO keyword_ideas**：同类目关联词

### 2. YouTube视频搜索
- 使用YouTube Data API v3
- 配额管理：自动追踪每日配额使用（默认上限9500）
- 断点续跑：配额用完后保存进度，第二天继续
- 双排序策略：按播放量 + 按相关性，合并去重

### 3. 数据筛选与打分
- **VPH计算**：`VPH = 观看数 / ((当前时间 - 发布时间)小时数)`
- 多维度打分：VPH、标题相关性、观看量绝对值
- 频道去重：每个频道只保留得分最高的视频

### 4. 结果输出
- **Excel双表格式**：
  - Sheet 1: 按视频维度（关键词来源、标题、链接、VPH等）
  - Sheet 2: 按频道维度汇总（命中视频数、最高/平均VPH）

## 安装配置

### 1. 安装依赖
```bash
cd 01_请在这个文件夹里操作
pip install -r requirements.txt
```

### 2. 配置.env文件
在`01_请在这个文件夹里操作`目录下创建`.env`文件：

```env
# YouTube Data API v3 密钥（必填）
YOUTUBE_API_KEY=你的YouTube_API密钥

# DataForSEO 账号（选填，不填则只用YouTube自动补全）
DATAFORSEO_LOGIN=你的登录名
DATAFORSEO_PASSWORD=你的密码
```

#### 获取YouTube API Key
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目
3. 启用 YouTube Data API v3
4. 创建凭据（API密钥）
5. 复制密钥到.env文件

#### DataForSEO账号（可选）
- 注册地址：https://dataforseo.com/
- 用于更全面的关键词拓展
- 不配置时仍可使用YouTube自动补全

### 3. 添加.env到.gitignore
```bash
echo ".env" >> .gitignore
```

## 使用方法

### 基础用法
```bash
python main.py --seed "AI video enhancer"
```

### 多个种子关键词
```bash
python main.py --seed "AI video enhancer" "video upscaler" "topaz alternative"
```

### 自定义参数
```bash
python main.py \
  --seed "AI video enhancer" \
  --vph-threshold 50 \
  --max-keywords 100 \
  --output hitpaw_kol_results.xlsx \
  --depth 2
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--seed` | 种子关键词（必填，可传多个） | - |
| `--vph-threshold` | VPH过滤阈值 | 20 |
| `--max-keywords` | 拓展关键词数量上限 | 50 |
| `--output` | 输出文件路径 | results.xlsx |
| `--depth` | DataForSEO拓展深度（1-3） | 1 |
| `--skip-expansion` | 跳过关键词拓展，直接搜索种子词 | False |
| `--resume` | 从断点继续 | False |

### 断点续跑
当配额用完时，程序会自动保存断点：
```bash
# 第二天继续
python main.py --seed "AI video enhancer" --resume
```

## 配额管理

### YouTube API配额
- 默认每日配额：10,000 units
- search.list：100 units/次
- videos.list：1 unit/次
- 工具默认安全上限：9,500 units

### 配额消耗示例
- 搜索50个关键词：约 50 × 101 = 5,050 units
- 搜索100个关键词：约 10,100 units（需分两天）

### 配额不足时
程序会：
1. 明确提示"今日配额已用完"
2. 保存已处理的关键词列表
3. 保存未处理的关键词列表
4. 第二天运行`--resume`继续

## DataForSEO成本预估

程序启动时会显示预估成本：
```
💰 预估DataForSEO成本: $0.0144 (2 tasks)
```

**计费规则**：
- 任务费：$0.012/task
- 结果费：$0.00012/result
- 1个种子词 = 2个tasks（related + ideas）

**成本示例**：
- 1个种子词：约 $0.012 × 2 = $0.024
- 5个种子词：约 $0.024 × 5 = $0.12
- 每个task平均返回50条结果，结果费约 $0.006/task

## 输出文件说明

### Sheet 1: 视频列表
| 列名 | 说明 |
|------|------|
| 关键词来源 | 该视频是通过哪个关键词找到的 |
| 视频标题 | YouTube视频标题 |
| 视频链接 | 完整视频URL |
| 频道名 | 频道名称 |
| 频道链接 | 频道主页URL |
| 观看数 | 视频观看次数 |
| 发布时间 | 视频发布时间 |
| VPH | 每小时观看数（Views Per Hour） |
| 得分 | 综合得分（VPH + 相关性 + 观看量） |

### Sheet 2: 频道汇总
| 列名 | 说明 |
|------|------|
| 频道名 | 频道名称 |
| 频道链接 | 频道主页URL |
| 命中视频数 | 该频道有多少个视频符合条件 |
| 最高VPH | 该频道视频的最高VPH |
| 平均VPH | 该频道视频的平均VPH |

**用途**：频道汇总表可快速判断哪些博主是稳定的高质量合作对象。

## 工作流程

```
种子关键词
  ↓
[关键词拓展] 三个来源并行
  ├─ YouTube自动补全
  ├─ DataForSEO related_keywords
  └─ DataForSEO keyword_ideas
  ↓
[合并去重] 记录每个词的来源
  ↓
[YouTube搜索] 每个关键词搜索视频
  ├─ 按播放量排序
  ├─ 按相关性排序
  └─ 合并去重
  ↓
[数据补全] 拉取详细统计
  ├─ 观看数
  ├─ 发布时间
  └─ 频道信息
  ↓
[筛选打分] 计算VPH并打分
  ├─ VPH >= 阈值
  ├─ 综合打分
  └─ 频道去重
  ↓
[输出] Excel双表格式
  ├─ 按视频维度
  └─ 按频道维度汇总
```

## 常见问题

### Q: YouTube API配额不够用怎么办？
A: 有以下几个方法：
1. 使用`--resume`分多天完成
2. 减少`--max-keywords`数量
3. 使用`--skip-expansion`只搜索种子词
4. 向Google申请配额提升（付费）

### Q: DataForSEO必须配置吗？
A: 不是必须的。不配置时：
- 仍可使用YouTube自动补全拓展关键词
- 拓展能力会下降，但免费
- 适合小规模测试

### Q: VPH阈值应该设置多少？
A: 建议值：
- 初筛：20（较宽松）
- 精选：50（较严格）
- 根据实际数据分布调整

### Q: 如何判断一个频道适合合作？
A: 查看频道汇总表：
- **平均VPH高**：稳定的内容质量
- **命中视频数多**：内容与你的产品相关度高
- **最高VPH**：爆款视频制作能力

### Q: 为什么有些关键词搜索结果为0？
A: 可能原因：
1. 关键词太冷门
2. YouTube API限流
3. 关键词不相关（被自动过滤）

### Q: 断点文件在哪里？
A: 生成的文件：
- `youtube_quota.json`：配额记录
- `search_checkpoint.json`：搜索断点
- 这些文件会在每日重置/完成后自动清理

## 目录结构

```
01_请在这个文件夹里操作/
├── main.py                    # 主程序入口
├── keyword_expansion.py       # 关键词拓展模块
├── video_search.py           # YouTube搜索模块
├── scoring.py                # 筛选打分模块
├── requirements.txt          # Python依赖
├── .env                      # 配置文件（需自行创建）
├── youtube_quota.json        # 配额记录（自动生成）
├── search_checkpoint.json    # 断点文件（自动生成）
└── README.md                 # 本文档
```

## 注意事项

1. **API密钥安全**：
   - .env文件包含敏感信息，不要提交到Git
   - 确保.env已加入.gitignore

2. **配额管理**：
   - 注意每日配额限制
   - 大批量搜索建议分多天完成

3. **网络环境**：
   - 需要能访问YouTube和Google API
   - DataForSEO API需要稳定网络连接

4. **异常处理**：
   - 每个API调用都有重试机制（2次）
   - 网络错误会自动等待后重试

## 开发计划

- [ ] 支持更多关键词来源（Ahrefs, SEMrush API）
- [ ] 添加频道粉丝数筛选
- [ ] 集成邮箱查找功能
- [ ] 生成outreach邮件模板
- [ ] Web界面（Flask/Django）

## 技术栈

- Python 3.7+
- openpyxl（Excel操作）
- urllib（HTTP请求，无需外部依赖）
- YouTube Data API v3
- DataForSEO API（可选）

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License
