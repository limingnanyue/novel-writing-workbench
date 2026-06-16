# InkOS Studio v6.0

> ✦ AI 写作工作台 · 模型余额管理 · 纯前端零依赖

[![Version](https://img.shields.io/badge/version-6.0-5c3a1e)](https://github.com/limingnanyue/novel-writing-workbench)
[![PWA](https://img.shields.io/badge/PWA-ready-36c073)]()
[![Zero Deps](https://img.shields.io/badge/frontend-zero_deps-36c073)]()

---

## 🎨 设计系统

InkOS 纸质文学氛围，100% 还原 Narcooo/inkos 的 UI 设计语言。

**配色（oklch 调色板）**

| 模式 | 背景 | 前景 | 主色 | 边框 |
|:--|:--|:--|:--|:--|
| ☀️ 亮色 | `0.985 0.005 80` 暖旧纸 | `0.13 0.02 60` 深墨水 | `0.45 0.12 25` 牛血 | `0.84 0.01 76` 纸纤维 |
| 🌙 暗色 | `0.12 0.01 250` 黑曜石 | `0.97 0.005` 浅灰 | `0.78 0.14 85` 琥珀 | `0.30 0.02 250` 深灰 |

**字体三层分级**
- `Instrument Serif` — 标题 / 文学内容
- `DM Sans` — UI 界面
- `JetBrains Mono` — 数据 / 日志

**纹理与质感**
- SVG 噪点纹理叠加（`mix-blend-mode: overlay`, `opacity: 0.025`）
- 毛玻璃侧边栏（`backdrop-filter: blur(12px)`）
- 纸张卡片（`.paper-sheet`）与玻璃面板（`.glass-panel`）

**11 种 CSS 动效**
`staggerIn` · `msgSlideRight` · `msgSlideLeft` · `thinkGlow` · `typingWave` · `fadeIn` · `iconPop` · `skel` · `pulse` · `ov-in` · `navIn`

---

## ⌨️ 页面结构

### 侧边栏（260px）

```
┌──────────────────┐
│ InkOS Logo       │  SVG: 深灰圆 + 橙色墨滴 + 金笔尖
├──────────────────┤
│ CREATION 2×4 网格 │  8 入口带交错入场动画
├──────────────────┤
│ 📖 我的书架       │  可折叠 · CSS Grid 0fr→1fr
├──────────────────┤
│ 📋 历史记录       │  最近会话列表
├──────────────────┤
│ SYSTEM           │
│  📦 模型余额      │  API 用量 / 剩余额度
│  ⚙️ 服务商         │
│  ⚙️ 项目设置       │
│  ⚡ Daemon        │
│  ⌨️ 日志           │
├──────────────────┤
│ TOOLS            │
│  🪄 风格 · 📥 导入 │
│  📈 雷达 · 🩺 诊断 │
├──────────────────┤
│ ● Agent online   │  绿色脉冲点
└──────────────────┘
```

### ⌘ 工作台

书籍网格（`.paper-sheet` 卡片），每张显示：
- 书名（Serif, h2）
- 题材标签
- 章节数 / 字数
- 状态圆点（草稿/进行中/已完成）
- 操作：[⚡写下一章] [📊统计] [⋮ 更多]

底部 **Manuscript Foundry** 玻璃面板：写作进度实时日志。

### 💬 对话

- 快捷操作栏：[⚡写下一章] [🔍审计] [📄导出] [📈市场雷达]
- 消息样式：用户右滑入 `msgSlideRight`，AI 左滑入 `msgSlideLeft`
- 思考状态呼吸发光 `thinkGlow`
- 输入：textarea + 发送按钮 + 模型选择器 + 书籍选择器

### ⚙️ 设置

- 📦 **模型余额管理**：添加 API 模型，显示总额度/已用量/剩余/过期
- ⚙️ **系统设置**：语言切换（中/EN）、主题切换（亮/暗）
- 📊 **存储管理**：清除本地数据
- 📖 **关于**：版本信息

---

## 📡 API 端点（17 个）

### 模型余额（3 个）

```
GET    /api/models            # 模型列表（含用量）
POST   /api/models            # 添加/更新模型
DELETE /api/models/{id}        # 删除模型
```

### 写作工作台（14 个）

```
GET    /api/writing/books              # 书籍列表
POST   /api/writing/books              # 创建新书
GET    /api/writing/books/{id}         # 书籍完整数据
DELETE /api/writing/books/{id}         # 删除书籍
GET    /api/writing/books/{id}/chapters          # 章节列表
POST   /api/writing/books/{id}/chapters          # 创建章节
GET    /api/writing/books/{id}/chapters/{cid}    # 获取章节
DELETE /api/writing/books/{id}/chapters/{cid}    # 删除章节
POST   /api/writing/books/{id}/characters       # 保存角色
POST   /api/writing/books/{id}/outline          # 保存大纲
```

---

## 🚀 快速开始

```bash
pip install fastapi uvicorn
python3 server.py
# → http://localhost:8080
```

环境变量：`HOST`（默认 `0.0.0.0`）、`PORT`（默认 `8080`）、`DATA_DIR`（默认 `./data`）

---

## 📦 技术栈

| 层 | 技术 |
|:--|:--|
| 后端 | Python · FastAPI · uvicorn |
| 前端 | 纯 HTML/CSS/JS（零依赖，单文件 67KB） |
| 存储 | JSON 文件系统（`data/writing/{book_id}/`） |
| 状态 | localStorage（`inkos_ws_data` 前缀） |

---

## 📜 版本历史

| 版本 | 说明 |
|:--|:--|
| **v6.0** | 纯 InkOS Studio 重制 — 删 LLM 网关，100% InkOS UI |
| v5.3 | LLM 网关 + InkOS 写作 + OpenWrite 方法论融合 |
| v5.2 | 网关 + AI 写作聊天 |
| v5.0 | LLM 模型管理仪表盘 |

---

## 📄 License

MIT
