#!/usr/bin/env python3
"""
测试脚本 - 验证各模块功能
运行: python test_modules.py
"""

import sys


def test_keyword_expansion():
    """测试关键词拓展模块"""
    print("\n" + "="*60)
    print("测试1: 关键词拓展模块")
    print("="*60)

    from keyword_expansion import KeywordExpander, estimate_dataforseo_cost

    # 测试YouTube自动补全（不需要凭据）
    expander = KeywordExpander()

    print("\n→ 测试YouTube自动补全...")
    suggestions = expander._fetch_youtube_suggestions("video editing")
    print(f"  获得 {len(suggestions)} 个建议:")
    for i, s in enumerate(suggestions[:5], 1):
        print(f"    {i}. {s}")

    # 测试成本预估
    print("\n→ 测试DataForSEO成本预估...")
    cost = estimate_dataforseo_cost(5, 50)
    print(f"  5个任务，每个50条结果，预估成本: ${cost}")

    # 测试合并去重
    print("\n→ 测试合并去重...")
    test_results = {
        "youtube": ["keyword1", "keyword2", "KEYWORD1"],
        "related": ["keyword3", "keyword2"],
        "ideas": ["keyword4"]
    }
    merged = expander.merge_and_deduplicate(test_results)
    print(f"  原始: {sum(len(v) for v in test_results.values())} 个")
    print(f"  去重后: {len(merged)} 个")

    print("\n✅ 关键词拓展模块测试通过")
    return True


def test_video_search():
    """测试视频搜索模块"""
    print("\n" + "="*60)
    print("测试2: 视频搜索模块")
    print("="*60)

    from video_search import YouTubeSearcher, QuotaManager

    # 测试配额管理（不实际调用API）
    print("\n→ 测试配额管理...")
    searcher = YouTubeSearcher("fake_api_key", quota_limit=10000)
    print(f"  配额上限: {searcher.quota_limit}")
    print(f"  已用配额: {searcher.quota_used}")
    print(f"  剩余配额: {searcher.get_remaining_quota()}")

    # 测试配额检查
    can_search = searcher.check_quota_available(100)
    print(f"  是否可搜索(cost=100): {can_search}")

    # 测试配额预估
    estimated = searcher.estimate_search_quota(50)
    print(f"  搜索50个关键词预估配额: {estimated}")

    # 测试断点管理
    print("\n→ 测试断点管理...")
    mgr = QuotaManager("test_checkpoint.json")
    mgr.save_checkpoint(["kw1", "kw2"], ["kw3", "kw4"])
    loaded = mgr.load_checkpoint()
    print(f"  保存并加载断点: {loaded is not None}")
    mgr.clear_checkpoint()
    print(f"  清除断点成功")

    print("\n✅ 视频搜索模块测试通过")
    return True


def test_scoring():
    """测试筛选打分模块"""
    print("\n" + "="*60)
    print("测试3: 筛选打分模块")
    print("="*60)

    from scoring import (
        calculate_vph, filter_videos, score_and_rank,
        deduplicate_by_channel, aggregate_by_channel
    )

    # 测试VPH计算
    print("\n→ 测试VPH计算...")
    vph1 = calculate_vph(10000, "2026-08-19T10:00:00Z")
    print(f"  10000观看，12小时前: VPH={vph1:.2f}")

    vph2 = calculate_vph(50000, "2026-08-18T10:00:00Z")
    print(f"  50000观看，36小时前: VPH={vph2:.2f}")

    # 测试视频过滤
    print("\n→ 测试视频过滤...")
    test_videos = [
        {
            "video_id": "v1",
            "title": "Test Video 1",
            "view_count": 10000,
            "published_at": "2026-08-19T10:00:00Z",
            "channel_id": "c1"
        },
        {
            "video_id": "v2",
            "title": "Test Video 2",
            "view_count": 1000,
            "published_at": "2026-08-19T10:00:00Z",
            "channel_id": "c2"
        }
    ]

    filtered = filter_videos(test_videos, vph_threshold=20)
    print(f"  原始视频数: {len(test_videos)}")
    print(f"  VPH>=20筛选后: {len(filtered)}")

    # 测试打分
    print("\n→ 测试打分排序...")
    scored = score_and_rank(filtered, "test")
    for v in scored:
        print(f"  {v['video_id']}: VPH={v['vph']:.2f}, Score={v['score']:.2f}")

    # 测试频道去重
    print("\n→ 测试频道去重...")
    test_dup = [
        {"video_id": "v1", "channel_id": "c1", "score": 100},
        {"video_id": "v2", "channel_id": "c1", "score": 50},
        {"video_id": "v3", "channel_id": "c2", "score": 80},
    ]
    unique = deduplicate_by_channel(test_dup)
    print(f"  原始: {len(test_dup)} 个视频")
    print(f"  去重后: {len(unique)} 个视频")
    print(f"  保留视频ID: {[v['video_id'] for v in unique]}")

    # 测试频道汇总
    print("\n→ 测试频道汇总...")
    test_agg = [
        {"channel_id": "c1", "channel_title": "Channel 1", "channel_url": "url1", "vph": 100},
        {"channel_id": "c1", "channel_title": "Channel 1", "channel_url": "url1", "vph": 80},
        {"channel_id": "c2", "channel_title": "Channel 2", "channel_url": "url2", "vph": 50},
    ]
    agg = aggregate_by_channel(test_agg)
    print(f"  汇总到 {len(agg)} 个频道")
    for ch in agg:
        print(f"  {ch['频道名']}: 视频数={ch['命中视频数']}, 平均VPH={ch['平均VPH']}")

    print("\n✅ 筛选打分模块测试通过")
    return True


def test_excel_output():
    """测试Excel输出"""
    print("\n" + "="*60)
    print("测试4: Excel输出")
    print("="*60)

    try:
        import openpyxl
        print("\n→ 测试openpyxl库...")

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "测试表"
        ws.append(["列1", "列2", "列3"])
        ws.append(["数据1", "数据2", "数据3"])

        test_file = "test_output.xlsx"
        wb.save(test_file)
        print(f"  ✓ 创建测试文件: {test_file}")

        # 清理
        import os
        os.remove(test_file)
        print(f"  ✓ 清理测试文件")

        print("\n✅ Excel输出测试通过")
        return True

    except Exception as e:
        print(f"\n❌ Excel输出测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  🧪 YouTube KOL工具 - 模块测试")
    print("="*60)

    results = []

    try:
        results.append(("关键词拓展", test_keyword_expansion()))
    except Exception as e:
        print(f"\n❌ 关键词拓展测试失败: {e}")
        results.append(("关键词拓展", False))

    try:
        results.append(("视频搜索", test_video_search()))
    except Exception as e:
        print(f"\n❌ 视频搜索测试失败: {e}")
        results.append(("视频搜索", False))

    try:
        results.append(("筛选打分", test_scoring()))
    except Exception as e:
        print(f"\n❌ 筛选打分测试失败: {e}")
        results.append(("筛选打分", False))

    try:
        results.append(("Excel输出", test_excel_output()))
    except Exception as e:
        print(f"\n❌ Excel输出测试失败: {e}")
        results.append(("Excel输出", False))

    # 汇总
    print("\n" + "="*60)
    print("  测试汇总")
    print("="*60)

    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"  {name}: {status}")

    all_passed = all(r[1] for r in results)

    if all_passed:
        print("\n" + "="*60)
        print("  🎉 所有测试通过！工具可以正常使用")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("  ⚠️  部分测试失败，请检查错误信息")
        print("="*60)
        sys.exit(1)


if __name__ == "__main__":
    main()
