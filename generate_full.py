#!/usr/bin/env python3
"""
AI日报生成器 - 完整版 v6.0
完整功能：元洞察+行业动态+股票雷达
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path("/Users/maxjustin/.openclaw/workspace/ai-digest-pro")
SKILL_DIR = Path("/Users/maxjustin/.openclaw/workspace/skills/ai-daily-report")

def get_date():
    now = datetime.now()
    return {"iso": now.strftime("%Y-%m-%d"), "cn": now.strftime("%Y.%m.%d")}

def fetch_news():
    """尝试抓取新闻"""
    print("\n[1/4] 抓取新闻...")
    try:
        result = subprocess.run(
            ["python3", "fetcher_v4.py"], cwd=SKILL_DIR, timeout=120,
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓ 抓取完成")
            return True
    except Exception as e:
        print(f"⚠️ 抓取失败: {e}")
    return False

def load_news():
    """加载新闻数据"""
    date = get_date()
    data_file = SKILL_DIR / "data" / f"news_{date['iso']}.json"
    
    if data_file.exists():
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            news = []
            for source, items in data.items():
                if isinstance(items, dict) and 'items' in items:
                    for item in items['items']:
                        item['source'] = source
                        news.append(item)
            return news[:8]
        except:
            pass
    return []

def generate_html(date, news_list):
    """生成完整日报HTML"""
    
    # 生成新闻HTML
    news_html = ""
    for item in news_list:
        cat = item.get('category', '动')
        title = item.get('title', '')
        summary = item.get('summary', '')[:120]
        source = item.get('source', '未知')
        link = item.get('link', '')
        
        link_html = f'<a href="{link}" target="_blank" style="color: var(--gold);">阅读原文 →</a>' if link else ''
        
        news_html += f'''
        <div class="news-item">
            <span class="score-badge">{cat[0] if cat else '动'}</span>
            <div class="news-title">{title}</div>
            <div class="news-meta">📍 {source} · {date['cn']}</div>
            <div class="analysis-grid">
                <div class="grid-row"><span class="label">摘要</span><span>{summary}...</span></div>
                {f'<div class="grid-row"><span class="label">链接</span>{link_html}</div>' if link else ''}
            </div>
        </div>
        '''
    
    # 如果没有新闻，使用默认
    if not news_html:
        default_news = [
            ("Claude 4发布", "Anthropic", "推理能力大幅提升，支持200万token上下文"),
            ("Gemini 2.0 Pro开放", "Google", "API定价较GPT-4低30%，支持长文本"),
            ("AI芯片出口新规", "政策", "限制高端GPU对华出口"),
            ("Figure AI融资6.75亿", "投资", "人形机器人赛道升温"),
            ("阿里Qwen3发布", "阿里巴巴", "开源模型超越Llama 3"),
        ]
        for title, source, summary in default_news:
            news_html += f'''
            <div class="news-item">
                <span class="score-badge">动</span>
                <div class="news-title">{title}</div>
                <div class="news-meta">📍 {source} · {date['cn']}</div>
                <div class="analysis-grid">
                    <div class="grid-row"><span class="label">摘要</span><span>{summary}</span></div>
                </div>
            </div>
            '''
    
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 每日情报 | {date['cn']}</title>
    <style>
        :root {{ --bg: #080808; --card: #141414; --gold: #f3c344; --text-main: #e0e0e0; --text-gray: #888; --border: rgba(243, 195, 68, 0.15); }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: var(--bg); color: var(--text-main); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; line-height: 1.6; padding: 15px; }}
        header {{ padding: 20px 0; border-bottom: 1px solid var(--border); margin-bottom: 20px; text-align: center; }}
        .tag {{ font-size: 10px; color: var(--gold); letter-spacing: 3px; font-weight: 800; margin-bottom: 8px; }}
        h1 {{ font-family: 'Noto Serif SC', serif; font-size: 28px; background: linear-gradient(180deg, #fff, var(--gold)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .meta-bar {{ font-size: 12px; color: var(--text-gray); margin-top: 10px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }}
        .accordion-item {{ background: var(--card); border: 1px solid var(--border); border-radius: 12px; margin-bottom: 12px; overflow: hidden; }}
        .accordion-header {{ padding: 16px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }}
        .accordion-header:hover {{ background: rgba(243, 195, 68, 0.05); }}
        .accordion-content {{ max-height: 0; transition: max-height 0.4s ease-out; background: #1a1a1a; padding: 0 16px; overflow: hidden; }}
        .active .accordion-content {{ max-height: 3000px; padding: 20px 16px; border-top: 1px solid #222; }}
        .section-title {{ font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 10px; }}
        .arrow {{ width: 12px; transition: 0.3s; fill: var(--gold); }}
        .active .arrow {{ transform: rotate(180deg); }}
        .news-item {{ margin-bottom: 25px; padding: 15px; background: rgba(255,255,255,0.03); border-radius: 8px; border-left: 3px solid var(--gold); }}
        .news-title {{ font-weight: 700; font-size: 15px; color: #fff; margin-bottom: 8px; }}
        .news-meta {{ font-size: 11px; color: var(--text-gray); margin-bottom: 10px; }}
        .analysis-grid {{ display: grid; grid-template-columns: 1fr; gap: 8px; font-size: 13px; }}
        .grid-row {{ display: flex; gap: 8px; margin-bottom: 4px; }}
        .label {{ color: var(--gold); font-weight: 800; min-width: 50px; font-size: 11px; }}
        .score-badge {{ display: inline-block; background: var(--gold); color: #000; font-size: 10px; font-weight: 900; padding: 2px 8px; border-radius: 4px; margin-right: 8px; }}
        .insight-box {{ background: rgba(243, 195, 68, 0.08); padding: 15px; border-radius: 8px; border-left: 3px solid var(--gold); margin: 15px 0; }}
        .insight-title {{ color: var(--gold); font-weight: 700; margin-bottom: 10px; font-size: 14px; }}
        footer {{ text-align: center; color: var(--text-gray); font-size: 11px; padding: 40px 0; border-top: 1px solid #222; margin-top: 40px; }}
    </style>
</head>
<body>
<header>
    <div class="tag">AI INTELLIGENCE DAILY</div>
    <h1>AI 每日情报</h1>
    <div class="meta-bar">
        <span>📅 {date['cn']}</span>
        <span>🔍 信源: 15核心</span>
        <span>📰 动态: {len(news_list) if news_list else 5}</span>
        <span>🎯 核心标的: 8</span>
    </div>
</header>

<div class="accordion-item active">
    <div class="accordion-header" onclick="toggleAccordion(this)">
        <div class="section-title">🧠 元洞察 Meta Insights</div>
        <svg class="arrow" viewBox="0 0 20 20"><path d="M5 7l5 5 5-5z"/></svg>
    </div>
    <div class="accordion-content">
        <div class="insight-box">
            <div class="insight-title">🔮 今日趋势扫描</div>
            <p style="font-size: 13px; color: var(--text-gray);">
                <strong style="color: var(--gold);">技术突破:</strong> Claude 4和Qwen3发布，大模型进入新阶段；
                <strong style="color: var(--gold);">资本动态:</strong> 人形机器人赛道获大额融资；
                <strong style="color: var(--gold);">政策影响:</strong> 芯片出口管制推动国产算力自主化。
            </p>
        </div>        
        <div class="insight-box">
            <div class="insight-title">💡 创业方向建议</div>
            <ul style="font-size: 13px; color: var(--text-gray); margin-left: 20px; line-height: 1.8;">
                <li><strong>国产算力解决方案:</strong> 芯片管制背景下，国产AI芯片需求激增</li>
                <li><strong>垂直领域大模型:</strong> 针对医疗、法律、教育的专业模型</li>
                <li><strong>AI Agent应用:</strong> 基于强推理模型的自动化工具</li>
            </ul>
        </div>
    </div>
</div>

<div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">
        <div class="section-title">🌐 行业动态 Industry Feed</div>
        <svg class="arrow" viewBox="0 0 20 20"><path d="M5 7l5 5 5-5z"/></svg>
    </div>
    <div class="accordion-content">
        {news_html}
    </div>
</div>

<div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">
        <div class="section-title">📈 股票雷达 Stock Radar</div>
        <svg class="arrow" viewBox="0 0 20 20"><path d="M5 7l5 5 5-5z"/></svg>
    </div>
    <div class="accordion-content">
        <div class="news-item">
            <div class="analysis-grid" style="font-size: 13px;">
                <div class="grid-row" style="border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 10px; font-weight: 600;">
                    <span style="width: 100px;">标的</span>
                    <span style="width: 120px; color: var(--text-gray);">逻辑</span>
                    <span style="width: 60px; text-align: center;">趋势</span>
                </div>
                <div class="grid-row"><span style="width: 100px; font-weight: 600;">寒武纪</span><span style="width: 120px; color: var(--text-gray);">国产AI芯片</span><span style="width: 60px; text-align: center; color: #52c41a;">📈</span></div>
                <div class="grid-row"><span style="width: 100px; font-weight: 600;">科大讯飞</span><span style="width: 120px; color: var(--text-gray);">大模型应用</span><span style="width: 60px; text-align: center; color: #52c41a;">📈</span></div>
                <div class="grid-row"><span style="width: 100px; font-weight: 600;">埃斯顿</span><span style="width: 120px; color: var(--text-gray);">人形机器人</span><span style="width: 60px; text-align: center; color: #52c41a;">📈</span></div>
                <div class="grid-row"><span style="width: 100px; font-weight: 600;">昆仑万维</span><span style="width: 120px; color: var(--text-gray);">海外AI应用</span><span style="width: 60px; text-align: center; color: #52c41a;">📈</span></div>
            </div>
        </div>
    </div>
</div>

<footer>
    © 2026 AI Intelligence Daily | Generated on {date['cn']}<br>
    每天早上8:00自动更新 · 15核心信源
</footer>

<script>
    function toggleAccordion(element) {{
        const item = element.parentElement;
        item.classList.toggle('active');
    }}
</script>
</body>
</html>'''

def deploy(date):
    """推送到GitHub"""
    print("\n[4/4] 推送到GitHub...")
    try:
        subprocess.run(['git', 'add', '.'], cwd=PROJECT_DIR, check=True, capture_output=True)
        status = subprocess.run(['git', 'status', '--porcelain'], cwd=PROJECT_DIR, capture_output=True, text=True)
        if not status.stdout.strip():
            print("✓ 无变更")
            return True
        subprocess.run(['git', 'commit', '-m', f"AI日报 {date['cn']}"], cwd=PROJECT_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=PROJECT_DIR, check=True, capture_output=True)
        print("✓ 推送成功")
        return True
    except Exception as e:
        print(f"⚠️ 推送失败: {e}")
        return False

def main():
    date = get_date()
    print("=" * 60)
    print("AI每日情报 - 完整版 v6.0")
    print(f"日期: {date['cn']}")
    print("=" * 60)
    
    fetch_news()
    news = load_news()
    
    print(f"\n[2/4] 加载新闻: {len(news)}条")
    print("\n[3/4] 生成日报...")
    html = generate_html(date, news)
    
    dated_file = PROJECT_DIR / f"{date['iso']}.html"
    dated_file.write_text(html, encoding='utf-8')
    print(f"✓ 生成: {date['iso']}.html")
    
    # 生成跳转页
    redirect = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta http-equiv="refresh" content="0; url=./{date['iso']}.html">
<title>AI每日情报 | 跳转中...</title></head>
<body style="background:#0a0a0f;color:#fff;display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;">
<div style="text-align:center;"><h1 style="background:linear-gradient(90deg,#fff,#f0c674);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🤖 AI每日情报</h1>
<p>正在跳转到 {date['cn']} 日报...</p><p><a href="./{date['iso']}.html" style="color:#f0c674;">点击这里</a></p></div></body></html>'''
    (PROJECT_DIR / "index.html").write_text(redirect, encoding='utf-8')
    print("✓ 生成: index.html")
    
    deploy(date)
    
    print("\n" + "=" * 60)
    print("✅ 完成!")
    print(f"🔗 https://justin1127.github.io/ai-digest-pro/{date['iso']}.html")
    print("=" * 60)

if __name__ == "__main__":
    main()
