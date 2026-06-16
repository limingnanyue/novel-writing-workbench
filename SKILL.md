---
name: novel-writing-workbench
description: >
  InkOS Studio v6.6 —— 100% InkOS UI faithful reproduction (Narcooo/inkos).
  纯AI写作工作台（无LLM网关管理），零依赖单文件前端+FastAPI后端。
  4Tab导航(⌘工作台/💬对话/🔌模型/⚙️设置) + InkOS oklch配色系统(暖纸/黑曜石双主题) +
  3层字体(Instrument Serif/DM Sans/JetBrains Mono) + SVG噪点纹理 +
  8动作交错入场动画 + 毛玻璃侧边栏(260px) + CSS Grid 0fr→1fr折叠 +
  SSE流式AI对话 + 实时Token计数器(⚡) + 模型配置(余额/用量百分比/进度条) +
  书籍管理/章节/角色/大纲/记忆台账 + 移动端底部3Tab + 桌面端侧边栏布局。
  InkOS设计参考：https://github.com/Narcooo/inkos。
triggers:
  - InkOS
  - 写作工作台
  - AI写作
  - 模型配置
  - 余额查询
  - 实时Token
  - SSE流式
  - 流式对话
version: 6.6
last_updated: 2026-06-16
---

# InkOS Studio v6.6 🖋️

> **100% InkOS UI · SSE流式对话 · 实时Token · 模型余额管理**

## 快速启动

```bash
cd /home/agentuser/.hermes/skills/novel-writing-workbench
pip install fastapi uvicorn
python3 server.py
# → http://localhost:8080
```

环境变量：`HOST`(默认0.0.0.0) `PORT`(默认8080) `DATA_DIR`(默认./data)

## 核心功能

| Tab | 功能 |
|:----|:-----|
| ⌘ **工作台** | 书籍网格(paper-sheet卡片) + 创作入口2x8网格 + 书架 + 写作进度(Manuscript Foundry) |
| 💬 **对话** | SSE流式AI对话 + 实时Token计数器(⚡N递增) + 快捷指令 + 模型选择 + 自动保存章节 |
| 🔌 **模型** | 模型列表 + 余额显示(用量百分比+进度条) + 添加/删除 |
| ⚙️ **设置** | 模型配置(名称/地址/Key/ID/额度) + 系统设置 + 关于 |

## 设计系统 (InkOS faithful)

| 元素 | 亮色(默认) | 暗色(.dark) |
|:-----|:----------|:-----------|
| 背景 | oklch(0.985 0.005 80) 暖纸 | oklch(0.12 0.01 250) 黑曜石 |
| 前景 | oklch(0.13 0.02 60) 深墨 | oklch(0.97 0.005 250) 白 |
| 主色 | oklch(0.45 0.12 25) 赭红 | oklch(0.78 0.14 85) 暖琥珀 |
| 卡片 | oklch(1 0 0) 白 | oklch(0.18 0.015 250) |

- **3层字体**: Instrument Serif(内容) / DM Sans(UI) / JetBrains Mono(数据)
- **噪点纹理**: body::before SVG filter, opacity 0.025-0.035
- **毛玻璃**: backdrop-filter: blur(12px) on sidebar
- **动画**: staggerIn(8项交错) / msgSlideLeft/Right / thinkGlow / typingWave / blinky

## SSE 流式对话

```python
POST /api/chat/stream → SSE events:
  data: {"type":"token","content":"...","tokens":N}  # 每个token触发
  data: {"type":"done","content":"...","tokens":N}   # 完成
  data: {"type":"error","content":"..."}              # 错误
  data: [DONE]                                        # 流结束
```

前端使用 `fetch + Response.body.getReader()` + `TextDecoder("utf-8", {stream:true})` 逐 token 渲染。

## API 端点

| 端点 | 方法 | 说明 |
|:-----|:-----|:------|
| `/api/health` | GET | 健康检查 |
| `/api/models` | GET/POST/DELETE | 模型配置CRUD(名称/地址/Key/ID/额度) |
| `/api/chat` | POST | 一次性聊天 |
| `/api/chat/stream` | POST | SSE流式聊天(实时token) |
| `/api/writing/books` | GET/POST | 书籍列表/创建 |
| `/api/writing/books/{id}` | GET/DELETE | 获取/删除 |
| `/api/writing/books/{id}/chapters` | GET/POST | 章节列表/创建 |
| `/api/writing/books/{id}/chapters/{cid}` | GET/DELETE | 获取/删除章节 |
| `/api/writing/books/{id}/characters` | POST | 保存角色 |
| `/api/writing/books/{id}/outline` | POST | 保存大纲 |

## 文件结构

```
novel-writing-workbench/
  server.py          ~395行 — FastAPI(SSE流式+写作API+模型CRUD)
  static/
    index.html       ~67KB — 完整SPA(InkOS UI, 1656行CSS+HTML+JS内联)
    sw.js            PWA Service Worker
    manifest.json    PWA配置
  data/              运行时数据(models.json + writing/{book_id}/ 书籍/章节/角色/大纲)
  SKILL.md           本技能定义
```

## 陷阱

- **SSE需要ReadableStream**: 前端用 `resp.body.getReader()` 流式读取，不支持老旧浏览器
- **版本号散落**: index.html(title/sidebar/about) + server.py(docstring/print) 需同步更新
- **模型Key安全**: GET /api/models 不返回 api_key，仅返回 has_key: true/false
- **端口占用**: 重启前 pkill -f "python3 server.py"
- **数据目录**: data/ 已加入 .gitignore，不提交运行时数据
