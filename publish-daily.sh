#!/bin/bash
# AI日报全自动发布脚本
# 生成HTML + 推送到GitHub Pages

cd "$(dirname "$0")"

# 1. 生成HTML日报
echo "🤖 正在生成AI日报..."
python3 generate.py --fetch --limit 5 --push
if [ $? -ne 0 ]; then
    echo "❌ 日报生成失败"
    exit 1
fi

# 获取今日日期
TODAY=$(date +%Y-%m-%d)
HTML_FILE="${TODAY}.html"

echo "✅ HTML已生成: ${HTML_FILE}"
echo "🔗 https://justin1127.github.io/ai-digest-pro/${HTML_FILE}"

exit 0
