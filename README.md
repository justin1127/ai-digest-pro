# AI日报系统 - 极简架构 v5.0

## 核心设计原则
1. **单一脚本**: 只有 `generate.py`，没有其他依赖
2. **内容保底**: RSS抓取失败时，使用AI搜索/手动整理的新闻
3. **定时触发**: OpenClaw每天早上8点触发，我负责执行和更新内容
4. **零外部依赖**: 不依赖不稳定的RSS服务

## 工作流程

### 每天早上8:00
1. OpenClaw定时任务触发 `cron:ai-digest-generate`
2. 我收到通知，主动抓取今日AI热点
3. 更新 `TODAY_NEWS` 变量
4. 运行 `python3 generate.py`
5. 推送到GitHub

### 如果GitHub推送失败
- 文件已保存在本地
- 手动上传或稍后重试

## 文件结构
```
ai-digest-pro/
├── generate.py      # 唯一脚本，包含新闻+生成+推送
├── 2026-03-06.html  # 每日日报（带日期）
└── index.html       # 自动跳转页
```

## 访问地址
- 首页: https://justin1127.github.io/ai-digest-pro/
- 今日: https://justin1127.github.io/ai-digest-pro/2026-03-06.html
