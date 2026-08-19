# 已联络历史功能实现文档

## 功能概述

实现了完整的"已联络历史"功能，允许团队成员上传已联络过的KOL名单，系统自动进行去重和时间阈值管理。

## 核心功能

### 1. 已联络历史管理
- ✅ 上传Excel文件批量导入联络历史
- ✅ 单条记录添加
- ✅ 查看历史记录列表
- ✅ 删除指定记录
- ✅ 自动去重（基于频道名和邮箱）

### 2. 时间阈值配置
- ✅ 可配置的时间阈值（默认90天）
- ✅ 小于阈值：直接排除候选人
- ✅ 大于阈值：不排除，但标注"XX天前已联络"

### 3. 候选人过滤
- ✅ 自动检查所有候选人的联络历史
- ✅ 在三个候选表中都显示"联络历史"列
  - 可直接发信（confirmed）
  - 人工审核（pending）
  - 未获邮箱（no_email）

## 技术实现

### 后端 API 端点

#### 1. `/api/contacted-history` (GET)
获取所有已联络历史记录
```json
{
  "total": 5,
  "records": [
    {
      "_row_index": 2,
      "频道名": "TechChannel",
      "邮箱": "tech@example.com",
      "联络日期": "2026-07-15",
      "备注": "已回复"
    }
  ]
}
```

#### 2. `/api/contacted-history` (POST)
添加单条联络历史记录
```json
// Request
{
  "频道名": "NewChannel",
  "email": "new@example.com",
  "联络日期": "2026-08-10",
  "备注": "初次联络"
}

// Response
{
  "status": "success",
  "message": "已添加联络历史记录"
}
```

#### 3. `/api/contacted-history` (DELETE)
删除指定记录
```json
// Request
{
  "row_index": 5
}

// Response
{
  "status": "success",
  "message": "已删除联络历史记录"
}
```

#### 4. `/api/filter-config/contacted-history/upload` (POST)
批量上传Excel文件
```
Content-Type: multipart/form-data
file: VikPea_已联络历史.xlsx
```

#### 5. `/api/filter-config/contact-threshold` (GET/PUT)
获取/更新联络历史时间阈值
```json
// GET Response
{
  "threshold_days": 90
}

// PUT Request
{
  "threshold_days": 60
}
```

### 前端功能

#### 设置页面 ([settings/page.tsx](frontend/app/settings/page.tsx))
新增以下UI组件：

1. **已联络历史上传区域**
   - 文件上传按钮（支持.xlsx/.xls）
   - 显示当前记录总数
   - Excel格式说明

2. **时间阈值配置**
   - 数字输入框（天数）
   - 实时显示当前阈值
   - 更新按钮

3. **历史记录管理面板**
   - 可展开/收起的记录列表
   - 添加新记录表单（频道名、邮箱、日期、备注）
   - 记录表格（可滚动，最高256px）
   - 每条记录都有删除按钮

#### 候选人表格 ([youtube/page.tsx](frontend/app/youtube/page.tsx))
- 已有"联络历史"列（第10列）
- 显示 `_contacted_note` 字段
- 三个候选表（confirmed/pending/no_email）都包含此列

### 数据文件

#### Excel模板文件
路径: `{WORKSPACE_DIR}/VikPea_已联络历史.xlsx`

列结构:
| 频道名 | 邮箱 | 联络日期 | 备注 |
|--------|------|----------|------|
| 示例频道名 | example@example.com | 2024-01-15 | 团队成员A联络，已回复 |

### 核心逻辑

#### 联络历史检查 ([filter_config.py](api/filter_config.py):230-266)
```python
def check_contacted_history(
    channel_name: str,
    email: str,
    threshold_days: int = 90
) -> Tuple[bool, Optional[int], Optional[str]]
```

逻辑流程：
1. 标准化频道名和邮箱（去除空格、统一小写）
2. 在历史记录中查找匹配项（频道名或邮箱）
3. 计算距离今天的天数
4. 返回：
   - `exclude`: 是否排除（< threshold_days）
   - `days_ago`: 距今天数
   - `note`: 备注信息

#### 候选人过滤集成 ([vikpea_bridge.py](api/vikpea_bridge.py):633-645)
在 `get_confirmed_candidates()` / `get_pending_candidates()` / `get_no_email_candidates()` 中：

```python
contacted_exclude, contacted_days, contacted_note = config.check_contacted_history(
    channel_name, email, threshold_days=90
)
if contacted_days is not None:
    if contacted_exclude:
        candidate["_filter_excluded"] = True
        candidate["_filter_warnings"].append(f"❌ {contacted_days}天前已联络")
    else:
        candidate["_filter_warnings"].append(f"⚠️ {contacted_days}天前已联络")
    candidate["_contacted_note"] = f"{contacted_days}天前已联络"
```

## 文件清单

### 新增文件
1. `api/create_contacted_history_template.py` - Excel模板生成脚本
2. `test_contacted_history.py` - 功能测试脚本
3. `CONTACTED_HISTORY_FEATURE.md` - 本文档

### 修改文件

#### 后端
1. `api/app.py`
   - 新增5个API端点
   - 行号: 755-900

2. `api/filter_config.py`
   - 已有联络历史检查功能
   - 行号: 149-184 (加载), 230-266 (检查), 371-450 (上传/删除)

3. `api/vikpea_bridge.py`
   - 已集成联络历史检查
   - 行号: 633-645 (confirmed), 663 (pending), 690 (no_email)

#### 前端
1. `frontend/app/settings/page.tsx`
   - 新增已联络历史管理UI
   - 新增时间阈值配置UI
   - 新增记录列表和添加/删除功能
   - 行号: 24-40 (状态), 157-257 (处理函数), 520-620 (UI)

2. `frontend/lib/api/vikpea.ts`
   - 更新类型定义添加 `contacted_history_count`
   - 行号: 483-493

3. `frontend/app/youtube/page.tsx`
   - 已有"联络历史"列（无需修改）
   - 行号: 765

## 使用流程

### 管理员/团队成员操作流程

1. **准备Excel文件**
   - 下载模板或按格式创建Excel
   - 填写: 频道名、邮箱、联络日期、备注

2. **上传历史记录**
   - 进入"设置"页面
   - 找到"📞 已联络历史"区域
   - 点击上传按钮选择Excel文件
   - 系统自动合并去重

3. **配置时间阈值**
   - 在"联络历史时间阈值"区域
   - 输入天数（如60天）
   - 点击"更新阈值"

4. **查看和管理记录**
   - 点击"查看已联络历史记录"
   - 可添加单条新记录
   - 可删除错误记录

5. **查看过滤效果**
   - 进入"YouTube搜索"页面
   - 点击"候选库"标签
   - 查看"联络历史"列
   - ❌ = 已排除，⚠️ = 警告但未排除

## 测试方法

### 1. 运行自动化测试
```bash
cd /Users/xuzifu/Downloads/VikPea_项目改进版
python3 test_contacted_history.py
```

### 2. 手动测试步骤
1. 启动后端服务
2. 访问前端设置页面
3. 上传测试Excel文件
4. 配置阈值为30天
5. 添加一条测试记录
6. 进入YouTube候选库查看"联络历史"列
7. 删除测试记录

## 注意事项

1. **Excel格式要求**
   - 第一行必须是表头：频道名 | 邮箱 | 联络日期 | 备注
   - 联络日期格式：YYYY-MM-DD（如2026-08-19）
   - 频道名和邮箱至少填写一个

2. **去重逻辑**
   - 同一频道名或邮箱的记录，保留最新的联络日期
   - 上传时自动与现有记录合并

3. **阈值配置**
   - 修改阈值后需要重新加载候选库才能生效
   - 建议设置为30-90天

4. **性能考虑**
   - 历史记录建议控制在10000条以内
   - 大文件上传可能需要几秒钟处理时间

## 未来扩展建议

1. 支持批量编辑记录
2. 导出当前联络历史为Excel
3. 联络历史统计图表
4. 自动提醒即将过期的联络记录
5. 支持按团队成员筛选记录
