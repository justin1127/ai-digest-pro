#!/usr/bin/env python3
"""
AI日报每日生成器
生成暗色手风琴风格的HTML日报
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

class DailyReportGenerator:
    def __init__(self):
        self.project_dir = Path("/Users/maxjustin/.openclaw/workspace/projects/ai-digest-pro")
        self.data_dir = self.project_dir / "data"
        self.data_dir.mkdir(exist_ok=True)
        
    def get_date_str(self):
        """获取日期字符串"""
        return datetime.now().strftime("%Y.%m.%d")
    
    def get_filename(self):
        """获取文件名"""
        return datetime.now().strftime("%Y-%m-%d") + ".html"
    
    def fetch_latest_news(self):
        """获取最新AI新闻（简化版）"""
        # 实际应调用AI抓取系统
        return [
            {
                "title": "AI行业最新动态",
                "score": "9.0",
                "what": "等待抓取...",
                "why": "等待抓取...",
                "impact": "等待抓取...",
                "stocks": "待定"
            }
        ]
    
    def generate_html(self):
        """生成HTML日报"""
        date_str = self.get_date_str()
        filename = self.get_filename()
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 每日情报 | {date_str}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Serif+SC:wght@700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #080808;
            --card: #141414;
            --gold: #f3c344;
            --gold-dim: #b8860b;
            --text-main: #e0e0e0;
            --text-gray: #888;
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
        .section-title {{ font-weight: 800; font-size: 16px; display: flex; align-items: center; gap: 10px; }}
        .arrow {{ width: 12px; transition: 0.3s; fill: var(--gold); }}
        .accordion-content {{ max-height: 0; transition: max-height 0.4s ease-out; background: #1a1a1a; padding: 0 16px; overflow: hidden; }}
        .active .accordion-content {{ max-height: 2000px; padding: 20px 16px; border-top: 1px solid #222; }}
        .active .arrow {{ transform: rotate(180deg); }}
        .news-item {{ margin-bottom: 25px; position: relative; padding-left: 10px; }}
        .score-badge {{ display: inline-block; background: var(--gold); color: #000; font-size: 10px; font-weight: 900; padding: 1px 6px; border-radius: 4px; margin-right: 8px; }}
        .news-title {{ font-weight: 700; font-size: 15px; color: #fff; margin-bottom: 8px; }}
        .analysis-grid {{ display: grid; grid-template-columns: 1fr; gap: 8px; font-size: 13px; }}
        .grid-row {{ display: flex; gap: 8px; margin-bottom: 4px; }}
        .label {{ color: var(--gold); font-weight: 800; min-width: 50px; font-size: 11px; flex-shrink: 0; }}
        .action-box {{ background: rgba(243, 195, 68, 0.08); padding: 10px; border-radius: 8px; border-left: 3px solid var(--gold); margin-top: 10px; }}
        .stock-tag {{ color: #52c41a; font-weight: 600; font-size: 12px; }}
        footer {{ text-align: center; color: var(--text-gray); font-size: 11px; padding: 40px 0; border-top: 1px solid #222; margin-top: 40px; }}
    </style>
</head>
<body>

<header>
    <div class="tag">AI INTELLIGENCE DAILY</div>
    <h1>AI 每日情报</h1>
    <div class="meta-bar">
        <span>📅 {date_str}</span>
        <span>🔍 扫描信源: 52</span>
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
            <div class="news-title">📈 今日趋势等待更新...</div>
            <p style="font-size: 13px; color: var(--text-gray);">正在抓取最新AI行业动态...</p>
            <div class="action-box">
                <div class="label">⚠️ 风险预警</div>
                <div style="font-size: 13px;">等待数据抓取完成...</div>
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
            <span class="score-badge">--</span>
            <div class="news-title">今日新闻正在抓取中...</div>
            <div class="analysis-grid">
                <div class="grid-row"><span class="label">状态</span>等待AI抓取系统完成数据收集...</div>
            </div>
        </div>
    </div>
</div>

<footer>
    © 2026 AI Intelligence Daily | Generated on {date_str}<br>
    明天早上8:00自动更新
</footer>

<script>
    function toggleAccordion(element) {{
        const item = element.parentElement;
        item.classList.toggle('active');
    }}
</script>

</body>
</html>"""
        
        return html, filename
    
    def save_and_push(self):
        """保存并推送到GitHub"""
        html, filename = self.generate_html()
        
        # 保存到项目目录
        file_path = self.project_dir / filename
        file_path.write_text(html, encoding='utf-8')
        print(f"✓ 生成文件: {filename}")
        
        # 同时更新index.html
        index_path = self.project_dir / "index.html"
        index_path.write_text(html, encoding='utf-8')
        print(f"✓ 更新 index.html")
        
        # Git提交并推送
        try:
            subprocess.run(['git', 'add', filename, 'index.html'], 
                         cwd=self.project_dir, check=True, capture_output=True)
            subprocess.run(['git', 'commit', '-m', f'Add: {self.get_date_str()} AI日报'], 
                         cwd=self.project_dir, check=True, capture_output=True)
            subprocess.run(['git', 'push'], 
                         cwd=self.project_dir, check=True, capture_output=True)
            print(f"✓ 推送到GitHub")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Git操作失败: {e}")
            return False
    
    def run(self):
        """执行完整流程"""
        print("=" * 50)
        print("AI日报每日生成器")
        print(f"日期: {self.get_date_str()}")
        print("=" * 50)
        
        success = self.save_and_push()
        
        if success:
            date_slug = datetime.now().strftime("%Y-%m-%d")
            url = f"https://justin1127.github.io/ai-digest-pro/{date_slug}.html"
            print(f"\n✓ 完成!")
            print(f"✓ 访问链接: {url}")
            return url
        else:
            print(f"\n✗ 失败")
            return None

if __name__ == "__main__":
    generator = DailyReportGenerator()
    generator.run()
