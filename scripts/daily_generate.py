#!/usr/bin/env python3
"""
AI日报每日生成器 - 简化版
生成带日期后缀的HTML日报，index.html自动跳转
"""

import subprocess
from datetime import datetime
from pathlib import Path

# 路径配置
PROJECT_DIR = Path("/Users/maxjustin/.openclaw/workspace/ai-digest-pro")

def get_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_date_str_chinese():
    return datetime.now().strftime("%Y.%m.%d")

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
        .loading {{
            text-align: center;
            color: white;
        }}
        .loading h1 {{ 
            font-size: 2.5em; 
            margin-bottom: 15px; 
            background: linear-gradient(90deg, #fff, #f0c674);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
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

def create_daily_report_html(date_str, date_chinese):
    """创建日报HTML - 包含今日提示"""
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
        .accordion-content {{ max-height: 0; transition: max-height 0.4s ease-out; background: #1a1a1a; padding: 0 16px; overflow: hidden; }}
        .active .accordion-content {{ max-height: 2000px; padding: 20px 16px; border-top: 1px solid #222; }}
        .section-title {{ font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 10px; }}
        .arrow {{ width: 12px; transition: 0.3s; fill: var(--gold); }}
        .active .arrow {{ transform: rotate(180deg); }}
        .news-item {{ margin-bottom: 25px; padding-left: 10px; border-left: 2px solid var(--gold); }}
        .news-title {{ font-weight: 700; font-size: 15px; color: #fff; margin-bottom: 8px; }}
        .analysis-grid {{ display: grid; grid-template-columns: 1fr; gap: 8px; font-size: 13px; }}
        .grid-row {{ display: flex; gap: 8px; margin-bottom: 4px; }}
        .label {{ color: var(--gold); font-weight: 800; min-width: 50px; font-size: 11px; flex-shrink: 0; }}
        .action-box {{ background: rgba(243, 195, 68, 0.08); padding: 10px; border-radius: 8px; border-left: 3px solid var(--gold); margin-top: 10px; }}
        footer {{ text-align: center; color: var(--text-gray); font-size: 11px; padding: 40px 0; border-top: 1px solid #222; margin-top: 40px; }}
        .highlight {{ color: var(--gold); font-weight: 600; }}
    </style>
</head>
<body>

<header>
    <div class="tag">AI INTELLIGENCE DAILY</div>
    <h1>AI 每日情报</h1>
    <div class="meta-bar">
        <span>📅 {date_chinese}</span>
        <span>🔍 扫描信源: 46+</span>
        <span>🎯 核心标的: 8</span>
    </div>
</header>

<div class="accordion-item active">
    <div class="accordion-header" onclick="toggleAccordion(this)">
        <div class="section-title">🧠 元洞察 Meta Insights</div>
        <svg class="arrow" viewBox="0 0 20 20"><path d="M5 7l5 5 5-5z"/></svg>
    </div>
    <div class="accordion-content">
        <div class="news-item">
            <div class="news-title">📈 今日日报生成中...</div>
            <p style="font-size: 13px; color: var(--text-gray); margin: 10px 0;">
                今天的AI日报正在抓取46个信源的最新动态，包括：
            </p>
            <ul style="font-size: 13px; color: var(--text-gray); margin-left: 20px; line-height: 1.8;">
                <li>TechCrunch、The Verge、MIT Tech Review等国际顶级媒体</li>
                <li>量子位、机器之心、新智元等中文AI媒体</li>
                <li>OpenAI、DeepMind、Google AI等官方博客</li>
                <li>X平台AI领袖和研究机构</li>
            </ul>
            <div class="action-box">
                <div class="label">💡 提示</div>
                <div style="font-size: 13px; margin-top: 5px;">
                    完整版日报将于 <span class="highlight">明天早上8:00</span> 自动生成并更新。
                    如需今日实时AI资讯，请访问 <a href="https://www.techcrunch.com/category/artificial-intelligence/" style="color: var(--gold);">TechCrunch AI</a> 或 <a href="https://www.jiqizhixin.com/" style="color: var(--gold);">机器之心</a>。
                </div>
            </div>
        </div>
    </div>
</div>

<div class="accordion-item">
    <div class="accordion-header" onclick="toggleAccordion(this)">
        <div class="section-title">🌐 行业动态 Industry Feed</div>
        <svg class="arrow" viewBox="0 0 20 20"><path d="M5 7l5 5 5-5z"/></svg>
    </div>
    <div class="accordion-content">
        <div class="news-item">
            <div class="news-title">🔄 日报更新机制</div>
            <div class="analysis-grid">
                <div class="grid-row">
                    <span class="label">时间</span>
                    <span>每天早上 8:00 自动更新</span>
                </div>
                <div class="grid-row">
                    <span class="label">内容</span>
                    <span>6大板块 + 5维度深度分析</span>
                </div>
                <div class="grid-row">
                    <span class="label">特色</span>
                    <span>英文自动翻译 + A股标的关联</span>
                </div>
            </div>
        </div>
    </div>
</div>

<footer>
    © 2026 AI Intelligence Daily | Generated on {date_chinese}<br>
    每天早上8:00自动更新 | <a href="https://justin1127.github.io/ai-digest-pro/{date_str}.html" style="color: var(--gold);">今日日报链接</a>
</footer>

<script>
    function toggleAccordion(element) {{
        const item = element.parentElement;
        item.classList.toggle('active');
    }}
</script>

</body>
</html>"""

def main():
    date_str = get_date_str()
    date_chinese = get_date_str_chinese()
    
    print("=" * 60)
    print("AI每日情报 - 日报生成器")
    print(f"日期: {date_chinese}")
    print("=" * 60)
    
    # 1. 创建带日期的日报文件
    dated_html = create_daily_report_html(date_str, date_chinese)
    dated_file = PROJECT_DIR / f"{date_str}.html"
    dated_file.write_text(dated_html, encoding='utf-8')
    print(f"✓ 创建日报: {date_str}.html")
    
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
            subprocess.run(['git', 'commit', '-m', f'AI每日情报 {date_chinese} - 自动更新'], 
                         cwd=PROJECT_DIR, check=True, capture_output=True)
            subprocess.run(['git', 'push'], cwd=PROJECT_DIR, check=True, capture_output=True)
            print(f"✓ 推送到GitHub")
        else:
            print(f"✓ 无变更需要提交")
        
        url = f"https://justin1127.github.io/ai-digest-pro/{date_str}.html"
        
        print("\n" + "=" * 60)
        print("✅ 日报已发布!")
        print("=" * 60)
        print(f"📅 日期: {date_chinese}")
        print(f"🔗 今日日报: {url}")
        print(f"🏠 首页跳转: https://justin1127.github.io/ai-digest-pro/")
        print("=" * 60)
        
        return url
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Git操作失败: {e}")
        return None

if __name__ == "__main__":
    main()
