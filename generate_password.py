#!/usr/bin/env python3
"""
密码生成器 - 为付费用户生成专属访问密码
使用方法: python3 generate_password.py [用户姓名] [微信名] [付费类型]
示例: python3 generate_password.py 张三 zhangsan 月付
"""

import secrets
import sys
from datetime import datetime, timedelta
from pathlib import Path

def generate_password():
    """生成16位随机密码"""
    # 格式: AI + 年份(2位) + 10位随机字符
    year_short = datetime.now().strftime("%y")
    random_part = secrets.token_hex(5).upper()  # 10位十六进制
    return f"AI{year_short}{random_part}"

def calculate_expiry(pay_type):
    """计算密码有效期"""
    today = datetime.now()
    if pay_type == "月付":
        expiry = today + timedelta(days=30)
    elif pay_type == "季付":
        expiry = today + timedelta(days=90)
    elif pay_type == "年付":
        expiry = today + timedelta(days=365)
    elif pay_type == "永久":
        expiry = today + timedelta(days=3650)  # 10年
    else:
        expiry = today + timedelta(days=30)  # 默认月付
    return expiry.strftime("%Y-%m-%d")

def save_subscriber(password, name, wechat, pay_type, expiry):
    """保存订阅者信息到文件"""
    config_file = Path(__file__).parent / "subscribers.ini"
    
    # 读取现有内容
    if config_file.exists():
        content = config_file.read_text(encoding='utf-8')
    else:
        content = ""
    
    # 添加新用户记录
    record = f"{password} = {name}|微信:{wechat}|{pay_type}|{expiry}|active\n"
    
    # 在"正式付费用户"区域后添加
    marker = "# ============ 正式付费用户 ============"
    if marker in content:
        content = content.replace(marker, marker + "\n" + record)
    else:
        content += "\n" + record
    
    config_file.write_text(content, encoding='utf-8')
    return True

def main():
    print("=" * 50)
    print("🤖 AI日报 - 密码生成器")
    print("=" * 50)
    
    # 获取参数
    if len(sys.argv) >= 3:
        name = sys.argv[1]
        wechat = sys.argv[2]
        pay_type = sys.argv[3] if len(sys.argv) > 3 else "月付"
    else:
        # 交互式输入
        name = input("用户姓名: ").strip()
        wechat = input("微信名: ").strip()
        print("\n付费类型:")
        print("1. 月付 (30天)")
        print("2. 季付 (90天)")
        print("3. 年付 (365天)")
        print("4. 永久")
        choice = input("选择 (1-4, 默认1): ").strip() or "1"
        
        pay_type_map = {"1": "月付", "2": "季付", "3": "年付", "4": "永久"}
        pay_type = pay_type_map.get(choice, "月付")
    
    # 生成密码
    password = generate_password()
    expiry = calculate_expiry(pay_type)
    
    print("\n" + "-" * 50)
    print("✅ 密码生成成功！")
    print("-" * 50)
    print(f"🔐 专属密码: {password}")
    print(f"👤 用户姓名: {name}")
    print(f"💬 微信名称: {wechat}")
    print(f"💰 付费类型: {pay_type}")
    print(f"📅 有效期至: {expiry}")
    print("-" * 50)
    
    # 保存到文件
    if save_subscriber(password, name, wechat, pay_type, expiry):
        print("✅ 已保存到 subscribers.ini")
    
    # 输出发送话术
    print("\n" + "=" * 50)
    print("📱 微信发送话术（复制使用）:")
    print("=" * 50)
    print(f"""
🎉 感谢订阅 AI决策情报 Pro！

您的专属访问密码：{password}
有效期至：{expiry}

📖 阅读地址：https://justin1127.github.io/ai-digest-pro/

使用说明：
1. 点击链接进入日报页面
2. 输入专属密码即可解锁
3. 每天早上8:00更新，建议收藏链接

如有问题随时微信联系我～
""")
    print("=" * 50)

if __name__ == "__main__":
    main()
