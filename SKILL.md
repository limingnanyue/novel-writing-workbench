---
name: novel-writing-workbench
description: >
  LLM Gateway Dashboard v5.2 —— 移动优先+桌面响应式，零依赖模型管理面板。
  4Tab导航(仪表盘/模型/写作/设置) + 连接测试 + 余额查询(3级回退) + 模型列表缓存 +
  AI写作对话(5个快速指令+提供商切换+最后10条历史上下文) + Token统计 +
  桌面端三栏布局(侧栏220px+中栏340px+详情面板) + PWA(ServiceWorker+manifest)。
  taste-skill v2设计(DIALS 5/3/5·暗色奢华+电动蓝+终端美学)。
  对标：one-api/lobe-chat/InkOS。
triggers:
  - LLM管理
  - 模型管理
  - API管理
  - 网关面板
  - 启动面板
  - 工作台
  - AI写作
  - 写作对话
  - 测试连接
  - 余额查询
  - Token统计
  - 提供商管理
  - PWA
version: 5.2
last_updated: 2026-06-16
---

# LLM Gateway Dashboard v5.2 🔌

> **移动优先 + 桌面响应式 · 4Tab导航 · AI写作对话 · 连接测试 · 余额查询**

## 快速启动

```bash
cd /home/agentuser/.hermes/skills/novel-writing-workbench
fuser -k 8080/tcp 2>/dev/null; sleep 1
python3 server.py &
# → http://localhost:8080
```

环境变量：`HOST`(默认0.0.0.0) `PORT`(默认8080) `DATA_DIR`(默认./data)

## 核心功能

| Tab | 功能 |
|:----|:-----|
| ⌘ **仪表盘** | 统计卡片(提供商数/模型数/请求数) + 提供商列表 + 详情面板 |
| 🔌 **模型** | 添加/编辑/删除提供商 + 测试连接(调用/v1/models) + 余额查询(3级回退) + 模型标签预览 |
| ✍️ **写作** | AI对话 + 5个快速指令(写第1章/分析文风/起名/大纲/去AI味) + 提供商切换下拉 + 最后10条历史上下文 |
| ⚙️ **设置** | 提供商管理 + Token统计(按提供商请求数/消耗) + 重置 + 关于 |

| 特性 | 说明 |
|:-----|:-----|
| 📱 **移动端** | 4Tab底部导航 + 底部弹出层 + 手势滑动 |
| 🖥️ **桌面端** | ≥768px三栏布局(侧栏220px+中栏340px+详情面板)，≥1200px侧栏加宽至260px |
| 💰 **余额查询** | 3级回退：Billing API → Usage API → Test Call |
| 📦 **PWA** | Service Worker(cache-first) + manifest + 192/512图标 |
| 🎨 **设计** | 暗色奢华(#0a0a0f) + 电动蓝(#5b8af7) + JetBrains Mono终端美学 |

## 版本演进

**v5.0** 从写作工作台重构为LLM Gateway：去除全部写作功能，精简至3Tab
**v5.1** 添加桌面端响应式三栏布局
**v5.2** 写作Tab回归——AI对话写得比人好，砍了可惜

### 余额查询三级回退

1. **Billing API**: `GET /dashboard/billing/subscription` → OpenAI风格
2. **Usage API**: `GET /v1/usage?date=...` → 按天用量
3. **Test Call**: 最小对话调用验证额度可用

## UI 设计系统

**taste-skill v2 DIALS: 5/3/5**
- 底色 `#0a0a0f` → 层级递进 s1/s2/s3
- 电动蓝 `#5b8af7` 强调 + 算法绿 `#36c073` 成功态
- 120ms克制动效
- 终端美学：JetBrains Mono用于数据/标签，`> ` 前缀
- 安全区适配：`safe-area-inset-*`

## API 端点

| 端点 | 方法 | 说明 |
|:-----|:-----|:------|
| `/api/health` | GET | 健康检查（版本/提供商数/模型数/请求统计） |
| `/api/providers` | GET/POST | 列表/添加（隐藏api_key） |
| `/api/providers/{id}` | DELETE | 删除 |
| `/api/providers/{id}/test` | POST | 测试连接 + 获取模型列表 + 缓存 |
| `/api/providers/{id}/models` | GET | 缓存模型列表 |
| `/api/providers/{id}/balance` | POST | 余额查询（3级回退） |
| `/api/chat` | POST | AI写作对话（provider+model+message+history） |
| `/api/tokens` | GET | Token统计 |
| `/api/tokens/reset` | POST | 重置统计 |

## 文件结构

```
novel-writing-workbench/
  server.py          ~370行 — FastAPI所有端点（含Chat）
  static/
    index.html       ~22KB — 完整SPA(CSS+JS内联，4Tab+桌面三栏)
    sw.js            PWA Service Worker
    manifest.json    PWA配置
    assets/          PWA icons (192+512)
  data/              提供商/Token数据(providers.json+tokens.json)
  references/        设计模式参考
```

## 陷阱

- **端口占用**：重启前 `fuser -k 8080/tcp`
- **api_key安全**：`GET /api/providers` 不返回 key，仅返回 `has_key: true/false`
- **HTML热更新**：修改 index.html 无需重启服务器
- **余额查询不支持所有提供商**：三级回退全部失败返回 `source: "none"`
- **版本号散落6处**：更新版本时需修改 index.html(title/hero/sidebar/about) + server.py(docstring/print) —— 漏一处就有残留旧版本号
- **Git无历史**：此仓库经历多次`git init`重置，推送时可能需要`--force`
- **GitHub直连被墙**：推送用GitHub API + token，不走git协议
