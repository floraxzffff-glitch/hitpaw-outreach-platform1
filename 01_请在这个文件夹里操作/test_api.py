#!/usr/bin/env python3
"""测试 VectorEngine API 配置"""

import json
import urllib.request
import ssl

API_KEY = "sk-2kPXDoMCCYy0E80asC2jVkhUgBeT6n0swDLBL2RKpQwlCfTp"
API_BASE = "https://api.vectorengine.ai/v1"

def safe_urlopen(req_or_url, timeout=15):
    """兼容SSL证书问题的请求"""
    try:
        return urllib.request.urlopen(req_or_url, timeout=timeout)
    except ssl.SSLCertVerificationError:
        pass
    except urllib.error.URLError as exc:
        if not isinstance(getattr(exc, "reason", None), ssl.SSLCertVerificationError):
            raise

    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
        return urllib.request.urlopen(req_or_url, timeout=timeout, context=ctx)
    except Exception:
        ctx = ssl._create_unverified_context()
        return urllib.request.urlopen(req_or_url, timeout=timeout, context=ctx)

print("测试 1: DeepSeek API (频道标签)")
print("-" * 50)

deepseek_payload = json.dumps({
    "model": "deepseek-chat",
    "max_tokens": 30,
    "messages": [{"role": "user", "content": "用1-3个中文词描述：科技测评频道。只输出分类词。"}],
}).encode("utf-8")

deepseek_req = urllib.request.Request(
    f"{API_BASE}/chat/completions",
    data=deepseek_payload,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "content-type": "application/json",
    },
    method="POST",
)

try:
    resp = safe_urlopen(deepseek_req, timeout=15)
    body = json.loads(resp.read().decode("utf-8"))
    text = ((body.get("choices") or [{}])[0].get("message", {}).get("content") or "").strip()
    print(f"✅ DeepSeek 标签响应: {text}")
except Exception as e:
    print(f"❌ DeepSeek API 失败: {e}")

print("\n测试 2: Claude API (频道标签)")
print("-" * 50)

claude_payload = json.dumps({
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 100,
    "messages": [{"role": "user", "content": "用1-3个中文词描述：游戏解说频道。只输出分类词。"}],
}).encode("utf-8")

claude_req = urllib.request.Request(
    f"{API_BASE}/messages",
    data=claude_payload,
    headers={
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    method="POST",
)

try:
    resp = safe_urlopen(claude_req, timeout=15)
    body = json.loads(resp.read().decode("utf-8"))
    content = body.get("content", [])
    if content and len(content) > 0:
        text = content[0].get("text", "").strip()
        print(f"✅ Claude 标签响应: {text}")
    else:
        print(f"⚠️ Claude 返回空内容: {body}")
except Exception as e:
    print(f"❌ Claude API 失败: {e}")

print("\n测试 3: DeepSeek API (深度分析)")
print("-" * 50)

analysis_prompt = """分析以下 YouTube 频道信息：

频道名：TestChannel
频道简介：专注AI视频工具测评
最近5个视频标题：
- Topaz Video AI vs HitPaw 对比
- 免费视频增强软件推荐

请按以下格式输出：
内容垂直度评分：[1-10]
频道标签：[2-4个中文词]
是否推过竞品：[是/否]
竞品名称：[产品名或"无"]
建议合作方式：[插链接/Dedicated]"""

analysis_payload = json.dumps({
    "model": "deepseek-chat",
    "max_tokens": 200,
    "temperature": 0.3,
    "messages": [{"role": "user", "content": analysis_prompt}],
}).encode("utf-8")

analysis_req = urllib.request.Request(
    f"{API_BASE}/chat/completions",
    data=analysis_payload,
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "content-type": "application/json",
    },
    method="POST",
)

try:
    resp = safe_urlopen(analysis_req, timeout=15)
    body = json.loads(resp.read().decode("utf-8"))
    text = ((body.get("choices") or [{}])[0].get("message", {}).get("content") or "").strip()
    print(f"✅ DeepSeek 深度分析响应:\n{text}")
except Exception as e:
    print(f"❌ DeepSeek 深度分析失败: {e}")

print("\n" + "=" * 50)
print("测试完成！")
