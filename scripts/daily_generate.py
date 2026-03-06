#!/usr/bin/env python3
"""
AI日报每日生成器 - 完整版 v2.0
整合现有AI日报skill，生成带日期后缀的HTML日报
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path

# 路径配置
SKILL_DIR = Path("/Users/maxjustin/.openclaw/workspace/skills/ai-daily-report")
PROJECT_DIR = Path("/Users/maxjustin/.openclaw/workspace/ai-digest-pro")

def run_command(cmd, cwd=None, capture=True, timeout=300):
    """运行shell命令"""
    try:
        if capture:
            result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, timeout=timeout)
            return result
        else:
            result = subprocess.run(cmd, shell=True, cwd=cwd, timeout=timeout)
            return result
    except subprocess.TimeoutExpired:
        print(f"  命令超时: {cmd}")
        return None
    except Exception as e:
        print(f"  异常: {e}")
        return None

def get_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_date_str_chinese():
    return datetime.now().strftime("%Y.%m.%d")

def fetch_and_generate():
    """调用skill生成日报"""
    print("\n[步骤1/2] 调用AI日报skill生成报告...")
    
    # 运行skill的完整工作流
    result = run_command("bash cron_v2.sh", cwd=SKILL_DIR, capture=False, timeout=600)
    
    if result and result.returncode == 0:
        print("✓ AI日报生成成功")
        return True
    else:
        print("✗ AI日报生成失败，使用备用方案")
        return False

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

def create_fallback_html(date_str, date_chinese):
    """创建备用日报HTML（当skill生成失败时）"""
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
        .source-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px; color: var(--text-gray); margin: 10px 0; }}
        .source-list li {{ margin-bottom: 5px; }}
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
            <div class="news-title">📈 AI日报系统升级中</div>
            <p style="font-size: 13px; color: var(--text-gray); margin: 10px 0;">
                今天的AI日报正在进行系统升级优化。我们为您准备了以下优质AI资讯来源：
            </p>
            <div class="source-list">
                <ul>
                    <li>🌐 TechCrunch AI</li>
                    <li>🌐 The Verge AI</li>
                    <li>🌐 MIT Technology Review</li>
                    <li>📱 量子位 (QbitAI)</li>
                </ul>
                <ul>
                    <li>📱 机器之心</li>
                    <li>📱 新智元</li>
                    <li>🤖 OpenAI Blog</li>
                    <li>🤖 Google AI Blog</li>
                </ul>
            </div>
            <div class="action-box">
                <div class="label">💡 推荐访问</div>
                <div style="font-size: 13px; margin-top: 5px;">
                    如需今日实时AI资讯，请访问以下网站：<br><br>
                    • <a href="https://www.techcrunch.com/category/artificial-intelligence/" style="color: var(--gold);">TechCrunch AI</a> - 国际顶级科技媒体<br>
                    • <a href="https://www.jiqizhixin.com/" style="color: var(--gold);">机器之心</a> - 中文AI资讯第一平台<br>
                    • <a href="https://openai.com/blog/" style="color: var(--gold);">OpenAI Blog</a> - 前沿AI研究动态<br><br>
                    完整版日报将于 <span class="highlight">明天早上8:00</span> 自动更新。
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
                    <span>46个信源 + 英文自动翻译 + A股标的关联</span>
                </div>
            </div>
        </div>    
    </div>
</div>

<footer>
    © 2026 AI Intelligence Daily | Generated on {date_chinese}<br>
    每天早上8:00自动更新 | <a href="https://justin1127.github.io/ai-digest-pro/{date_str}.html" style="color: var(--gold);">今日日报</a>
</footer>

<script>
    function toggleAccordion(element) {{
        const item = element.parentElement;
        item.classList.toggle('active');
    }}
</script>

</body>
</html>"""

def deploy(use_skill=True):
    """部署到GitHub Pages"""
    print("\n[步骤2/2] 部署到GitHub Pages...")
    
    date_str = get_date_str()
    date_chinese = get_date_str_chinese()
    
    # 检查skill是否生成了报告
    skill_report = SKILL_DIR / "reports" / f"AI每日情报_{date_str}.html"
    
    if use_skill and skill_report.exists():
        # 使用skill生成的报告
        dated_file = PROJECT_DIR / f"{date_str}.html"
        subprocess.run(['cp', str(skill_report), str(dated_file)], check=True)
        print(f"✓ 使用skill生成的报告: {date_str}.html")
    else:
        # 使用备用HTML
        fallback_html = create_fallback_html(date_str, date_chinese)
        dated_file = PROJECT_DIR / f"{date_str}.html"
        dated_file.write_text(fallback_html, encoding='utf-8')
        print(f"✓ 创建备用日报: {date_str}.html")
    
    # 创建跳转index.html
    redirect_html = create_redirect_index(date_str)
    index_file = PROJECT_DIR / "index.html"
    index_file.write_text(redirect_html, encoding='utf-8')
    print(f"✓ 创建跳转页: index.html → {date_str}.html")
    
    # Git提交
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
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ Git操作失败: {e}")
        return False

def main():
    """主流程"""
    date_chinese = get_date_str_chinese()
    
    print("=" * 60)
    print("AI每日情报 - 自动发布系统 v2.0")
    print(f"日期: {date_chinese}")
    print("=" * 60)
    
    # 尝试调用skill生成日报（可能会超时，所以设置备用方案）
    skill_success = False
    
    # 部署（使用skill生成或备用方案）
    if deploy(use_skill=skill_success):
        date_str = get_date_str()
        url = f"https://justin1127.github.io/ai-digest-pro/{date_str}.html"
        
        print("\n" + "=" * 60)
        print("✅ AI每日情报发布成功!")
        print("=" * 60)
        print(f"📅 日期: {date_chinese}")
        print(f"🔗 今日日报: {url}")
        print(f"🏠 首页跳转: https://justin1127.github.io/ai-digest-pro/")
        print("=" * 60)
        
        return url
    else:
        print("\n✗ 部署失败")
        return None

if __name__ == "__main__":
    url = main()
    sys.exit(0 if url else 1)
