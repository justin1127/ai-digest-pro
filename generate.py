#!/usr/bin/env python3
"""Generate the Chinese AI decision intelligence daily briefing.

The public page contains exactly five ranked signals.  Facts are kept separate
from editorial inference so the briefing can be used in business discussions,
product reviews, teaching, and research without blurring evidence and opinion.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
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
MAX_PER_CATEGORY = 2

FEEDS = [
    {
        "name": "谷歌新闻聚合",
        "url": "https://news.google.com/rss/search?q=artificial%20intelligence%20OR%20OpenAI%20OR%20Anthropic%20OR%20Gemini%20OR%20AI%20agent%20when:2d&hl=en-US&gl=US&ceid=US:en",
    },
    {"name": "科技媒体 TechCrunch", "url": "https://techcrunch.com/category/artificial-intelligence/feed/"},
    {"name": "科技媒体 The Verge", "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"},
    {"name": "科技媒体 VentureBeat", "url": "https://venturebeat.com/ai/feed/"},
    {"name": "Hugging Face 博客", "url": "https://huggingface.co/blog/feed.xml"},
]

FALLBACK_ITEMS = [
    {
        "title": "自动信源暂不可用，AI 情报生产链路需要人工复核",
        "source": "系统提示",
        "summary": "系统未获得足够可靠的当日候选信息，已保留日报结构与发布链路。",
        "category": "系统",
        "link": PUBLIC_BASE_URL,
        "score": 60,
        "fact": "自动信源抓取未达到发布阈值。",
        "mechanism": "信息源中断会直接降低情报的时效性与可验证性。",
        "impact": "不应以缺少来源支撑的内容替代当天的决策输入。",
        "action": "由编辑人工补充至少五条可追溯来源后再发布。",
        "watch": "确认网络、RSS 源和模型研判步骤是否正常。",
        "audiences": ["运营负责人", "产品负责人"],
        "confidence": "低",
    }
]

CATEGORY_ICONS = {
    "政策": "政策",
    "模型": "模型",
    "算力": "算力",
    "产品": "产品",
    "融资": "资本",
    "安全": "安全",
    "系统": "系统",
}

CATEGORY_PLAYBOOK = {
    "政策": {
        "mechanism": "政策口径会经由合规要求、采购规则与跨境限制，传导到产品上线和商业合作节奏。",
        "impact": "对企业而言，合规从法务事项变成影响销售、交付和产品范围的经营变量。",
        "action": "本周由业务与法务共同核对适用地区、数据流向、模型提供方和客户准入要求。",
        "watch": "关注正式规则、生效日期、执法案例及重点客户的采购条款变化。",
        "audiences": ["企业管理者", "产品负责人", "研究者"],
    },
    "模型": {
        "mechanism": "模型能力、价格、部署方式与生态工具会共同改变应用的可实现边界和单位经济模型。",
        "impact": "企业需要重新比较能力上限、推理成本、数据控制权和供应商锁定风险。",
        "action": "在一周内补齐目标任务集，用相同数据比较效果、成本、延迟和安全边界。",
        "watch": "关注真实任务评测、价格调整、上下文能力、可用地区和企业协议。",
        "audiences": ["企业管理者", "产品负责人", "研究者"],
    },
    "算力": {
        "mechanism": "芯片供给、云服务价格和工程效率会经由训练与推理成本，影响产品毛利和交付能力。",
        "impact": "算力变化首先影响规模化应用的单位成本，其次影响供应链韧性和研发节奏。",
        "action": "由技术与采购更新算力账本，按峰值需求、区域、供应商和替代方案做压力测试。",
        "watch": "关注交付周期、云端单价、出口限制、能耗和实际吞吐量。",
        "audiences": ["企业管理者", "产品负责人", "研究者"],
    },
    "产品": {
        "mechanism": "新的交互入口、智能体权限和工作流能力会改变用户任务的完成路径与平台控制权。",
        "impact": "机会在于重做高频任务，风险在于权限越界、错误自动化和用户信任受损。",
        "action": "挑选一个高频、可回滚任务做小范围试点，并把人工确认和审计日志设为默认。",
        "watch": "关注真实留存、任务成功率、人工接管率、异常行为和权限范围。",
        "audiences": ["企业管理者", "产品负责人", "教师与研究者"],
    },
    "融资": {
        "mechanism": "融资、并购和估值反映资本对技术路线与商业化速度的预期，并会改变竞争资源。",
        "impact": "它不是需求成立的证明，但可提示人才、客户预算和平台能力会向何处集中。",
        "action": "将该公司放入竞品雷达，核对客户、定价、渠道和单位经济数据，而非只跟踪估值。",
        "watch": "关注后续客户验证、收入质量、并购整合和同赛道公司的跟进动作。",
        "audiences": ["企业管理者", "产品负责人", "研究者"],
    },
    "安全": {
        "mechanism": "安全事故与标准会经由权限控制、模型行为、责任分配和客户信任，影响智能体的可部署范围。",
        "impact": "AI 安全已经从模型评测延伸到生产系统：身份、工具、数据和人工接管缺一不可。",
        "action": "48 小时内完成一次智能体权限盘点：最小权限、敏感操作确认、隔离环境和异常告警。",
        "watch": "关注事故复盘、攻击路径、检测时长、责任划分和行业标准的具体要求。",
        "audiences": ["企业管理者", "产品负责人", "教师与研究者"],
    },
    "系统": {
        "mechanism": "情报链路的稳定性决定后续判断能否建立在可核验的输入上。",
        "impact": "数据质量下降时，错误结论会比信息缺失更有害。",
        "action": "先恢复来源与质量检查，再安排人工编辑补充。",
        "watch": "检查抓取、去重、模型研判和发布四个步骤。",
        "audiences": ["运营负责人", "产品负责人"],
    },
}


def shanghai_now() -> datetime:
    return datetime.now(ZoneInfo("Asia/Shanghai")) if ZoneInfo else datetime.now()


def get_date(date_arg: str | None = None) -> dict[str, str]:
    now = datetime.strptime(date_arg, "%Y-%m-%d") if date_arg else shanghai_now()
    return {"iso": now.strftime("%Y-%m-%d"), "cn": now.strftime("%Y年%m月%d日")}


def clean_text(value: Any, max_len: int | None = None) -> str:
    text = unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if max_len and len(text) > max_len:
        return text[: max_len - 1].rstrip() + "…"
    return text


def has_chinese(value: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", value))


def display_source(source: str) -> str:
    return {
        "Google News AI": "谷歌新闻聚合",
        "TechCrunch AI": "科技媒体 TechCrunch",
        "The Verge AI": "科技媒体 The Verge",
        "VentureBeat AI": "科技媒体 VentureBeat",
        "Hugging Face Blog": "Hugging Face 博客",
    }.get(source, source)


def parse_feed_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed
    except (TypeError, ValueError, IndexError):
        return None


def display_published_at(value: str, date: dict[str, str]) -> str:
    parsed = parse_feed_datetime(value)
    if not parsed:
        return date["cn"]
    if ZoneInfo:
        parsed = parsed.astimezone(ZoneInfo("Asia/Shanghai"))
    return parsed.strftime("%m月%d日 %H:%M")


def load_valid_passwords() -> dict[str, dict[str, str]]:
    passwords = {"TEST888": {"name": "测试用户", "expiry": "2099-12-31"}}
    if not SUBSCRIBERS_FILE.exists():
        return passwords

    today = shanghai_now().strftime("%Y-%m-%d")
    for raw_line in SUBSCRIBERS_FILE.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        password, info = line.split("=", 1)
        parts = [part.strip() for part in info.split("|")]
        if len(parts) >= 4 and parts[3] >= today:
            passwords[password.strip()] = {"name": parts[0], "expiry": parts[3]}
    return passwords


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manual_digest(date: dict[str, str]) -> dict[str, Any] | None:
    for path in (DATA_DIR / f"{date['iso']}.json", PROJECT_DIR / "daily_items.json"):
        if path.exists():
            data = read_json(path)
            return {"items": data} if isinstance(data, list) else data
    return None


def fetch_feed(feed: dict[str, str], timeout: int = 15) -> list[dict[str, Any]]:
    request = Request(
        feed["url"],
        headers={
            "User-Agent": "Mozilla/5.0 ai-digest-pro/2.0",
            "Accept": "application/rss+xml, application/xml, text/xml",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        xml_text = response.read().decode("utf-8", errors="replace")

    root = ElementTree.fromstring(xml_text)
    candidates: list[dict[str, Any]] = []
    for node in root.findall(".//item")[:30]:
        title = clean_text(node.findtext("title"), 200)
        if not title:
            continue
        candidates.append(
            {
                "title": title,
                "summary": clean_text(node.findtext("description"), 500),
                "link": clean_text(node.findtext("link")),
                "source": feed["name"],
                "published_at": node.findtext("pubDate") or node.findtext("published") or "",
            }
        )
    return candidates


def fetch_candidates() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for feed in FEEDS:
        try:
            candidates.extend(fetch_feed(feed))
        except Exception as exc:  # Network failures are handled by the fallback item.
            print(f"[警告] 信源抓取失败：{feed['name']}（{exc}）")
    return candidates


def infer_category(text: str) -> str:
    lowered = text.lower()
    rules = [
        ("政策", ["policy", "regulation", "law", "lawsuit", "court", "sanction", "government", "copyright"]),
        ("安全", ["safety", "security", "hack", "breach", "risk", "eval", "benchmark", "cyber"]),
        ("算力", ["nvidia", "gpu", "chip", "compute", "datacenter", "data center", "infrastructure", "cpu"]),
        ("模型", ["model", "gpt", "claude", "gemini", "llama", "kimi", "qwen", "deepseek"]),
        ("融资", ["funding", "raises", "valuation", "ipo", "acquires", "series"]),
        ("产品", ["agent", "app", "device", "hardware", "siri", "assistant", "api", "platform"]),
    ]
    for category, keywords in rules:
        if any(keyword in lowered for keyword in keywords):
            return category
    return "产品"


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
        "谷歌新闻": 5,
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
        score += 10 if age_hours <= 24 else 6 if age_hours <= 48 else 3 if age_hours <= 72 else 0
    return max(0, min(99, score))


def score_breakdown(item: dict[str, Any], score: int) -> dict[str, int]:
    supplied = item.get("score_breakdown")
    if isinstance(supplied, dict):
        values = {key: int(supplied.get(key, 0)) for key in ("影响范围", "紧迫程度", "可行动性", "可信度")}
        if sum(values.values()) == score:
            return values
    impact = round(score * 0.40)
    urgency = round(score * 0.25)
    actionability = round(score * 0.20)
    return {
        "影响范围": impact,
        "紧迫程度": urgency,
        "可行动性": actionability,
        "可信度": score - impact - urgency - actionability,
    }


def rule_based_title(original_title: str, category: str) -> str:
    entities = []
    for entity in ("OpenAI", "Anthropic", "Google", "Microsoft", "Nvidia", "Meta", "DeepMind", "Hugging Face"):
        if entity.lower() in original_title.lower():
            entities.append(entity)
    subject = "、".join(entities[:3]) or "行业机构"
    return f"{subject}出现新的{CATEGORY_ICONS.get(category, category)}动态"


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    original_title = clean_text(item.get("original_title") or item.get("title"), 220)
    original_summary = clean_text(item.get("original_summary") or item.get("summary") or item.get("description"), 600)
    category = clean_text(item.get("category"), 20) or infer_category(f"{original_title} {original_summary}")
    playbook = CATEGORY_PLAYBOOK.get(category, CATEGORY_PLAYBOOK["产品"])
    supplied_title = clean_text(item.get("title_cn"), 100)
    raw_title = clean_text(item.get("title"), 100)
    title = supplied_title or (raw_title if has_chinese(raw_title) else rule_based_title(original_title, category))
    supplied_summary = clean_text(item.get("summary_cn"), 180)
    raw_summary = clean_text(item.get("summary"), 180)
    summary = supplied_summary or (raw_summary if has_chinese(raw_summary) else "原始报道已进入编辑研判流程，建议结合原文核验具体细节。")
    score = compute_score(item)
    fact = clean_text(item.get("fact"), 220) or summary
    confidence = clean_text(item.get("confidence"), 12) or ("高" if item.get("source") not in {"谷歌新闻聚合", "Google News AI"} else "中")
    return {
        "title": title,
        "original_title": original_title,
        "source": display_source(clean_text(item.get("source"), 80) or "未知来源"),
        "summary": summary,
        "category": category,
        "link": clean_text(item.get("link")) or "#",
        "score": score,
        "score_breakdown": score_breakdown(item, score),
        "reason": clean_text(item.get("reason"), 150) or f"{category}信号同时影响业务判断与产品实践，进入今日优先观察清单。",
        "fact": fact,
        "mechanism": clean_text(item.get("mechanism"), 240) or playbook["mechanism"],
        "impact": clean_text(item.get("impact"), 240) or playbook["impact"],
        "action": clean_text(item.get("action"), 240) or playbook["action"],
        "watch": clean_text(item.get("watch"), 200) or playbook["watch"],
        "audiences": [clean_text(value, 16) for value in item.get("audiences", playbook["audiences"])[:3]],
        "confidence": confidence,
        "published_at": clean_text(item.get("published_at"), 80),
    }


def topic_tokens(item: dict[str, Any]) -> set[str]:
    text = f"{item['original_title']} {item['summary']}".lower()
    return {
        token
        for token in re.findall(r"[a-z][a-z0-9-]{3,}|[\u4e00-\u9fff]{2,}", text)
        if token not in {"news", "with", "from", "that", "this", "about", "after", "have", "into"}
    }


def is_duplicate(candidate: dict[str, Any], selected: list[dict[str, Any]]) -> bool:
    tokens = topic_tokens(candidate)
    if not tokens:
        return False
    for existing in selected:
        other = topic_tokens(existing)
        overlap = len(tokens & other) / max(1, min(len(tokens), len(other)))
        if overlap >= 0.62:
            return True
    return False


def select_items(raw_items: list[dict[str, Any]], limit: int = DEFAULT_LIMIT) -> list[dict[str, Any]]:
    normalized = [normalize_item(item) for item in raw_items]
    normalized.sort(key=lambda item: (-item["score"], item["title"]))
    selected: list[dict[str, Any]] = []
    category_count: Counter[str] = Counter()
    for item in normalized:
        if category_count[item["category"]] >= MAX_PER_CATEGORY or is_duplicate(item, selected):
            continue
        selected.append(item)
        category_count[item["category"]] += 1
        if len(selected) == limit:
            return selected
    for item in normalized:
        if item in selected or is_duplicate(item, selected):
            continue
        selected.append(item)
        if len(selected) == limit:
            return selected
    return selected or [normalize_item(item) for item in FALLBACK_ITEMS]


def parse_editorial_json(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE)
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("编辑研判必须是 JSON 对象")
    return data


def apply_editorial(items: list[dict[str, Any]], editorial: dict[str, Any]) -> list[dict[str, Any]]:
    entries = editorial.get("items", [])
    by_rank = {int(entry["rank"]): entry for entry in entries if isinstance(entry, dict) and str(entry.get("rank", "")).isdigit()}
    merged: list[dict[str, Any]] = []
    for rank, item in enumerate(items, 1):
        entry = by_rank.get(rank, {})
        enriched = {**item}
        for key in ("title", "summary", "fact", "mechanism", "impact", "action", "watch", "reason", "confidence"):
            if entry.get(key):
                enriched[key] = clean_text(entry[key], 240 if key != "title" else 100)
        if isinstance(entry.get("audiences"), list) and entry["audiences"]:
            enriched["audiences"] = [clean_text(value, 16) for value in entry["audiences"][:3]]
        if entry.get("title"):
            enriched["title_cn"] = enriched["title"]
        if entry.get("summary"):
            enriched["summary_cn"] = enriched["summary"]
        merged.append(normalize_item(enriched))
    return merged


def fallback_daily_brief(items: list[dict[str, Any]]) -> dict[str, str]:
    categories = "、".join(dict.fromkeys(item["category"] for item in items))
    top = items[0]
    return {
        "headline": f"今日最重要的变量是「{top['category']}」：AI 应用的竞争正在从单点能力转向可控落地。",
        "takeaway": f"五条信号覆盖{categories}。对决策者而言，先判断它改变的是能力、成本、治理还是市场格局，再决定是否投入资源。",
        "action": "本周选出一项与自身业务最相关的信号，指定责任人、验证指标和决策截止日。",
        "watch": "持续区分已证实事实与后续推断；原始报道是事实层，日报研判是决策辅助层。",
    }


def build_daily_brief(items: list[dict[str, Any]], manual: dict[str, Any] | None, editorial: dict[str, Any] | None) -> dict[str, str]:
    source = (editorial or {}).get("daily_brief") or (manual or {}).get("daily_brief") or {}
    fallback = fallback_daily_brief(items)
    return {key: clean_text(source.get(key), 260) or value for key, value in fallback.items()}


def action_level(score: int) -> str:
    if score >= 92:
        return "本周优先处理"
    if score >= 80:
        return "纳入本周评估"
    return "持续观察"


def item_html(item: dict[str, Any], rank: int, date: dict[str, str]) -> str:
    breakdown = " · ".join(f"{escape(label)} {value}" for label, value in item["score_breakdown"].items())
    roles = "".join(f'<span class="role">{escape(role)}</span>' for role in item["audiences"])
    return f"""
        <article class="news-item">
            <div class="item-topline">
                <span class="rank">优先级 {rank:02d}</span>
                <span class="tag">{escape(CATEGORY_ICONS.get(item['category'], item['category']))}</span>
                <span class="action-level">{action_level(item['score'])}</span>
                <span class="score" aria-label="综合优先级评分">{item['score']}分</span>
            </div>
            <h2>{escape(item['title'])}</h2>
            <p class="source">来源：{escape(item['source'])} · 发布于 {escape(display_published_at(item['published_at'], date))} · 事实把握度：{escape(item['confidence'])}</p>
            <p class="why"><strong>为什么入选：</strong>{escape(item['reason'])}</p>
            <div class="fact-row">
                <div class="row-label">已知事实</div>
                <p>{escape(item['fact'])}</p>
            </div>
            <div class="analysis-columns">
                <div>
                    <div class="row-label">影响机制</div>
                    <p>{escape(item['mechanism'])}</p>
                </div>
                <div>
                    <div class="row-label">决策影响</div>
                    <p>{escape(item['impact'])}</p>
                </div>
            </div>
            <div class="analysis-columns action-columns">
                <div>
                    <div class="row-label">建议行动</div>
                    <p>{escape(item['action'])}</p>
                </div>
                <div>
                    <div class="row-label">下一步验证</div>
                    <p>{escape(item['watch'])}</p>
                </div>
            </div>
            <div class="item-foot">
                <span class="score-detail">评分构成：{breakdown}</span>
                <span class="roles">适用：{roles}</span>
                <a href="{escape(item['link'], quote=True)}" target="_blank" rel="noopener noreferrer" class="link">查看原始报道</a>
            </div>
        </article>
    """


def generate_html(
    date: dict[str, str],
    items: list[dict[str, Any]],
    manual: dict[str, Any] | None = None,
    editorial: dict[str, Any] | None = None,
) -> str:
    valid_passwords = load_valid_passwords()
    passwords_json = json.dumps(valid_passwords, ensure_ascii=False)
    brief = build_daily_brief(items, manual, editorial)
    avg_score = round(sum(item["score"] for item in items) / len(items)) if items else 0
    source_count = len({item["source"] for item in items})
    report_url = f"{PUBLIC_BASE_URL}/{date['iso']}.html"
    news_html = "\n".join(item_html(item, index, date) for index, item in enumerate(items, 1))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 决策情报｜{date['cn']}</title>
    <meta name="description" content="面向企业管理者、产品负责人、教师与研究者的中文 AI 应用决策日报。每日 5 条，按综合优先级排序。">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        :root {{
            --bg: #11151a; --surface: #191f25; --surface-2: #202831; --ink: #f4f6f7;
            --muted: #aeb8c1; --line: #34414c; --teal: #57d1bd; --amber: #f1b863;
            --danger: #ff8585; --ok: #70d69b;
        }}
        body {{ background: var(--bg); color: var(--ink); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif; line-height: 1.65; padding: 24px; }}
        a {{ color: inherit; }}
        .container {{ max-width: 1080px; margin: 0 auto; }}
        #password-overlay {{ position: fixed; inset: 0; min-height: 100dvh; background: #11151a; display: flex; justify-content: center; align-items: center; z-index: 9999; padding: 24px; }}
        #password-overlay.hidden {{ display: none !important; }}
        .password-box {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 36px; text-align: center; max-width: 420px; width: 100%; box-shadow: 0 20px 60px rgba(0, 0, 0, .32); }}
        .password-box h2 {{ font-size: 24px; margin-bottom: 10px; }}
        .password-box p {{ color: var(--muted); margin-bottom: 22px; font-size: 14px; }}
        .password-box input {{ width: 100%; padding: 13px 14px; font-size: 16px; background: #0e1216; border: 1px solid var(--line); border-radius: 6px; color: var(--ink); text-align: center; letter-spacing: 1px; margin-bottom: 14px; }}
        .password-box input:focus {{ outline: 2px solid var(--teal); outline-offset: 2px; }}
        .password-box button {{ width: 100%; padding: 13px; font-size: 15px; background: var(--teal); color: #071311; border: 0; border-radius: 6px; cursor: pointer; font-weight: 800; }}
        .password-box button:disabled {{ opacity: .65; cursor: wait; }}
        .error-msg {{ color: var(--danger); font-size: 13px; margin-top: 12px; }}
        .success-msg {{ color: var(--ok); font-size: 13px; margin-top: 12px; }}
        .subscribe-info {{ margin-top: 22px; padding-top: 20px; border-top: 1px solid var(--line); font-size: 13px; color: var(--muted); }}
        .subscribe-info a {{ color: var(--teal); text-decoration: none; }}
        .user-info {{ position: fixed; top: 16px; right: 16px; background: rgba(25, 31, 37, .94); border: 1px solid var(--line); border-radius: 6px; padding: 8px 11px; font-size: 12px; color: var(--muted); z-index: 100; }}
        .user-info span {{ color: var(--teal); }}
        header {{ padding: 32px 0 26px; border-bottom: 1px solid var(--line); }}
        .eyebrow, .section-kicker {{ color: var(--teal); font-size: 12px; font-weight: 800; letter-spacing: 1px; }}
        .eyebrow {{ margin-bottom: 8px; }}
        h1 {{ font-size: clamp(30px, 5vw, 46px); line-height: 1.18; letter-spacing: 0; }}
        .subtitle {{ color: var(--muted); margin-top: 11px; font-size: 15px; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); border-bottom: 1px solid var(--line); }}
        .stat {{ padding: 17px 16px; border-right: 1px solid var(--line); }}
        .stat:last-child {{ border-right: 0; }}
        .stat-label {{ color: var(--muted); font-size: 12px; }}
        .stat-value {{ color: var(--ink); font-size: 22px; font-weight: 850; margin-top: 2px; }}
        section {{ margin-top: 30px; }}
        .section-heading {{ display: flex; align-items: baseline; justify-content: space-between; gap: 12px; margin-bottom: 14px; }}
        .section-heading h2 {{ font-size: 21px; line-height: 1.25; }}
        .section-note {{ color: var(--muted); font-size: 12px; text-align: right; }}
        .brief {{ border-top: 3px solid var(--teal); border-bottom: 1px solid var(--line); padding: 22px 0; }}
        .brief h2 {{ font-size: 23px; line-height: 1.35; margin: 6px 0 18px; max-width: 850px; }}
        .brief-grid {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }}
        .brief-grid > div {{ border-top: 1px solid var(--line); padding-top: 10px; }}
        .brief-label, .row-label {{ color: var(--amber); font-size: 12px; font-weight: 850; }}
        .brief-grid p {{ color: #d9e0e5; margin-top: 5px; font-size: 14px; }}
        .method {{ background: #151b20; border-left: 3px solid var(--amber); padding: 16px 18px; }}
        .method p {{ color: #d4dde3; font-size: 14px; }}
        .method strong {{ color: var(--ink); }}
        .news-item {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 22px; margin-bottom: 16px; }}
        .item-topline {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 12px; }}
        .rank {{ color: var(--teal); font-size: 12px; font-weight: 900; }}
        .tag, .action-level, .score, .role {{ display: inline-flex; align-items: center; min-height: 24px; font-size: 12px; font-weight: 800; }}
        .tag {{ color: var(--teal); border: 1px solid rgba(87, 209, 189, .4); border-radius: 999px; padding: 2px 8px; }}
        .action-level {{ color: var(--amber); }}
        .score {{ background: var(--amber); color: #211300; border-radius: 4px; padding: 2px 8px; margin-left: auto; }}
        .news-item h2 {{ font-size: clamp(19px, 2.4vw, 25px); line-height: 1.35; letter-spacing: 0; max-width: 900px; }}
        .source {{ color: var(--muted); font-size: 12px; margin-top: 8px; }}
        .why {{ color: #dce4e8; font-size: 14px; margin: 16px 0; }}
        .why strong {{ color: var(--teal); }}
        .fact-row {{ border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); padding: 13px 0; }}
        .fact-row p, .analysis-columns p {{ color: #dce4e8; font-size: 14px; margin-top: 4px; }}
        .analysis-columns {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 24px; padding: 14px 0; border-bottom: 1px solid var(--line); }}
        .action-columns .row-label {{ color: var(--teal); }}
        .item-foot {{ display: flex; align-items: center; gap: 10px 16px; flex-wrap: wrap; padding-top: 14px; }}
        .score-detail {{ color: var(--muted); font-size: 12px; }}
        .roles {{ display: inline-flex; align-items: center; gap: 5px; color: var(--muted); font-size: 12px; flex-wrap: wrap; }}
        .role {{ background: var(--surface-2); color: #d8e2e8; border-radius: 3px; padding: 2px 6px; font-size: 11px; }}
        .link {{ margin-left: auto; color: var(--teal); font-size: 13px; font-weight: 800; text-decoration: none; white-space: nowrap; }}
        .link:hover {{ text-decoration: underline; }}
        footer {{ color: var(--muted); border-top: 1px solid var(--line); padding: 28px 0 10px; margin-top: 36px; text-align: center; font-size: 12px; }}
        footer a {{ color: var(--teal); }}
        @media (max-width: 720px) {{
            body {{ padding: 14px; }}
            .stats {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
            .stat:nth-child(2) {{ border-right: 0; }}
            .stat:nth-child(-n+2) {{ border-bottom: 1px solid var(--line); }}
            .brief-grid, .analysis-columns {{ grid-template-columns: 1fr; gap: 14px; }}
            .user-info {{ position: static; width: fit-content; margin: 0 auto 10px; }}
            .password-box {{ padding: 28px 20px; }}
            .news-item {{ padding: 17px; }}
            .score {{ margin-left: 0; }}
            .link {{ margin-left: 0; }}
            .section-heading {{ align-items: flex-start; flex-direction: column; }}
            .section-note {{ text-align: left; }}
        }}
    </style>
</head>
<body>
    <div id="password-overlay">
        <div class="password-box">
            <h2>AI 决策情报</h2>
            <p>输入专属密码，查看今日中文决策日报</p>
            <input type="text" id="password-input" placeholder="输入密码" maxlength="24" autocomplete="one-time-code">
            <button id="unlock-btn" onclick="checkPassword()">解锁访问</button>
            <div id="message"></div>
            <div class="subscribe-info">未订阅？<a href="#" onclick="alert('请添加微信：justin1127（备注 AI 日报）订阅')">咨询订阅</a><br><span>月付 19 元 / 年付 169 元</span></div>
        </div>
    </div>
    <div class="user-info" id="user-info" style="display: none;">订阅用户：<span id="user-name">用户</span> · 有效期至 <span id="expiry-date">--</span></div>
    <main class="container" id="content" style="display: none;">
        <header>
            <div class="eyebrow">AI 应用决策日报</div>
            <h1>AI 决策情报</h1>
            <p class="subtitle">{date['cn']} · 面向企业管理者、产品负责人、教师与研究者 · 每日五条高优先级信号</p>
        </header>
        <div class="stats" aria-label="今日日报概览">
            <div class="stat"><div class="stat-label">精选信号</div><div class="stat-value">{len(items)} 条</div></div>
            <div class="stat"><div class="stat-label">平均优先级</div><div class="stat-value">{avg_score} 分</div></div>
            <div class="stat"><div class="stat-label">独立来源</div><div class="stat-value">{source_count} 个</div></div>
            <div class="stat"><div class="stat-label">建议阅读</div><div class="stat-value">8 分钟</div></div>
        </div>
        <section class="brief" aria-labelledby="daily-brief-title">
            <div class="section-kicker">先给结论</div>
            <h2 id="daily-brief-title">{escape(brief['headline'])}</h2>
            <div class="brief-grid">
                <div><div class="brief-label">这意味着什么</div><p>{escape(brief['takeaway'])}</p></div>
                <div><div class="brief-label">本周建议</div><p>{escape(brief['action'])}</p></div>
                <div><div class="brief-label">保持验证</div><p>{escape(brief['watch'])}</p></div>
            </div>
        </section>
        <section class="method" aria-label="研判方法说明">
            <p><strong>如何阅读：</strong>评分由影响范围、紧迫程度、可行动性与来源可信度组成。每条内容严格区分<strong>已知事实</strong>与<strong>决策研判</strong>，并用“技术能力 → 成本结构 → 组织治理 → 市场格局”的四层框架判断影响。</p>
        </section>
        <section aria-labelledby="signals-title">
            <div class="section-heading"><h2 id="signals-title">今日五条决策信号</h2><p class="section-note">按综合优先级降序排列</p></div>
            {news_html}
        </section>
        <footer>
            AI 决策情报 · 每日自动生成并保留可追溯原始报道<br>
            本页研判用于辅助决策，不替代事实核验、专业意见或组织内部评审。<br>
            <a href="{report_url}">{report_url}</a>
        </footer>
    </main>
    <script>
        const VALID_PASSWORDS = {passwords_json};
        window.onload = function() {{
            const savedPassword = localStorage.getItem('ai_digest_password');
            const savedExpiry = localStorage.getItem('ai_digest_expiry');
            if (savedPassword && savedExpiry) {{
                const today = new Date().toISOString().split('T')[0];
                if (savedExpiry >= today && VALID_PASSWORDS[savedPassword]) unlockContent(savedPassword, VALID_PASSWORDS[savedPassword]);
                else {{ localStorage.removeItem('ai_digest_password'); localStorage.removeItem('ai_digest_expiry'); localStorage.removeItem('ai_digest_user'); }}
            }}
            document.getElementById('password-input').addEventListener('keypress', function(event) {{ if (event.key === 'Enter') checkPassword(); }});
        }};
        function checkPassword() {{
            const input = document.getElementById('password-input').value.trim().toUpperCase();
            const message = document.getElementById('message');
            const button = document.getElementById('unlock-btn');
            if (!input) {{ message.innerHTML = '<p class="error-msg">请输入密码</p>'; return; }}
            button.disabled = true; button.textContent = '验证中…';
            setTimeout(() => {{
                const userInfo = VALID_PASSWORDS[input];
                const today = new Date().toISOString().split('T')[0];
                if (userInfo && userInfo.expiry >= today) {{
                    message.innerHTML = '<p class="success-msg">验证成功，正在进入…</p>';
                    localStorage.setItem('ai_digest_password', input); localStorage.setItem('ai_digest_expiry', userInfo.expiry); localStorage.setItem('ai_digest_user', userInfo.name);
                    setTimeout(() => unlockContent(input, userInfo), 250);
                }} else {{ message.innerHTML = `<p class="error-msg">${{userInfo ? '密码已过期，请联系续费' : '密码错误，请检查或联系订阅'}}</p>`; button.disabled = false; button.textContent = '解锁访问'; }}
            }}, 250);
        }}
        function unlockContent(password, userInfo) {{
            document.getElementById('password-overlay').classList.add('hidden'); document.getElementById('content').style.display = 'block'; document.getElementById('user-info').style.display = 'block';
            document.getElementById('user-name').textContent = userInfo.name; document.getElementById('expiry-date').textContent = userInfo.expiry;
        }}
    </script>
</body>
</html>"""


def generate_index_redirect(date: dict[str, str]) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0; url=./{date['iso']}.html"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>AI 决策情报｜跳转中</title>
<style>body{{background:#11151a;color:#f4f6f7;display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;padding:24px}}.loading{{text-align:center;max-width:480px}}a{{color:#57d1bd}}</style></head>
<body><div class="loading"><h1>AI 决策情报</h1><p>正在跳转到 {date['cn']} 日报…</p><p>如果没有跳转，<a href="./{date['iso']}.html">点击查看</a></p></div></body></html>"""


def archive_generated(date: dict[str, str], items: list[dict[str, Any]], brief: dict[str, str]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / f"{date['iso']}.generated.json").write_text(
        json.dumps({"date": date["iso"], "daily_brief": brief, "items": items}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def git_push(date: dict[str, str]) -> bool:
    try:
        subprocess.run(["git", "add", "."], cwd=PROJECT_DIR, check=True)
        status = subprocess.run(["git", "status", "--porcelain"], cwd=PROJECT_DIR, capture_output=True, text=True, check=True)
        if not status.stdout.strip():
            print("无变更")
            return True
        subprocess.run(["git", "commit", "-m", f"AI 决策情报 {date['cn']}"], cwd=PROJECT_DIR, check=True)
        subprocess.run(["git", "push"], cwd=PROJECT_DIR, check=True)
        return True
    except Exception as exc:
        print(f"Git 推送失败（请稍后手动处理）：{exc}")
        return False


def items_from_file(path: Path) -> list[dict[str, Any]]:
    data = read_json(path)
    if isinstance(data, dict):
        data = data.get("items", [])
    if not isinstance(data, list):
        raise ValueError("候选条目文件必须包含 items 数组")
    return data


def build_digest(date: dict[str, str], args: argparse.Namespace) -> tuple[list[dict[str, Any]], dict[str, Any] | None, bool]:
    if args.items_file:
        return select_items(items_from_file(Path(args.items_file)), args.limit), None, False
    manual = load_manual_digest(date)
    if manual and manual.get("items"):
        return select_items(manual["items"], args.limit), manual, True
    if args.fetch:
        return select_items(fetch_candidates(), args.limit), None, False
    return select_items(FALLBACK_ITEMS, args.limit), None, True


def main() -> int:
    parser = argparse.ArgumentParser(description="生成中文 AI 决策情报日报")
    parser.add_argument("--date", help="日报日期，格式 YYYY-MM-DD；默认上海当日")
    parser.add_argument("--fetch", action="store_true", help="在没有人工日报数据时抓取 RSS 候选条目")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="精选条数，默认 5")
    parser.add_argument("--items-file", help="从 JSON 候选条目文件生成，用于模型研判后的二次渲染")
    parser.add_argument("--editorial-file", help="GitHub Models 输出的中文编辑研判 JSON 文件")
    parser.add_argument("--export-items", help="导出选中的候选条目 JSON，供模型研判使用")
    parser.add_argument("--no-render", action="store_true", help="仅生成候选条目，不写 HTML")
    parser.add_argument("--push", action="store_true", help="提交并推送生成文件")
    args = parser.parse_args()
    if args.limit != DEFAULT_LIMIT:
        print("提示：公开日报固定展示 5 条，已将数量设为 5。")
        args.limit = DEFAULT_LIMIT

    date = get_date(args.date)
    items, manual, is_manual = build_digest(date, args)
    if args.editorial_file:
        editorial = parse_editorial_json(Path(args.editorial_file))
        items = apply_editorial(items, editorial)
    else:
        editorial = None

    if len(items) != DEFAULT_LIMIT and not (len(items) == 1 and items[0]["category"] == "系统"):
        raise RuntimeError(f"候选不足：需要 {DEFAULT_LIMIT} 条，当前只有 {len(items)} 条")

    if args.export_items:
        target = Path(args.export_items)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({"date": date["iso"], "items": items}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"已导出候选：{target}")
    if args.no_render:
        return 0

    brief = build_daily_brief(items, manual, editorial)
    (PROJECT_DIR / f"{date['iso']}.html").write_text(generate_html(date, items, manual, editorial), encoding="utf-8")
    (PROJECT_DIR / "index.html").write_text(generate_index_redirect(date), encoding="utf-8")
    if not is_manual:
        archive_generated(date, items, brief)
    print(f"生成：{date['iso']}.html")
    print(f"精选：{len(items)} 条，评分降序：{all(items[index]['score'] >= items[index + 1]['score'] for index in range(len(items) - 1))}")
    for index, item in enumerate(items, 1):
        print(f"  {index}. [{item['score']}] {item['title']}")
    print(f"公开链接：{PUBLIC_BASE_URL}/{date['iso']}.html")
    if args.push:
        git_push(date)
    return 0


if __name__ == "__main__":
    sys.exit(main())
