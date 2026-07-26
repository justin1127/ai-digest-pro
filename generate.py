#!/usr/bin/env python3
"""
AI决策情报 Pro

Generate a password-protected daily AI digest page.
The digest always selects the top 5 items sorted by score descending.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import escape, unescape
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen
from xml.etree import ElementTree

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover
    ZoneInfo = None


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
SUBSCRIBERS_FILE = PROJECT_DIR / "subscribers.ini"
PUBLIC_BASE_URL = "https://justin1127.github.io/ai-digest-pro"
DEFAULT_LIMIT = 5

FEEDS = [
    {
        "name": "Google News AI",
        "url": "https://news.google.com/rss/search?q=artificial%20intelligence%20OR%20OpenAI%20OR%20Anthropic%20OR%20Gemini%20OR%20AI%20agent%20when:2d&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/ai/feed/",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
    },
]

FALLBACK_ITEMS = [
    {
        "title": "AI政策、开源模型与算力基础设施成为今日主线",
        "source": "Fallback Brief",
        "summary": "今日自动信源暂不可用，建议人工补充最新新闻。系统保留日报结构、评分排序和发布链路。",
        "category": "系统",
        "link": PUBLIC_BASE_URL,
        "score": 60,
        "reason": "自动化可用性保障",
        "impact": "保证日报不断更，但不替代人工精选。",
        "action": "检查网络或在 data/YYYY-MM-DD.json 中补充精选条目。",
    }
]


def shanghai_now() -> datetime:
    if ZoneInfo:
        return datetime.now(ZoneInfo("Asia/Shanghai"))
    return datetime.now()


def get_date(date_arg: str | None = None) -> dict[str, str]:
    if date_arg:
        now = datetime.strptime(date_arg, "%Y-%m-%d")
    else:
        now = shanghai_now()
    return {
        "iso": now.strftime("%Y-%m-%d"),
        "cn": now.strftime("%Y.%m.%d"),
        "weekday": now.strftime("%A"),
    }


def clean_text(value: Any, max_len: int | None = None) -> str:
    text = unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if max_len and len(text) > max_len:
        return text[: max_len - 1].rstrip() + "…"
    return text


def load_valid_passwords() -> dict[str, dict[str, str]]:
    passwords = {"TEST888": {"name": "测试用户", "expiry": "2099-12-31"}}

    if not SUBSCRIBERS_FILE.exists():
        return passwords

    today = shanghai_now().strftime("%Y-%m-%d")
    content = SUBSCRIBERS_FILE.read_text(encoding="utf-8")

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        password, info = line.split("=", 1)
        info_parts = [part.strip() for part in info.split("|")]
        if len(info_parts) >= 4 and info_parts[3] >= today:
            passwords[password.strip()] = {
                "name": info_parts[0],
                "expiry": info_parts[3],
            }

    return passwords


def load_manual_digest(date: dict[str, str]) -> dict[str, Any] | None:
    candidates = [
        DATA_DIR / f"{date['iso']}.json",
        PROJECT_DIR / "daily_items.json",
    ]
    for path in candidates:
        if path.exists():
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
            if isinstance(data, list):
                return {"items": data}
            return data
    return None


def parse_feed_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    except Exception:
        return None


def fetch_feed(feed: dict[str, str], timeout: int = 15) -> list[dict[str, Any]]:
    request = Request(
        feed["url"],
        headers={
            "User-Agent": "Mozilla/5.0 ai-digest-pro/1.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        xml_text = response.read().decode("utf-8", errors="replace")

    root = ElementTree.fromstring(xml_text)
    items: list[dict[str, Any]] = []
    for node in root.findall(".//item")[:30]:
        title = clean_text(node.findtext("title"), 180)
        if not title:
            continue
        summary = clean_text(node.findtext("description"), 260)
        link = clean_text(node.findtext("link"))
        published = node.findtext("pubDate") or node.findtext("published")
        items.append(
            {
                "title": title,
                "summary": summary,
                "link": link,
                "source": feed["name"],
                "published_at": published or "",
            }
        )
    return items


def fetch_candidates() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for feed in FEEDS:
        try:
            candidates.extend(fetch_feed(feed))
        except Exception as exc:
            print(f"[warn] feed failed: {feed['name']} ({exc})")
    return candidates


def infer_category(text: str) -> str:
    lowered = text.lower()
    rules = [
        ("政策", ["policy", "regulation", "law", "lawsuit", "court", "sanction", "government", "copyright"]),
        ("模型", ["model", "gpt", "claude", "gemini", "llama", "kimi", "qwen", "deepseek"]),
        ("算力", ["nvidia", "gpu", "chip", "compute", "datacenter", "data center", "infrastructure"]),
        ("产品", ["agent", "app", "device", "hardware", "siri", "assistant", "api"]),
        ("融资", ["funding", "raises", "valuation", "ipo", "acquires", "series"]),
        ("安全", ["safety", "security", "hack", "risk", "eval", "benchmark"]),
    ]
    for category, keywords in rules:
        if any(keyword in lowered for keyword in keywords):
            return category
    return "动态"


def compute_score(item: dict[str, Any]) -> int:
    if isinstance(item.get("score"), (int, float)):
        return max(0, min(100, int(item["score"])))

    text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('source', '')}".lower()
    score = 50

    source_weights = {
        "techcrunch": 8,
        "verge": 8,
        "business insider": 8,
        "barron": 7,
        "google news": 5,
        "venturebeat": 6,
        "hugging face": 6,
    }
    score += max((weight for key, weight in source_weights.items() if key in text), default=0)

    keyword_weights = {
        "openai": 8,
        "anthropic": 8,
        "google": 7,
        "deepmind": 7,
        "meta": 6,
        "nvidia": 7,
        "microsoft": 6,
        "agent": 7,
        "open-weight": 8,
        "open source": 7,
        "regulation": 8,
        "sanction": 8,
        "lawsuit": 6,
        "copyright": 6,
        "chip": 7,
        "gpu": 7,
        "funding": 5,
        "ipo": 5,
        "safety": 7,
        "security": 7,
        "model": 5,
    }
    score += sum(weight for keyword, weight in keyword_weights.items() if keyword in text)

    published_at = parse_feed_datetime(item.get("published_at"))
    if published_at:
        age_hours = (datetime.now(timezone.utc) - published_at.astimezone(timezone.utc)).total_seconds() / 3600
        if age_hours <= 24:
            score += 10
        elif age_hours <= 48:
            score += 6
        elif age_hours <= 72:
            score += 3

    return max(0, min(99, score))


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    title = clean_text(item.get("title"), 180)
    summary = clean_text(item.get("summary") or item.get("description"), 260)
    source = clean_text(item.get("source"), 80) or "未知来源"
    category = clean_text(item.get("category"), 20) or infer_category(f"{title} {summary} {source}")
    score = compute_score(item)
    return {
        "title": title,
        "source": source,
        "summary": summary or "暂无摘要，建议打开原文查看详情。",
        "category": category,
        "link": clean_text(item.get("link")) or "#",
        "score": score,
        "reason": clean_text(item.get("reason"), 120) or infer_reason(category, score),
        "impact": clean_text(item.get("impact"), 180) or infer_impact(category),
        "action": clean_text(item.get("action"), 180) or infer_action(category),
        "published_at": clean_text(item.get("published_at"), 80),
    }


def infer_reason(category: str, score: int) -> str:
    if score >= 90:
        return f"{category}影响面广，优先级最高"
    if score >= 80:
        return f"{category}相关信号强，值得关注"
    return f"{category}信息有参考价值"


def infer_impact(category: str) -> str:
    mapping = {
        "政策": "可能改变AI产品上线、合规、采购或跨境合作节奏。",
        "模型": "可能影响模型选型、产品能力边界和成本结构。",
        "算力": "可能影响训练/推理成本、供应链和基础设施布局。",
        "产品": "可能带来新的交互入口、增长渠道或应用形态。",
        "融资": "反映资本偏好的变化，可用于判断赛道热度。",
        "安全": "可能影响企业采用、评测、权限和风控设计。",
    }
    return mapping.get(category, "对AI产品、投资或技术判断有参考价值。")


def infer_action(category: str) -> str:
    mapping = {
        "政策": "跟踪监管口径，检查产品合规和客户采购风险。",
        "模型": "评估是否进入模型雷达，补一次成本和能力对比。",
        "算力": "关注供应链、云厂商价格和国产替代机会。",
        "产品": "拆解交互模式，判断是否可迁移到自己的产品。",
        "融资": "观察同赛道公司定位、估值逻辑和商业化路径。",
        "安全": "更新安全评测、权限隔离和异常行为监控清单。",
    }
    return mapping.get(category, "保存为观察项，必要时做深度分析。")


def select_items(raw_items: list[dict[str, Any]], limit: int = DEFAULT_LIMIT) -> list[dict[str, Any]]:
    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []

    for raw in raw_items:
        item = normalize_item(raw)
        key = re.sub(r"\W+", "", item["title"].lower())[:80]
        if not key or key in seen:
            continue
        seen.add(key)
        normalized.append(item)

    normalized.sort(key=lambda item: (-item["score"], item["title"]))
    return normalized[:limit] or [normalize_item(item) for item in FALLBACK_ITEMS]


def category_icon(category: str) -> str:
    return {
        "政策": "⚖️",
        "模型": "🧠",
        "算力": "⚙️",
        "产品": "📱",
        "融资": "💰",
        "安全": "🛡️",
        "系统": "🔧",
    }.get(category, "🌐")


def build_meta_insights(items: list[dict[str, Any]], manual: dict[str, Any] | None = None) -> list[str]:
    if manual and isinstance(manual.get("insights"), list) and manual["insights"]:
        return [clean_text(insight, 220) for insight in manual["insights"][:4]]

    if not items:
        return ["今日暂无足够信号，优先检查自动化数据源。"]

    top = items[0]
    categories = []
    for item in items:
        if item["category"] not in categories:
            categories.append(item["category"])
    return [
        f"今日最高优先级来自「{top['category']}」：{top['title']}，说明AI行业的关键变量仍集中在政策、模型、算力和入口之争。",
        f"5条精选覆盖「{'、'.join(categories[:4])}」等方向，适合用来更新产品路线图、投资观察池和竞品雷达。",
        "建议把每条新闻都转成一个判断：会改变用户入口、成本结构、合规风险，还是商业化机会。",
    ]


def item_html(item: dict[str, Any], rank: int, date: dict[str, str]) -> str:
    link = escape(item["link"], quote=True)
    source_line = f"{escape(item['source'])} · {escape(date['cn'])}"
    if item.get("published_at"):
        source_line = f"{escape(item['source'])} · {escape(item['published_at'])}"

    return f"""
        <article class="news-item">
            <div class="item-topline">
                <span class="rank">#{rank:02d}</span>
                <span class="tag">{category_icon(item['category'])} {escape(item['category'])}</span>
                <span class="score">{item['score']}分</span>
            </div>
            <h3>{escape(item['title'])}</h3>
            <p class="meta">📍 {source_line}</p>
            <p class="summary">{escape(item['summary'])}</p>
            <div class="analysis-grid">
                <div class="grid-row"><span class="label">入选理由</span><span>{escape(item['reason'])}</span></div>
                <div class="grid-row"><span class="label">影响判断</span><span>{escape(item['impact'])}</span></div>
                <div class="grid-row"><span class="label">行动建议</span><span>{escape(item['action'])}</span></div>
            </div>
            <a href="{link}" target="_blank" rel="noopener noreferrer" class="link">阅读原文 →</a>
        </article>
    """


def generate_html(date: dict[str, str], items: list[dict[str, Any]], manual: dict[str, Any] | None = None) -> str:
    valid_passwords = load_valid_passwords()
    passwords_json = json.dumps(valid_passwords, ensure_ascii=False)
    insights = build_meta_insights(items, manual)
    avg_score = round(sum(item["score"] for item in items) / len(items)) if items else 0
    sources_count = len({item["source"] for item in items})
    report_url = f"{PUBLIC_BASE_URL}/{date['iso']}.html"

    insight_html = "\n".join(
        f"""
        <div class="insight-card">
            <span class="insight-index">{idx:02d}</span>
            <p>{escape(insight)}</p>
        </div>
        """
        for idx, insight in enumerate(insights, 1)
    )
    news_html = "\n".join(item_html(item, idx, date) for idx, item in enumerate(items, 1))

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI决策情报 | {date['cn']}</title>
    <meta name="description" content="AI决策情报 Pro：每日5条AI行业高优先级精选，按评分排序。">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        :root {{
            --bg: #0a0a0f;
            --panel: #141418;
            --panel-2: #1c1c22;
            --gold: #f0c674;
            --gold-2: #d4a853;
            --text: #eeeeee;
            --muted: #9a9aa3;
            --line: rgba(240, 198, 116, 0.22);
            --danger: #ff6b6b;
            --ok: #51cf66;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: radial-gradient(circle at top, #1a1a2e 0, var(--bg) 42%);
            color: var(--text);
            line-height: 1.6;
            padding: 20px;
        }}
        a {{ color: inherit; }}
        .container {{ max-width: 860px; margin: 0 auto; }}

        #password-overlay {{
            position: fixed; inset: 0; min-height: 100dvh;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            display: flex; justify-content: center; align-items: center; z-index: 9999;
            padding: 24px;
        }}
        #password-overlay.hidden {{ display: none !important; }}
        .password-box {{
            background: var(--panel); border: 1px solid #333; border-radius: 16px;
            padding: 36px; text-align: center; max-width: 420px; width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        .password-box h2, h1 {{
            background: linear-gradient(90deg, #fff, var(--gold));
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .password-box h2 {{ font-size: 24px; margin-bottom: 10px; }}
        .password-box p {{ color: var(--muted); margin-bottom: 24px; font-size: 14px; }}
        .password-box input {{
            width: 100%; padding: 14px 16px; font-size: 16px;
            background: #0a0a0f; border: 1px solid #333; border-radius: 8px;
            color: #fff; text-align: center; letter-spacing: 2px; margin-bottom: 16px;
        }}
        .password-box input:focus {{ outline: none; border-color: var(--gold); }}
        .password-box button {{
            width: 100%; padding: 14px; font-size: 16px;
            background: linear-gradient(90deg, var(--gold), var(--gold-2));
            color: #000; border: none; border-radius: 8px; cursor: pointer; font-weight: 800;
        }}
        .error-msg {{ color: var(--danger); font-size: 13px; margin-top: 12px; }}
        .success-msg {{ color: var(--ok); font-size: 13px; margin-top: 12px; }}
        .subscribe-info {{
            margin-top: 24px; padding-top: 24px; border-top: 1px solid #333;
            font-size: 13px; color: #666;
        }}
        .subscribe-info a {{ color: var(--gold); text-decoration: none; }}
        .user-info {{
            position: fixed; top: 18px; right: 18px; background: rgba(20,20,24,0.92);
            border: 1px solid #333; border-radius: 8px; padding: 10px 14px;
            font-size: 12px; color: var(--muted); z-index: 100; backdrop-filter: blur(10px);
        }}
        .user-info span {{ color: var(--gold); }}
        header {{
            padding: 30px 0 24px; border-bottom: 1px solid var(--line); margin-bottom: 24px;
            text-align: center;
        }}
        .eyebrow {{
            color: var(--gold); font-size: 11px; font-weight: 900; letter-spacing: 3px;
            margin-bottom: 8px;
        }}
        h1 {{ font-size: clamp(30px, 6vw, 48px); line-height: 1.12; letter-spacing: 0; }}
        .subtitle {{ color: var(--muted); margin-top: 12px; font-size: 14px; }}
        .stats {{
            display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px;
            margin: 24px 0;
        }}
        .stat {{
            background: rgba(255,255,255,0.035); border: 1px solid var(--line);
            border-radius: 8px; padding: 14px; min-height: 74px;
        }}
        .stat-label {{ color: var(--muted); font-size: 12px; }}
        .stat-value {{ font-size: 22px; font-weight: 900; color: #fff; margin-top: 4px; }}
        section {{ margin-bottom: 22px; }}
        .section-title {{
            display: flex; align-items: center; gap: 10px; font-size: 18px;
            font-weight: 900; margin-bottom: 14px;
        }}
        .insight-card {{
            display: grid; grid-template-columns: 46px 1fr; gap: 12px;
            background: rgba(240,198,116,0.08); border: 1px solid var(--line);
            border-radius: 8px; padding: 14px; margin-bottom: 10px;
        }}
        .insight-index {{ color: var(--gold); font-weight: 900; }}
        .insight-card p {{ color: #d8d8df; font-size: 14px; }}
        .news-item {{
            background: linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.02));
            border: 1px solid var(--line); border-left: 4px solid var(--gold);
            border-radius: 10px; padding: 18px; margin-bottom: 16px;
        }}
        .item-topline {{
            display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;
        }}
        .rank {{ color: var(--gold); font-weight: 900; font-size: 12px; }}
        .tag, .score {{
            display: inline-flex; align-items: center; min-height: 24px;
            padding: 3px 9px; border-radius: 999px; font-size: 12px; font-weight: 800;
        }}
        .tag {{ background: rgba(240,198,116,0.14); color: var(--gold); }}
        .score {{ background: var(--gold); color: #000; margin-left: auto; }}
        h3 {{ font-size: 18px; line-height: 1.38; color: #fff; margin-bottom: 8px; }}
        .meta {{ color: var(--muted); font-size: 12px; margin-bottom: 10px; }}
        .summary {{ color: #c9c9d1; font-size: 14px; margin-bottom: 14px; }}
        .analysis-grid {{
            display: grid; gap: 8px; font-size: 13px; background: rgba(0,0,0,0.18);
            border-radius: 8px; padding: 12px; margin-bottom: 14px;
        }}
        .grid-row {{ display: grid; grid-template-columns: 72px 1fr; gap: 10px; }}
        .label {{ color: var(--gold); font-weight: 900; font-size: 12px; }}
        .link {{ color: var(--gold); text-decoration: none; font-size: 13px; font-weight: 800; }}
        .link:hover {{ text-decoration: underline; }}
        footer {{
            text-align: center; padding: 30px 0; color: #666; font-size: 12px;
            border-top: 1px solid #333; margin-top: 30px;
        }}
        @media (max-width: 680px) {{
            body {{ padding: 14px; }}
            .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
            .score {{ margin-left: 0; }}
            .grid-row {{ grid-template-columns: 1fr; gap: 2px; }}
            .user-info {{ position: static; margin: 0 auto 12px; width: fit-content; }}
            .password-box {{ padding: 28px 20px; }}
        }}
    </style>
</head>
<body>
    <div id="password-overlay">
        <div class="password-box">
            <h2>🔐 AI决策情报 Pro</h2>
            <p>输入您的专属密码解锁今日内容</p>
            <input type="text" id="password-input" placeholder="输入密码（如：TEST888）" maxlength="24" autocomplete="one-time-code">
            <button id="unlock-btn" onclick="checkPassword()">解锁访问</button>
            <div id="message"></div>
            <div class="subscribe-info">
                未订阅？<a href="#" onclick="alert('请添加微信：justin1127（备注AI日报）订阅')">点击咨询订阅</a><br>
                <span style="font-size: 11px; color: #555;">月付¥19 / 年付¥169</span>
            </div>
        </div>
    </div>

    <div class="user-info" id="user-info" style="display: none;">
        👤 <span id="user-name">用户</span> | 有效期至 <span id="expiry-date">--</span>
    </div>

    <div class="container" id="content" style="display: none;">
        <header>
            <div class="eyebrow">AI INTELLIGENCE DAILY</div>
            <h1>AI决策情报</h1>
            <p class="subtitle">📅 {date['cn']} · 每日5条高优先级精选 · 按评分排序</p>
        </header>

        <div class="stats">
            <div class="stat"><div class="stat-label">精选</div><div class="stat-value">{len(items)}</div></div>
            <div class="stat"><div class="stat-label">平均分</div><div class="stat-value">{avg_score}</div></div>
            <div class="stat"><div class="stat-label">来源</div><div class="stat-value">{sources_count}</div></div>
            <div class="stat"><div class="stat-label">阅读</div><div class="stat-value">5min</div></div>
        </div>

        <section>
            <div class="section-title">🧠 元洞察 Meta Insights</div>
            {insight_html}
        </section>

        <section>
            <div class="section-title">🌐 今日精选 Top 5</div>
            {news_html}
        </section>

        <footer>
            © 2026 AI决策情报 | 每天早上8:00更新<br>
            订阅咨询微信：justin1127<br>
            <a href="{report_url}" style="color: #777;">{report_url}</a>
        </footer>
    </div>

    <script>
        const VALID_PASSWORDS = {passwords_json};

        window.onload = function() {{
            const savedPassword = localStorage.getItem('ai_digest_password');
            const savedExpiry = localStorage.getItem('ai_digest_expiry');

            if (savedPassword && savedExpiry) {{
                const today = new Date().toISOString().split('T')[0];
                if (savedExpiry >= today && VALID_PASSWORDS[savedPassword]) {{
                    unlockContent(savedPassword, VALID_PASSWORDS[savedPassword]);
                }} else {{
                    localStorage.removeItem('ai_digest_password');
                    localStorage.removeItem('ai_digest_expiry');
                    localStorage.removeItem('ai_digest_user');
                }}
            }}

            document.getElementById('password-input').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') checkPassword();
            }});
        }};

        function checkPassword() {{
            const input = document.getElementById('password-input').value.trim().toUpperCase();
            const message = document.getElementById('message');
            const btn = document.getElementById('unlock-btn');

            if (!input) {{
                message.innerHTML = '<p class="error-msg">请输入密码</p>';
                return;
            }}

            btn.disabled = true;
            btn.textContent = '验证中...';

            setTimeout(() => {{
                const userInfo = VALID_PASSWORDS[input];

                if (userInfo) {{
                    const today = new Date().toISOString().split('T')[0];
                    if (userInfo.expiry >= today) {{
                        message.innerHTML = '<p class="success-msg">✅ 验证成功！正在进入...</p>';
                        localStorage.setItem('ai_digest_password', input);
                        localStorage.setItem('ai_digest_expiry', userInfo.expiry);
                        localStorage.setItem('ai_digest_user', userInfo.name);
                        setTimeout(() => unlockContent(input, userInfo), 350);
                    }} else {{
                        message.innerHTML = '<p class="error-msg">❌ 密码已过期，请联系续费</p>';
                        btn.disabled = false;
                        btn.textContent = '解锁访问';
                    }}
                }} else {{
                    message.innerHTML = '<p class="error-msg">❌ 密码错误，请检查或联系订阅</p>';
                    btn.disabled = false;
                    btn.textContent = '解锁访问';
                }}
            }}, 350);
        }}

        function unlockContent(password, userInfo) {{
            document.getElementById('password-overlay').classList.add('hidden');
            document.getElementById('content').style.display = 'block';
            document.getElementById('user-info').style.display = 'block';
            document.getElementById('user-name').textContent = userInfo.name;
            document.getElementById('expiry-date').textContent = userInfo.expiry;
        }}
    </script>
</body>
</html>"""


def generate_index_redirect(date: dict[str, str]) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=./{date['iso']}.html">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI决策情报 | 跳转中...</title>
    <style>
        body {{ background: #0a0a0f; color: #fff; display: flex; justify-content: center; align-items: center; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; padding: 24px; }}
        .loading {{ text-align: center; max-width: 480px; }}
        h1 {{ background: linear-gradient(90deg,#fff,#f0c674); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
        a {{ color: #f0c674; }}
    </style>
</head>
<body>
    <div class="loading">
        <h1>🤖 AI决策情报</h1>
        <p>正在跳转到 {date['cn']} 日报...</p>
        <p>如果没有跳转，<a href="./{date['iso']}.html">点击这里</a></p>
    </div>
</body>
</html>"""


def maybe_archive_feed(date: dict[str, str], items: list[dict[str, Any]]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / f"{date['iso']}.generated.json"
    path.write_text(
        json.dumps({"date": date["iso"], "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def git_push(date: dict[str, str]) -> bool:
    try:
        subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            check=True,
        )
        if not status.stdout.strip():
            print("✓ 无变更")
            return True
        subprocess.run(["git", "commit", "-m", f"AI决策情报 {date['cn']}"], cwd=PROJECT_DIR, check=True)
        subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True)
        return True
    except Exception as exc:
        print(f"Git推送失败（稍后手动处理）: {exc}")
        return False


def build_digest(date: dict[str, str], fetch: bool, limit: int) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    manual = load_manual_digest(date)
    if manual and manual.get("items"):
        return select_items(manual["items"], limit), manual

    if fetch:
        raw_items = fetch_candidates()
        selected = select_items(raw_items, limit)
        maybe_archive_feed(date, selected)
        return selected, {"items": selected}

    return select_items(FALLBACK_ITEMS, limit), {"items": FALLBACK_ITEMS}


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate AI决策情报 daily report")
    parser.add_argument("--date", help="Report date in YYYY-MM-DD. Defaults to Asia/Shanghai today.")
    parser.add_argument("--fetch", action="store_true", help="Fetch candidates from RSS/Google News when no manual data file exists.")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Number of selected items, default 5.")
    parser.add_argument("--push", action="store_true", help="Commit and push generated files.")
    args = parser.parse_args()

    date = get_date(args.date)
    print("=" * 60)
    print("AI决策情报 Pro")
    print(f"日期: {date['cn']}")
    print("=" * 60)

    items, manual = build_digest(date, args.fetch, args.limit)
    html = generate_html(date, items, manual)

    dated_file = PROJECT_DIR / f"{date['iso']}.html"
    dated_file.write_text(html, encoding="utf-8")
    (PROJECT_DIR / "index.html").write_text(generate_index_redirect(date), encoding="utf-8")

    print(f"✓ 生成: {dated_file.name}")
    print(f"✓ 精选: {len(items)}条，已按评分排序")
    for idx, item in enumerate(items, 1):
        print(f"  {idx}. [{item['score']}] {item['title']} - {item['source']}")
    print(f"🔗 {PUBLIC_BASE_URL}/{date['iso']}.html")

    if args.push:
        git_push(date)

    return 0


if __name__ == "__main__":
    sys.exit(main())
