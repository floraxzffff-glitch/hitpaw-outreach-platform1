# VikPea YouTube KOL搜索 - AI功能说明

## 已集成的三大AI功能

### ✅ 1. Claude API - 频道标签生成
**状态**: 已测试通过 ✅

**功能**: 根据频道简介和视频标题，自动生成1-3个中文分类词

**配置位置**: 
- API密钥: `ANTHROPIC_API_KEY = "sk-2kPXDoMCCYy0E80asC2jVkhUgBeT6n0swDLBL2RKpQwlCfTp"`
- API地址: `ANTHROPIC_API_BASE = "https://api.vectorengine.ai/v1"`
- 模型: `ANTHROPIC_TAG_MODEL = "claude-3-5-sonnet-20241022"`
- 代码行: 第114-116行

**输出示例**: `科技测评`、`游戏解说`、`手机摄影`

**Excel列**: 第10列 - `频道标签`

---

### ⚠️ 2. DeepSeek API - 深度频道分析
**状态**: 已配置，但遇到速率限制（429错误）

**功能**: 综合分析频道信息，输出：
1. **内容垂直度评分** (1-10分)
2. **频道标签** (2-4个中文词)
3. **是否推过竞品** (是/否 + 竞品名称)
4. **建议合作方式** (插链接 / Dedicated)

**配置位置**:
- API密钥: `DEEPSEEK_API_KEY = "sk-2kPXDoMCCYy0E80asC2jVkhUgBeT6n0swDLBL2RKpQwlCfTp"`
- API地址: `DEEPSEEK_API_BASE = "https://api.vectorengine.ai/v1"`
- 代码行: 第112-113行

**分析数据来源**:
- 频道简介（前400字符）
- 最近5个视频标题
- 最新视频的高赞评论（前10条）

**Excel列**:
- 第11列 - `垂直度` (1-10分)
- 第12列 - `推过竞品` (显示"是(Topaz/Aiarty)"或"否")
- 第13列 - `合作方式` ("插链接"或"Dedicated")

**评分标准**:
- **垂直度**: 10分=专注单一领域，5-7分=内容分散，1-4分=杂乱无章
- **竞品检测**: Topaz Video AI, Aiarty, DemoCreator, HitPaw, AVCLabs, UniFab, VanceAI等
- **合作方式**: 专业测评频道→Dedicated，教程类频道→插链接

**注意**: 目前遇到429错误，可能需要：
1. 等待一段时间后重试（速率限制冷却）
2. 联系VectorEngine确认该API密钥的速率限制配置
3. 或者换用DeepSeek官方API（https://api.deepseek.com）

---

### ✅ 3. 市场评分功能（无需API）
**状态**: 已内置，无需外部API ✅

**功能**: 基于关键词信号和粉丝数，自动评估频道的"小博主市场"匹配度

**评分逻辑**:
- **正向信号** (+分):
  - 移动剪辑工具: capcut(+4), kinemaster(+4), vn editor(+4)
  - 免费/低配需求: free(+2), low end(+4), 2gb ram(+4)
  - 发展中市场语言: hindi(+4), tagalog(+4), bahasa(+4), tamil(+4)
  - 产品相关: review(+3), alternative(+3), topaz(+3)
  - 粉丝数加分:
    * 1K-50K粉: +3分
    * 50K-150K粉: +2分
    * 150K-250K粉: +1分

- **负向信号** (-分):
  - 企业级: enterprise(-4), agency(-3)
  - 大频道: >250K粉 (-3分)

**筛选门槛**: 
- `SMALL_CREATOR_MARKET_MODE = True` 时启用
- `MARKET_SCORE_MIN = 2` (评分≥2才会被收录)

**控制台输出**: `(15.6K粉/S5)` - S5表示市场评分5分

---

## 如何使用

### 运行脚本
```bash
cd "/Users/xuzifu/Downloads/VikPea工作台/VikPea工作台_Mac试用包_2026-08-12/01_请在这个文件夹里操作"
python3 VikPea_YouTube批量搜索.py
```

### 查看输出
脚本会在控制台显示：
```
      ↳ 频道标签：科技测评
      ↳ DeepSeek分析: 垂直度8/10 | 推过竞品:是 | 建议:Dedicated
    ✅ ChannelName       (15.6K粉/S5) → email@example.com [about页]
```

### Excel输出文件
结果保存在 `VikPea_发信名单.xlsx`，包含以下列：
1. 频道名
2. 邮箱
3. 定制主题
4. 定制开头
5. 主页链接
6. 视频链接
7. 备注
8. 类型
9. 来源关键词
10. **频道标签** ← Claude生成
11. **垂直度** ← DeepSeek分析
12. **推过竞品** ← DeepSeek分析
13. **合作方式** ← DeepSeek分析

---

## 故障排查

### DeepSeek 429错误
**症状**: `HTTP Error 429: Too Many Requests`

**原因**: API速率限制

**解决方案**:
1. 等待10-30分钟后重试
2. 检查VectorEngine控制台的速率限制设置
3. 临时禁用DeepSeek分析：将第112行改为 `DEEPSEEK_API_KEY = ""`
4. 或使用DeepSeek官方API：将第113行改为 `DEEPSEEK_API_BASE = ""`（会自动使用 https://api.deepseek.com）

### Claude API错误
如果遇到Claude API问题，检查：
- API密钥是否正确
- API地址是否为 `https://api.vectorengine.ai/v1`（不是 `/v1/messages`）
- 网络连接是否正常

---

## API调用时机

脚本在处理每个频道时会：
1. 先调用 **YouTube Data API** 获取频道信息和视频数据
2. 如果配置了 `ANTHROPIC_API_KEY`，调用 **Claude API** 生成标签
3. 如果配置了 `DEEPSEEK_API_KEY`，调用 **DeepSeek API** 进行深度分析
4. 本地计算 **市场评分**（无API调用）
5. 将所有结果写入Excel

---

## 成本估算

假设处理100个频道：
- **Claude API**: ~100次调用 × 100 tokens = 10,000 tokens
- **DeepSeek API**: ~100次调用 × 200 tokens = 20,000 tokens
- **YouTube Data API**: ~300-500次调用（免费配额内）

具体费用取决于VectorEngine的计费规则。

---

## 更新日志

**2026-08-16**
- ✅ 集成Claude API用于频道标签生成
- ✅ 集成DeepSeek API用于深度频道分析（垂直度/竞品/合作方式）
- ✅ 市场评分功能已内置（无需API）
- ✅ 更新Excel输出列，新增：垂直度、推过竞品、合作方式
- ✅ 修复Claude API路径问题（从 `/v1/messages` 改为 `/messages`）
- ⚠️ DeepSeek API遇到429速率限制，待解决
