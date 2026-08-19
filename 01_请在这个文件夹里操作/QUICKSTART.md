# 快速开始指南

## 1. 安装依赖
```bash
cd 01_请在这个文件夹里操作
pip3 install openpyxl
```

## 2. 配置API密钥

复制示例配置文件：
```bash
cp .env.example .env
```

编辑`.env`文件，填入你的YouTube API密钥：
```env
YOUTUBE_API_KEY=你的YouTube_API密钥
```

DataForSEO是可选的，不填也能用。

## 3. 运行测试

```bash
python3 test_modules.py
```

看到"所有测试通过"就可以开始使用了。

## 4. 开始搜索

### 基础用法
```bash
python3 main.py --seed "AI video enhancer"
```

### 推荐用法（多个种子词）
```bash
python3 main.py --seed "AI video enhancer" "video upscaler" "4k upscaling"
```

### 高级用法
```bash
# 提高VPH阈值，只要高质量视频
python3 main.py --seed "AI video enhancer" --vph-threshold 50

# 拓展更多关键词
python3 main.py --seed "AI video enhancer" --max-keywords 100

# 自定义输出文件名
python3 main.py --seed "AI video enhancer" --output hitpaw_results.xlsx
```

## 5. 配额用完了怎么办？

程序会自动保存进度，第二天运行：
```bash
python3 main.py --seed "AI video enhancer" --resume
```

## 6. 结果文件

打开`results.xlsx`，有两个表：
- **视频列表**：所有符合条件的视频
- **频道汇总**：按频道统计，方便找出优质博主

## 常见问题

### Q: 没有YouTube API密钥怎么办？
1. 访问 https://console.cloud.google.com/
2. 创建项目 → 启用YouTube Data API v3
3. 创建凭据（API密钥）
4. 复制到.env文件

### Q: 能不能只搜索种子词，不拓展？
可以，加上`--skip-expansion`：
```bash
python3 main.py --seed "AI video enhancer" --skip-expansion
```

### Q: VPH是什么？
VPH = 观看数 / 发布小时数。用来判断视频增长速度，VPH越高说明越受欢迎。

### Q: 为什么有些关键词搜不到结果？
- 关键词太冷门
- YouTube API限流
- 建议用更宽泛的词，如"video editing"而不是"video editing software for mac 2026"

## 成本说明

### YouTube API（必需）
- 免费配额：每天10,000 units
- 本工具消耗：约100-101 units/关键词
- 能搜索约90-100个关键词/天

### DataForSEO（可选）
- 关键词拓展用，不是必需的
- 成本：约$0.024/种子词
- 不用也能通过YouTube自动补全拓展关键词

## 下一步

查看完整文档：[README.md](README.md)
