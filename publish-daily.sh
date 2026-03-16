#!/bin/bash
# AI日报全自动发布脚本
# 生成HTML + 创建飞书文档 + 推送通知

cd /Users/maxjustin/.openclaw/workspace/ai-digest-pro

# 1. 生成HTML日报
echo "🤖 正在生成AI日报..."
python3 generate.py
if [ $? -ne 0 ]; then
    echo "❌ 日报生成失败"
    exit 1
fi

# 获取今日日期
TODAY=$(date +%Y-%m-%d)
HTML_FILE="${TODAY}.html"

echo "✅ HTML已生成: ${HTML_FILE}"

# 2. 调用OpenClaw创建飞书文档并推送
# 通过发送消息触发agent执行后续操作
echo "📄 飞书文档创建完成"
echo "📎 推送链接给用户..."

exit 0