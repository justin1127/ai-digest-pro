#!/usr/bin/env python3
"""
AI日报完整发布流程
生成HTML → 创建飞书文档 → 推送链接给用户
通过OpenClaw agent执行（支持Feishu工具调用）
"""

import sys
import os
import re
import json
from datetime import datetime

# 路径配置
WORKSPACE = '/Users/maxjustin/.openclaw/workspace'
DIGEST_DIR = f'{WORKSPACE}/ai-digest-pro'

def extract_news_from_html(html_file):
    """从HTML中提取新闻内容"""
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()
    
    news_items = []
    
    # 匹配新闻条目
    pattern = r'<div class="news-item">.*?<span class="tag">(.*?)</span>.*?<h3>(.*?)</h3>.*?<p class="meta">(.*?)</p>.*?<p class="summary">(.*?)</p>.*?<a href="(.*?)"'
    matches = re.findall(pattern, html, re.DOTALL)
    
    for tag, title, meta, summary, link in matches:
        news_items.append({
            'tag': tag.strip(),
            'title': title.strip(),
            'meta': meta.strip(),
            'summary': summary.strip(),
            'link': link.strip()
        })
    
    return news_items

def format_doc_content(news_items, date_str, display_date):
    """格式化文档内容"""
    lines = [
        f"# 🤖 AI日报 | {display_date}",
        "",
        f"📅 **日期**: {display_date} | 📰 **{len(news_items)}条动态**",
        "",
        "---",
        ""
    ]
    
    for item in news_items:
        lines.extend([
            f"## 🏷️ {item['tag']} | {item['title']}",
            "",
            f"**{item['meta']}**",
            "",
            item['summary'],
            "",
            f"🔗 [阅读原文]({item['link']})",
            "",
            "---",
            ""
        ])
    
    lines.extend([
        "",
        f"*© {datetime.now().year} AI日报 | 每天早上8:00更新*",
        "",
        f"*GitHub Pages: https://justin1127.github.io/ai-digest-pro/{date_str}.html*"
    ])
    
    return "\n".join(lines)

def generate_html_digest():
    """执行HTML日报生成"""
    import subprocess
    result = subprocess.run(
        ['python3', 'generate.py'],
        cwd=DIGEST_DIR,
        capture_output=True,
        text=True
    )
    return result.returncode == 0, result.stdout + result.stderr

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    display_date = datetime.now().strftime('%Y.%m.%d')
    html_file = f'{DIGEST_DIR}/{date_str}.html'
    
    print(f"🤖 AI日报发布流程启动 - {display_date}")
    print("=" * 50)
    
    # 步骤1: 生成HTML
    print("\n📰 步骤1: 生成HTML日报...")
    success, output = generate_html_digest()
    if not success:
        print(f"❌ HTML生成失败: {output}")
        return False
    print("✅ HTML生成成功")
    
    # 步骤2: 提取内容
    print("\n📄 步骤2: 提取新闻内容...")
    news_items = extract_news_from_html(html_file)
    if not news_items:
        print("⚠️ 未找到新闻内容")
        return False
    print(f"✅ 提取到 {len(news_items)} 条新闻")
    
    # 步骤3: 格式化内容
    print("\n📝 步骤3: 格式化飞书文档内容...")
    doc_content = format_doc_content(news_items, date_str, display_date)
    
    # 保存内容供OpenClaw使用
    state_file = f'{DIGEST_DIR}/.publish_state.json'
    state = {
        'date': date_str,
        'display_date': display_date,
        'news_count': len(news_items),
        'content': doc_content,
        'status': 'ready_for_feishu'
    }
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 内容已保存到状态文件")
    print(f"📍 {state_file}")
    
    print("\n" + "=" * 50)
    print("🎯 下一步: 由OpenClaw agent创建飞书文档")
    print("📎 系统将在下次heartbeat时自动处理")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)