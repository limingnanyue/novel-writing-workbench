# LLM Gateway Dashboard v5.0

> 📱 手机上的 LLM 模型管理面板 —— 测试连接、查余额、管模型。

[![Version](https://img.shields.io/badge/version-5.0-5b8af7)](https://github.com/limingnanyue/novel-writing-workbench)
[![PWA](https://img.shields.io/badge/PWA-ready-36c073)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)

**3Tab 移动端仪表盘 · 暗色奢华 · 终端美学 · 零依赖前端**

管理你的 LLM API 提供商：添加 provider → 测试连接拉取模型列表 → 查余额 → 统计用量。

## 功能

| 功能 | 说明 |
|:--|:--|
| 🔌 **提供商管理** | 添加/删除 OpenAI 兼容 API |
| 🔍 **连接测试** | 调用 `/models` 拉取可用模型列表 |
| 💰 **余额查询** | 支持 billing API / 测试调用 两种方式 |
| 📊 **用量统计** | Token 消耗、请求次数、测试次数 |
| 📱 **PWA** | 添加到主屏幕，离线缓存 |

## 快速开始

```bash
pip install fastapi uvicorn
python3 server.py
# → http://localhost:8080
```

## 设计

- **taste-skill v2 DIALS (5/3/5)** — 暗色 `#0a0a0f` + 电动蓝 `#5b8af7`
- **3 Tab** — ⌘仪表盘 / 🔌模型 / ⚙️设置
- **底部弹出层** — 提供商详情、添加表单
- **终端美学** — JetBrains Mono，`> ` 前缀
- **零依赖前端** — 纯 HTML/CSS/JS，单文件 21KB

## API

```
GET  /api/health                     # 健康检查 + 统计
GET  /api/providers                  # 提供商列表
POST /api/providers                  # 添加提供商
DELETE /api/providers/:id            # 删除
POST /api/providers/:id/test         # 测试连接 + 拉模型
GET  /api/providers/:id/models       # 缓存模型列表
POST /api/providers/:id/balance      # 查询余额
POST /api/chat                       # 测试对话
GET  /api/tokens                     # 用量统计
POST /api/tokens/reset               # 重置统计
```

## 借鉴

- [InkOS](https://github.com/Narcooo/inkos) — 模型路由/多agent配置设计
- [one-api](https://github.com/songquanpeng/one-api) — LLM API 管理标杆
- 鲁班工坊打磨

## License

MIT
