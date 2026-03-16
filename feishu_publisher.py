#!/usr/bin/env python3
"""
AI日报飞书发布器
读取生成的HTML日报内容，创建飞书文档并获取链接
"""

import sys
import re
import json
from datetime import datetime

sys.path.insert(0, '/Users/maxjustin/.openclaw/workspace')

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

def format_doc_content(news_items, date_str):
    """格式化文档内容"""
    lines = [
        f"# 🤖 AI日报 | {date_str}",
        "",
        f"📅 **日期**: {date_str} | 📰 **{len(news_items)}条动态**",
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
        f"*© {datetime.now().year} AI日报 | 每天早上8:00更新*"
    ])
    
    return "\n".join(lines)

def main():
    date_str = datetime.now().strftime('%Y-%m-%d')
    html_file = f'/Users/maxjustin/.openclaw/workspace/ai-digest-pro/{date_str}.html'
    
    try:
        # 提取新闻
        news_items = extract_news_from_html(html_file)
        if not news_items:
            print("⚠️ 未找到新闻内容")
            return
        
        # 格式化内容
        content = format_doc_content(news_items, date_str)
        
        # 输出到文件供后续使用
        output_file = f'/Users/maxjustin/.openclaw/workspace/ai-digest-pro/feishu_content_{date_str}.md'
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 内容已准备好: {output_file}")
        print(f"📰 共 {len(news_items)} 条新闻")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()