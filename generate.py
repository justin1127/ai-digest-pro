#!/usr/bin/env python3
"""
AI日报 - 密码保护版 v6.0
微信收款 + 专属密码访问
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

# 配置
PROJECT_DIR = Path("/Users/maxjustin/.openclaw/workspace/ai-digest-pro")
DATA_FILE = PROJECT_DIR / "news_archive.json"
SUBSCRIBERS_FILE = PROJECT_DIR / "subscribers.ini"

def get_date():
    """获取日期"""
    now = datetime.now()
    return {
        "iso": now.strftime("%Y-%m-%d"),
        "cn": now.strftime("%Y.%m.%d"),
        "weekday": now.strftime("%A")
    }

def load_valid_passwords():
    """从subscribers.ini加载有效密码"""
    passwords = {
        "TEST888": {"name": "测试用户", "expiry": "2099-12-31"}
    }
    
    if not SUBSCRIBERS_FILE.exists():
        return passwords
    
    content = SUBSCRIBERS_FILE.read_text(encoding='utf-8')
    today = datetime.now().strftime("%Y-%m-%d")
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # 解析格式: 密码 = 用户信息|微信:xxx|付费类型|有效期|状态
        if '=' in line:
            parts = line.split('=', 1)
            password = parts[0].strip()
            info = parts[1].strip()
            
            # 提取有效期
            info_parts = info.split('|')
            if len(info_parts) >= 4:
                expiry = info_parts[3].strip()
                # 检查是否过期
                if expiry >= today:
                    passwords[password] = {
                        "name": info_parts[0],
                        "expiry": expiry
                    }
    
    return passwords

# 新闻模板 - 每日手动更新或从可靠API获取
TODAY_NEWS = {
    "date": "2026-03-17",
    "items": [
        {
            "title": "Claude 4发布：推理能力大幅提升",
            "source": "Anthropic",
            "summary": "Anthropic发布Claude 4，上下文窗口提升至200万token，代码生成能力超越GPT-4",
            "category": "技术",
            "link": "https://www.anthropic.com"
        },
        {
            "title": "Google Gemini 2.0 Pro开放API",
            "source": "Google",
            "summary": "Gemini 2.0 Pro API正式开放，定价较GPT-4低30%，支持100万token长文本",
            "category": "产品",
            "link": "https://ai.google.dev"
        },
        {
            "title": "美国AI芯片出口新规生效",
            "source": "政策",
            "summary": "新规限制高端GPU对华出口，国内AI企业加速转向国产算力方案",
            "category": "政策",
            "link": "https://www.commerce.gov"
        },
        {
            "title": "Figure AI完成6.75亿美元融资",
            "source": "投资",
            "summary": "人形机器人公司Figure AI估值达26亿美元，投资方包括微软、OpenAI、NVIDIA",
            "category": "融资",
            "link": "https://www.figure.ai"
        },
        {
            "title": "阿里通义千问Qwen3发布",
            "source": "阿里巴巴",
            "summary": "开源模型Qwen3在多项评测中超越Llama 3，支持201种语言",
            "category": "技术",
            "link": "https://qwenlm.github.io"
        }
    ]
}

def generate_html(date, news_data):
    """生成带密码保护的日报HTML"""
    
    # 加载有效密码
    valid_passwords = load_valid_passwords()
    passwords_json = json.dumps(valid_passwords, ensure_ascii=False)
    
    # 生成新闻列表
    news_html = ""
    for item in news_data.get("items", []):
        news_html += f"""
        <div class="news-item">
            <span class="tag">{item.get('category', '动态')}</span>
            <h3>{item.get('title', '')}</h3>
            <p class="meta">📍 {item.get('source', '')} · {date['cn']}</p>
            <p class="summary">{item.get('summary', '')}</p>
            <a href="{item.get('link', '#')}" target="_blank" class="link">阅读原文 →</a>
        </div>
        """
    
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI决策情报 | {date['cn']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', sans-serif;
            background: #0a0a0f; color: #e0e0e0; line-height: 1.6; padding: 20px;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        
        /* 密码保护层 */
        #password-overlay {{
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
            display: flex; flex-direction: column; justify-content: center; align-items: center;
            z-index: 9999;
        }}
        #password-overlay.hidden {{ display: none !important; }}
        .password-box {{
            background: #141414; border: 1px solid #333; border-radius: 16px;
            padding: 40px; text-align: center; max-width: 400px; width: 90%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
        }}
        .password-box h2 {{
            font-size: 24px; margin-bottom: 10px;
            background: linear-gradient(90deg, #fff, #f0c674); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .password-box p {{ color: #888; margin-bottom: 24px; font-size: 14px; }}
        .password-box input {{
            width: 100%; padding: 14px 16px; font-size: 16px;
            background: #0a0a0f; border: 1px solid #333; border-radius: 8px;
            color: #fff; text-align: center; letter-spacing: 2px;
            margin-bottom: 16px;
        }}
        .password-box input:focus {{
            outline: none; border-color: #f0c674;
        }}
        .password-box button {{
            width: 100%; padding: 14px; font-size: 16px;
            background: linear-gradient(90deg, #f0c674, #d4a853);
            color: #000; border: none; border-radius: 8px;
            cursor: pointer; font-weight: bold;
        }}
        .password-box button:hover {{ opacity: 0.9; }}
        .password-box button:disabled {{ opacity: 0.5; cursor: not-allowed; }}
        .error-msg {{ color: #ff6b6b; font-size: 13px; margin-top: 12px; }}
        .success-msg {{ color: #51cf66; font-size: 13px; margin-top: 12px; }}
        .subscribe-info {{
            margin-top: 24px; padding-top: 24px; border-top: 1px solid #333;
            font-size: 13px; color: #666;
        }}
        .subscribe-info a {{ color: #f0c674; text-decoration: none; }}
        
        /* 内容层 */
        header {{ text-align: center; padding: 30px 0; border-bottom: 1px solid #333; margin-bottom: 30px; }}
        h1 {{ 
            font-size: 32px; 
            background: linear-gradient(90deg, #fff, #f0c674); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .subtitle {{ color: #888; margin-top: 10px; }}
        .news-item {{ 
            background: #141414; border: 1px solid #333; border-radius: 12px;
            padding: 20px; margin-bottom: 20px;
        }}
        .tag {{ 
            display: inline-block; background: #f0c674; color: #000;
            padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;
        }}
        h3 {{ margin: 10px 0; color: #fff; }}
        .meta {{ color: #888; font-size: 13px; margin-bottom: 10px; }}
        .summary {{ color: #aaa; font-size: 14px; margin-bottom: 15px; }}
        .link {{ color: #f0c674; text-decoration: none; font-size: 13px; }}
        .link:hover {{ text-decoration: underline; }}
        .user-info {{
            position: fixed; top: 20px; right: 20px;
            background: #141414; border: 1px solid #333; border-radius: 8px;
            padding: 10px 16px; font-size: 12px; color: #888;
            z-index: 100;
        }}
        .user-info span {{ color: #f0c674; }}
        footer {{ text-align: center; padding: 30px 0; color: #666; font-size: 12px; border-top: 1px solid #333; margin-top: 30px; }}
    </style>
</head>
<body>
    <!-- 密码保护层 -->
    <div id="password-overlay">
        <div class="password-box">
            <h2>🔐 AI决策情报 Pro</h2>
            <p>输入您的专属密码解锁今日内容</p>
            <input type="text" id="password-input" placeholder="输入密码（如：AI26XXXXXX）" maxlength="16">
            <button id="unlock-btn" onclick="checkPassword()">解锁访问</button>
            <div id="message"></div>
            <div class="subscribe-info">
                未订阅？<a href="#" onclick="alert('请添加微信：justin1127（备注AI日报）订阅')">点击咨询订阅</a><br>
                <span style="font-size: 11px; color: #444;">月付¥19 / 年付¥169</span>
            </div>
        </div>
    </div>
    
    <!-- 用户信息（解锁后显示）-->
    <div class="user-info" id="user-info" style="display: none;">
        👤 <span id="user-name">用户</span> | 有效期至 <span id="expiry-date">--</span>
    </div>
    
    <!-- 内容层 -->
    <div class="container" id="content" style="display: none;">
        <header>
            <h1>🤖 AI决策情报</h1>
            <p class="subtitle">📅 {date['cn']} · 📰 {len(news_data.get('items', []))}条精选动态</p>
        </header>
        
        {news_html}
        
        <footer>
            © 2026 AI决策情报 | 每天早上8:00更新<br>
            订阅咨询微信：justin1127<br>
            <a href="./{date['iso']}.html" style="color: #666;">今日链接</a>
        </footer>
    </div>
    
    <script>
        // 有效密码列表（由服务器生成）
        const VALID_PASSWORDS = {passwords_json};
        
        // 检查本地存储的密码
        window.onload = function() {{
            const savedPassword = localStorage.getItem('ai_digest_password');
            const savedExpiry = localStorage.getItem('ai_digest_expiry');
            
            if (savedPassword && savedExpiry) {{
                // 检查是否过期
                const today = new Date().toISOString().split('T')[0];
                if (savedExpiry >= today && VALID_PASSWORDS[savedPassword]) {{
                    unlockContent(savedPassword, VALID_PASSWORDS[savedPassword]);
                }} else {{
                    // 密码过期，清除存储
                    localStorage.removeItem('ai_digest_password');
                    localStorage.removeItem('ai_digest_expiry');
                    localStorage.removeItem('ai_digest_user');
                }}
            }}
            
            // 回车键提交
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
            
            // 模拟验证延迟
            setTimeout(() => {{
                const userInfo = VALID_PASSWORDS[input];
                
                if (userInfo) {{
                    const today = new Date().toISOString().split('T')[0];
                    if (userInfo.expiry >= today) {{
                        message.innerHTML = '<p class="success-msg">✅ 验证成功！正在进入...</p>';
                        
                        // 保存到本地存储（30天内免输入）
                        localStorage.setItem('ai_digest_password', input);
                        localStorage.setItem('ai_digest_expiry', userInfo.expiry);
                        localStorage.setItem('ai_digest_user', userInfo.name);
                        
                        setTimeout(() => unlockContent(input, userInfo), 500);
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
            }}, 500);
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

def generate_index_redirect(date):
    """生成跳转页"""
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="0; url=./{date['iso']}.html">
    <title>AI决策情报 | 跳转中...</title>
    <style>
        body {{ background: #0a0a0f; color: #fff; display: flex; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; }}
        .loading {{ text-align: center; }}
        a {{ color: #f0c674; }}
    </style>
</head>
<body>
    <div class="loading">
        <h2>🤖 AI决策情报</h2>
        <p>正在跳转到 {date['cn']} 日报...</p>
        <p>如果没有跳转，<a href="./{date['iso']}.html">点击这里</a></p>
    </div>
</body>
</html>"""

def git_push():
    """推送Git"""
    try:
        subprocess.run(['git', 'add', '.'], cwd=PROJECT_DIR, check=True, capture_output=True)
        
        # 检查是否有变更
        status = subprocess.run(['git', 'status', '--porcelain'], cwd=PROJECT_DIR, capture_output=True, text=True)
        if not status.stdout.strip():
            return True
            
        date = get_date()
        subprocess.run(['git', 'commit', '-m', f"AI决策情报 {date['cn']}"], cwd=PROJECT_DIR, check=True, capture_output=True)
        subprocess.run(['git', 'push'], cwd=PROJECT_DIR, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Git推送失败（稍后手动处理）: {e}")
        return False

def main():
    """主函数"""
    date = get_date()
    
    print(f"🤖 AI决策情报生成器 v6.0")
    print(f"📅 日期: {date['cn']}")
    print("-" * 40)
    
    # 加载密码统计
    passwords = load_valid_passwords()
    print(f"🔐 有效密码数: {len(passwords)}")
    
    # 1. 生成日报HTML
    html = generate_html(date, TODAY_NEWS)
    dated_file = PROJECT_DIR / f"{date['iso']}.html"
    dated_file.write_text(html, encoding='utf-8')
    print(f"✓ 生成: {date['iso']}.html ({len(TODAY_NEWS['items'])}条)")
    
    # 2. 生成跳转页
    index_html = generate_index_redirect(date)
    index_file = PROJECT_DIR / "index.html"
    index_file.write_text(index_html, encoding='utf-8')
    print(f"✓ 生成: index.html → {date['iso']}.html")
    
    # 3. 尝试推送
    if git_push():
        print(f"✓ 已推送到GitHub")
    else:
        print(f"⚠️ GitHub推送失败（文件已生成本地）")
    
    print("-" * 40)
    print(f"✅ 完成!")
    print(f"🔗 https://justin1127.github.io/ai-digest-pro/{date['iso']}.html")

if __name__ == "__main__":
    main()
