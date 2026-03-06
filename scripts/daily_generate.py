#!/usr/bin/env python3
"""
AI日报生成器 - 完整工作流 v4.0
抓取 → 分析 → 生成HTML → 部署
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 路径配置
SKILL_DIR = Path("/Users/maxjustin/.openclaw/workspace/skills/ai-daily-report")
PROJECT_DIR = Path("/Users/maxjustin/.openclaw/workspace/ai-digest-pro")

def get_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_date_str_chinese():
    return datetime.now().strftime("%Y.%m.%d")

def run_fetcher():
    """步骤1: 抓取新闻"""
    print("\n" + "="*60)
    print("[步骤1/3] 抓取AI新闻...")
    print("="*60)
    
    result = subprocess.run(
        ["python3", "fetcher_v4.py"],
        cwd=SKILL_DIR,
        capture_output=False,
        timeout=120
    )
    return result.returncode == 0

def load_news_data():
    """加载抓取的新闻数据"""
    today = get_date_str()
    data_file = SKILL_DIR / "data" / f"news_{today}.json"
    
    if not data_file.exists():
        return None
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def categorize_news(news_data):
    """对新闻进行分类和筛选"""
    if not news_data:
        return []
    
    all_items = []
    for source, data in news_data.items():
        if isinstance(data, dict) and 'items' in data:
            for item in data['items']:
                item['source_name'] = source
                all_items.append(item)
    
    # 按时间排序（如果有发布时间）
    # 这里简化处理，直接取前8条
    return all_items[:8]

def generate_html_content(news_items, date_str, date_chinese):
    """生成日报HTML内容"""
    
    # 生成新闻HTML
    news_html = ""
    for i, item in enumerate(news_items, 1):
        category = "技术" if any(kw in item.get('title', '') for kw in ['发布', '推出', '模型', '技术']) else "动态"
        news_html += f"""
        <div class="news-item">
            <span class="score-badge">{category[0]}</span>
            <div class="news-title">{item.get('title', '无标题')}</div>
            <div class="news-meta">📍 {item.get('source_name', '未知')} · {date_chinese}</div>
            <div class="analysis-grid">
                <div class="grid-row">
                    <span class="label">摘要</span>
                    <span>{item.get('summary', '暂无摘要')[:150]}...</span>
                </div>
                <div class="grid-row">
                    <span class="label">链接</span>
                    <a href="{item.get('link', '#')}" style="color: var(--gold);" target="_blank">阅读原文 →</a>
                </div>
            </div>
        </div>
        """
    
    if not news_items:
        news_html = """
        <div class="news-item">
            <div class="news-title">📰 今日AI动态</div>
            <p style="font-size: 13px; color: var(--text-gray);">
                正在抓取最新AI资讯，请稍后再试...
            </p>
        </div>
        """
    
    return f"""
<!DOCTYPE html>
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
        footer {{ text-align: center; color: var(--text-gray); font-size: 11px; padding: 40px 0; border-top: 1px solid #222; margin-top: 40px; }}
    </style>
</head>
<body>

<header>
    <div class="tag">AI INTELLIGENCE DAILY</div>
    <h1>AI 每日情报</h1>
    <div class="meta-bar">
        <span>📅 {date_chinese}</span>
        <span>🔍 信源: 15核心</span>
        <span>📰 动态: {len(news_items)}</span>
    </div>
</header>

<div class="accordion-item active">
    <div class="accordion-header" onclick="toggleAccordion(this)">
        <div class="section-title">🌐 今日AI动态</div>
        <svg class="arrow" viewBox="0 0 20 20"><path d="M5 7l5 5 5-5z"/></svg>
    </div>
    <div class="accordion-content">
        {news_html}
    </div>
</div>

<footer>
    © 2026 AI Intelligence Daily | {date_chinese}<br>
    每天早上8:00自动更新 · 15核心信源抓取
</footer>

<script>
    function toggleAccordion(element) {{
        const item = element.parentElement;
        item.classList.toggle('active');
    }}
</script>

</body>
</html>
"""

def create_redirect_index(date_str):
    """创建自动跳转的index.html"""
    return f"""
<!DOCTYPE html>
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
</html>
"""

def deploy(news_items):
    """步骤2-3: 生成HTML并部署"""
    print("\n" + "="*60)
    print("[步骤2/3] 生成日报HTML...")
    print("="*60)
    
    date_str = get_date_str()
    date_chinese = get_date_str_chinese()
    
    # 生成日报HTML
    html_content = generate_html_content(news_items, date_str, date_chinese)
    dated_file = PROJECT_DIR / f"{date_str}.html"
    dated_file.write_text(html_content, encoding='utf-8')
    print(f"✓ 生成日报: {date_str}.html ({len(news_items)} 条新闻)")
    
    # 创建跳转index.html
    redirect_html = create_redirect_index(date_str)
    index_file = PROJECT_DIR / "index.html"
    index_file.write_text(redirect_html, encoding='utf-8')
    print(f"✓ 创建跳转页: index.html")
    
    print("\n" + "="*60)
    print("[步骤3/3] 部署到GitHub...")
    print("="*60)
    
    # Git提交
    try:
        subprocess.run(['git', 'add', f'{date_str}.html', 'index.html'], 
                     cwd=PROJECT_DIR, check=True, capture_output=True)
        
        status = subprocess.run(['git', 'status', '--porcelain'], 
                               cwd=PROJECT_DIR, capture_output=True, text=True)
        
        if status.stdout.strip():
            subprocess.run(['git', 'commit', '-m', f'AI日报 {date_chinese} - {len(news_items)}条动态'], 
                         cwd=PROJECT_DIR, check=True, capture_output=True)
            subprocess.run(['git', 'push'], cwd=PROJECT_DIR, check=True, capture_output=True)
            print(f"✓ 已推送到GitHub")
        else:
            print(f"✓ 无变更需要提交")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Git操作失败: {e}")
        return False

def main():
    """主流程"""
    date_chinese = get_date_str_chinese()
    
    print("=" * 60)
    print(f"AI每日情报 - 自动发布系统 v4.0")
    print(f"日期: {date_chinese}")
    print("=" * 60)
    
    try:
        # 步骤1: 抓取新闻
        if not run_fetcher():
            print("\n⚠️ 抓取返回错误，继续部署...")
        
        # 步骤2-3: 生成并部署
        news_data = load_news_data()
        news_items = categorize_news(news_data) if news_data else []
        
        if deploy(news_items):
            date_str = get_date_str()
            url = f"https://justin1127.github.io/ai-digest-pro/{date_str}.html"
            
            print("\n" + "=" * 60)
            print("✅ AI每日情报发布成功!")
            print("=" * 60)
            print(f"📅 日期: {date_chinese}")
            print(f"📰 内容: {len(news_items)}条AI动态")
            print(f"🔗 访问地址: {url}")
            print("=" * 60)
            return url
        else:
            print("\n✗ 部署失败")
            return None
            
    except subprocess.TimeoutExpired:
        print("\n✗ 操作超时")
        return None
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        return None

if __name__ == "__main__":
    url = main()
    sys.exit(0 if url else 1)
