#!/usr/bin/env python3
"""
密码管理工具 - 查看/管理所有订阅用户
用法: python3 manage_passwords.py
"""

from datetime import datetime
from pathlib import Path

def load_subscribers():
    """加载所有订阅者信息"""
    subscribers_file = Path(__file__).parent / "subscribers.ini"
    
    if not subscribers_file.exists():
        print("❌ 未找到 subscribers.ini 文件")
        return []
    
    content = subscribers_file.read_text(encoding='utf-8')
    today = datetime.now().strftime("%Y-%m-%d")
    subscribers = []
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        if '=' in line:
            parts = line.split('=', 1)
            password = parts[0].strip()
            info = parts[1].strip()
            info_parts = info.split('|')
            
            if len(info_parts) >= 5:
                expiry = info_parts[3].strip()
                status = "✅ 有效" if expiry >= today else "❌ 已过期"
                
                subscribers.append({
                    'password': password,
                    'name': info_parts[0],
                    'wechat': info_parts[1],
                    'type': info_parts[2],
                    'expiry': expiry,
                    'state': info_parts[4],
                    'status': status
                })
    
    return subscribers

def main():
    print("=" * 80)
    print("🤖 AI决策情报 - 订阅用户管理")
    print("=" * 80)
    
    subscribers = load_subscribers()
    
    if not subscribers:
        print("\n暂无订阅用户")
        return
    
    # 统计
    valid_count = sum(1 for s in subscribers if "有效" in s['status'])
    expired_count = len(subscribers) - valid_count
    
    print(f"\n📊 统计: 总计 {len(subscribers)} 人 | ✅ 有效 {valid_count} 人 | ❌ 过期 {expired_count} 人")
    print("-" * 80)
    
    # 打印用户列表
    print(f"\n{'密码':<18} {'姓名':<10} {'微信':<15} {'类型':<8} {'有效期':<12} {'状态':<8}")
    print("-" * 80)
    
    for s in subscribers:
        print(f"{s['password']:<18} {s['name']:<10} {s['wechat']:<15} {s['type']:<8} {s['expiry']:<12} {s['status']:<8}")
    
    print("-" * 80)
    print("\n💡 操作提示:")
    print("   1. 添加新用户: python3 generate_password.py")
    print("   2. 编辑用户信息: 直接修改 subscribers.ini 文件")
    print("   3. 删除用户: 在 subscribers.ini 中删除对应行")
    print("   4. 生成日报: python3 generate.py")
    print("=" * 80)

if __name__ == "__main__":
    main()
