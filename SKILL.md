---
name: novel-writing-workbench
description: >
  小说写作工作台 v4.5 —— 移动优先Web应用。5Tab导航(工作台/对话/写作/书籍/设置) + 手势滑动 +
  6风格封面生成(现代/古典/暗黑/极简/海报/插画) + InkOS AI封面提示词 + 市场扫榜(起点/番茄/飞卢/晋江) +
  对话式AI写作(ChatPage消息气泡+快捷操作) + 开书推倒(5维评分+平台推荐) +
  文风分析(句长/AI标记) + AI写作代理(8题材+规则注入+Token追踪) +
  自定义AI提供商 + 多Agent路由 + PWA + 底部弹出层(替代模态框)。
  taste-skill v2重设计(DIALS 5/3/5·Anti-Default·Restrained Motion·Brief Inference)。
  对标项目：InkOS/oh-story-claudecode/chinese-novelist-skill/feinetcui。
triggers:
  - 工作台
  - web写作
  - 启动工作台
  - 写作工具
  - 封面生成
  - 设计封面
  - 生成封面
  - 扫榜
  - 市场扫榜
  - 市场雷达
  - Token统计
  - 自定义AI
  - 写作分析
  - 书籍管理
  - 开书推倒
  - 推倒
  - 评估开篇
  - AI写作
  - 手机写作
  - PWA
  - 底部弹出层
version: 4.5
last_updated: 2026-06-16
---

# LLM Gateway Dashboard v5.0 🔌

> **移动优先 · 3Tab导航 · 连接测试 · 余额查询 · 模型列表**

## 快速启动

```bash
cd /home/agentuser/.hermes/skills/novel-writing-workbench
fuser -k 8080/tcp 2>/dev/null; sleep 1
python3 server.py &
# → http://localhost:8080
```

环境变量：`HOST`(默认0.0.0.0) `PORT`(默认8080) `DATA_DIR`(默认./data)

## 核心功能

| 功能 | v5.0 |
|:-----|:-----|
| 🔌 **多提供商管理** | 添加/编辑/删除 OpenAI 兼容 API 提供商 |
| 🔍 **连接测试** | 调用 `/v1/models` 获取模型列表，过滤非文本模型 |
| 💰 **余额查询** | 3级回退策略：Billing API → Usage API → Test Call |
| 📋 **模型列表** | 测试后缓存模型列表，展示模型ID和归属 |
| 📊 **Token追踪** | 按提供商统计请求数/Token消耗/测试次数 |
| 📱 **移动端** | 3Tab底部导航 + 底部弹出层 + 手势滑动 |
| 📦 **PWA** | Service Worker(cache-first) + manifest + 192/512图标 |

## v5.0 重构（鲁班打磨）

**从写作工作台 → LLM模型管理面板**

- **验料**：定位调整为"手机上的LLM API管理面板"
- **访行**：对标 one-api(35K星)/lobe-chat/LLM-API-Key-Proxy
- **慢刨**：去除全部写作功能（chat/editor/books/evaluate），精简 server.py 从1336行→290行
- **新增**：连接测试 + 余额查询(3级回退) + 模型列表缓存
- **回炉**：3Tab UI重设计（仪表盘/模型/设置）

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
| `/api/chat` | POST | 测试对话 |
| `/api/tokens` | GET | Token统计 |
| `/api/tokens/reset` | POST | 重置统计 |

## 文件结构

```
novel-writing-workbench/
  server.py          290行 — FastAPI所有端点
  static/
    index.html       21KB — 完整SPA(CSS+JS内联)
    sw.js            PWA Service Worker
    manifest.json    PWA配置
    assets/          PWA icons
  data/              提供商/Token数据
  references/        设计模式参考
```

## 陷阱

- **端口占用**：重启前 `fuser -k 8080/tcp`
- **api_key安全**：`GET /api/providers` 不返回 key，仅返回 `has_key: true/false`
- **HTML热更新**：修改 index.html 无需重启
- **余额查询不支持所有提供商**：三级回退全部失败返回 `source: "none"`
