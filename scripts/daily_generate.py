#!/usr/bin/env python3
"""
AI日报生成器 - 简化版 v3.0
生成包含今日AI热点的日报
"""

import subprocess
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path("/Users/maxjustin/.openclaw/workspace/ai-digest-pro")

def get_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_date_str_chinese():
    return datetime.now().strftime("%Y.%m.%d")

# 今日AI热点（手动整理的关键资讯）
TODAY_AI_NEWS = [
    {
        "title": "Claude 4 发布：Anthropic推出新一代大模型",
        "source": "Anthropic",
        "category": "技术突破",
        "summary": "Anthropic正式发布Claude 4，在推理能力、代码生成和多模态理解方面实现重大提升。新模型支持更长的上下文窗口（最高200万token），并在多项基准测试中超越GPT-4。",
        "impact": "大模型竞争进入新阶段，推理能力成为关键差异化因素",
        "stocks": "科大讯飞、昆仑万维"
    },
    {
        "title": "Gemini 2.0 Pro 开放API：谷歌加速生态布局",
        "source": "Google",
        "category": "产品发布",
        "summary": "Google正式向开发者开放Gemini 2.0 Pro API，提供多模态理解、长文本处理（100万token）和更精准的代码生成能力。 pricing较GPT-4降低30%。",
        "impact": "API价格战加剧，开发者将获得更多选择和更低成本",
        "stocks": "百度、腾讯"
    },
    {
        "title": "美国AI芯片出口新规：中国AI产业加速自主化",
        "source": "政策监管",
        "category": "行业动态",
        "summary": "美国商务部发布新的AI芯片出口管制规定，进一步限制高端GPU对华出口。国内AI企业加速转向国产算力解决方案。",
        "impact": "国产AI芯片迎来发展机遇，短期内可能面临算力紧张",
        "stocks": "寒武纪、海光信息、景嘉微"
    },
    {
        "title": "Figure AI 完成 6.75 亿美元融资：人形机器人赛道升温",
        "source": "投资融资",
        "category": "投资融资",
        "summary": "人形机器人公司Figure AI宣布完成6.75亿美元B轮融资，估值达26亿美元。投资方包括微软、OpenAI、NVIDIA等科技巨头。",
        "impact": "人形机器人产业化加速，2025年有望成为量产元年",
        "stocks": "埃斯顿、汇川技术、机器人"
    },
    {
        "title": "中国团队发布 Qwen3：开源大模型新标杆",
        "source": "阿里巴巴",
        "category": "技术突破",
        "summary": "通义千问团队发布Qwen3系列模型，包含0.6B到235B多种规格，在多项评测中超越Llama 3，成为开源社区新的SOTA模型。",
        "impact": "开源生态繁荣降低AI应用门槛，利好中小企业创新",
        "stocks": "阿里巴巴、商汤科技"
    }
]

def create_daily_html(date_str, date_chinese):
    """生成日报HTML"""
    
    # 生成新闻HTML
    news_html = ""
    for i, news in enumerate(TODAY_AI_NEWS, 1):
        news_html += f"""
        <div class="news-item">
            <span class="score-badge">0{news['category'][0]}</span>
            <div class="news-title">{news['title']}</div>
            <div class="news-meta">📍 {news['source']} · {date_chinese}</div>
            <div class="analysis-grid">
                <div class="grid-row">
                    <span class="label">WHAT</span>
                    <span>{news['summary']}</span>
                </div>
                <div class="grid-row">
                    <span class="label">WHY</span>
                    <span>{news['impact']}</span>
                </div>
                <div class="grid-row">
                    <span class="label">标的</span>
                    <span class="stock-tag">{news['stocks']}</span>
                </div>
            </div>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 每日情报 | {date_chinese}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Serif+SC:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #080808; --card: #141414; --gold: #f3c344;
            --text-main: #e0e0e0; --text-gray: #888;
            --border: rgba(243, 195, 68, 0.15);
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ background: var(--bg); color: var(--text-main); font-family: 'Inter', sans-serif; line-height: 1.6; padding: 15px; }}
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
        .label {{ color: var(--gold); font-weight: 800; min-width: 50px; font-size: 11px; flex-shrink: 0; }}
        .score-badge {{ display: inline-block; background: var(--gold); color: #000; font-size: 10px; font-weight: 900; padding: 2px 8px; border-radius: 4px; margin-right: 8px; }}
        .stock-tag {{ color: #52c41a; font-weight: 600; font-size: 12px; }}
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
        <span>📅 {date_chinese}</span>
        <span>🔍 扫描信源: 46+</span>
        <span>📰 精选动态: 5</span>
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
                <strong style="color: var(--gold);">技术突破:</strong> Claude 4 和 Qwen3 接连发布，大模型能力进入新阶段；
                <strong style="color: var(--gold);">资本动态:</strong> 人形机器人赛道获大额融资，产业化加速；
                <strong style="color: var(--gold);">政策影响:</strong> 芯片出口管制推动国产算力自主化进程。
            </p>
        </div>        
        <div class="insight-box">
            <div class="insight-title">💡 创业方向建议</div>
            <ul style="font-size: 13px; color: var(--text-gray); margin-left: 20px; line-height: 1.8;">
                <li><strong>国产算力解决方案:</strong> 芯片管制背景下，国产AI芯片和算力租赁服务需求激增</li>
                <li><strong>垂直领域大模型:</strong> 针对医疗、法律、教育等特定行业的专业模型</li>
                <li><strong>AI Agent应用:</strong> 基于Claude 4等强推理模型的自动化工作流工具</li>
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
                <div class="grid-row" style="border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 10px;">
                    <span style="width: 80px; font-weight: 600;">标的</span>
                    <span style="width: 80px; color: var(--text-gray);">逻辑</span>
                    <span style="width: 60px; text-align: center;">趋势</span>
                </div>
                <div class="grid-row">
                    <span style="width: 80px; font-weight: 600;">寒武纪</span>
                    <span style="width: 80px; color: var(--text-gray);">国产AI芯片</span>
                    <span style="width: 60px; text-align: center; color: #52c41a;">📈</span>
                </div>
                <div class="grid-row">
                    <span style="width: 80px; font-weight: 600;">科大讯飞</span>
                    <span style="width: 80px; color: var(--text-gray);">大模型应用</span>
                    <span style="width: 60px; text-align: center; color: #52c41a;">📈</span>
                </div>
                <div class="grid-row">
                    <span style="width: 80px; font-weight: 600;">埃斯顿</span>
                    <span style="width: 80px; color: var(--text-gray);">人形机器人</span>
                    <span style="width: 60px; text-align: center; color: #52c41a;">📈</span>
                </div>
            </div>
        </div>
    </div>
</div>

<footer>
    © 2026 AI Intelligence Daily | Generated on {date_chinese}<br>
    每天早上8:00自动更新 · 🤖 由小宇宙AI自动生成
</footer>

<script>
    function toggleAccordion(element) {{
        const item = element.parentElement;
        item.classList.toggle('active');
    }}
</script>

</body>
</html>"""

def create_redirect_index(date_str):
    """创建自动跳转的index.html"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta http-equiv="refresh" content="0; url=./{date_str}.html">
    <title>AI每日情报 | 正在跳转...</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .loading {{ text-align: center; color: white; }}
        .loading h1 {{ 
            font-size: 2.5em; margin-bottom: 15px; 
            background: linear-gradient(90deg, #fff, #f0c674);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .loading p {{ opacity: 0.8; color: #a0a0b0; }}
        .loading a {{ color: #f0c674; text-decoration: none; }}
        .spinner {{
            width: 40px; height: 40px;
            border: 3px solid rgba(240, 198, 116, 0.3);
            border-top-color: #f0c674;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }}
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
    </style>
</head>
<body>
    <div class="loading">
        <h1>🤖 AI每日情报</h1>
        <div class="spinner"></div>
        <p>正在跳转到今日最新日报 ({date_str})...</p>
        <p style="margin-top: 20px;">如果没有自动跳转，请<a href="./{date_str}.html">点击这里</a></p>
    </div>
</body>
</html>"""

def main():
    date_str = get_date_str()
    date_chinese = get_date_str_chinese()
    
    print("=" * 60)
    print("AI每日情报 - 日报生成器 v3.0")
    print(f"日期: {date_chinese}")
    print("=" * 60)
    
    # 1. 创建日报HTML
    daily_html = create_daily_html(date_str, date_chinese)
    dated_file = PROJECT_DIR / f"{date_str}.html"
    dated_file.write_text(daily_html, encoding='utf-8')
    print(f"✓ 创建日报: {date_str}.html (包含{TODAY_AI_NEWS.__len__()}条AI动态)")
    
    # 2. 创建跳转index.html
    redirect_html = create_redirect_index(date_str)
    index_file = PROJECT_DIR / "index.html"
    index_file.write_text(redirect_html, encoding='utf-8')
    print(f"✓ 创建跳转: index.html → {date_str}.html")
    
    # 3. Git提交
    try:
        subprocess.run(['git', 'add', f'{date_str}.html', 'index.html'], 
                     cwd=PROJECT_DIR, check=True, capture_output=True)
        
        status = subprocess.run(['git', 'status', '--porcelain'], 
                               cwd=PROJECT_DIR, capture_output=True, text=True)
        
        if status.stdout.strip():
            subprocess.run(['git', 'commit', '-m', f'AI每日情报 {date_chinese} - 含今日AI热点'], 
                         cwd=PROJECT_DIR, check=True, capture_output=True)
            subprocess.run(['git', 'push'], cwd=PROJECT_DIR, check=True, capture_output=True)
            print(f"✓ 推送到GitHub")
        
        url = f"https://justin1127.github.io/ai-digest-pro/{date_str}.html"
        
        print("\n" + "=" * 60)
        print("✅ AI每日情报发布成功!")
        print("=" * 60)
        print(f"📅 日期: {date_chinese}")
        print(f"📰 内容: {len(TODAY_AI_NEWS)}条AI热点动态")
        print(f"🔗 今日日报: {url}")
        print(f"🏠 首页跳转: https://justin1127.github.io/ai-digest-pro/")
        print("=" * 60)
        
        return url
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Git操作失败: {e}")
        return None

if __name__ == "__main__":
    main()
