# LLM Gateway Dashboard v5.3 · 写作工作台

> 📱 手机上的 LLM 管理面板 + AI 写作工作台 —— 管模型、写小说，一个面板搞定。

[![Version](https://img.shields.io/badge/version-5.3-8b4513)](https://github.com/limingnanyue/novel-writing-workbench)
[![PWA](https://img.shields.io/badge/PWA-ready-36c073)](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
[![Zero Deps](https://img.shields.io/badge/frontend-zero_deps-36c073)]()

**4Tab 移动+桌面双模式 · InkOS 纸质美学 · OpenWrite 写作方法论 · 零前端依赖**

## 功能

### 🔌 LLM 网关管理

| 功能 | 说明 |
|:--|:--|
| **提供商管理** | 添加/删除 OpenAI 兼容 API |
| **连接测试** | 调用 `/models` 拉取模型列表，自动缓存 |
| **余额查询** | billing API / 测试调用双模式 |
| **用量统计** | Token 消耗、请求次数、测试次数 |

### ✍️ AI 写作工作台

| 功能 | 说明 | 灵感来源 |
|:--|:--|:--|
| **书籍管理** | 创建/切换/删除，多书并行 | — |
| **章节编辑** | 全文编辑器，自动字数统计 | oh-story-claudecode |
| **角色档案** | 五维骨架：外观·驱动·关系·弧线·语言 | oh-story-claudecode + OpenWrite |
| **大纲规划** | 三层结构：大纲→卷纲→细纲 | oh-story-claudecode |
| **记忆台账** | 结尾类型·角色状态·伏笔追踪 | OpenWrite |
| **AI 对话** | 书籍上下文注入，多模型切换 | InkOS |
| **7 大快捷指令** | 续写/黄金三章/大纲/角色/去AI味/质检/保存 | OpenWrite 路由表 |

### 🔬 去 AI 味系统（OpenWrite 6 门禁）

```
Gate A·禁用词替换 → Gate B·句式去套路 → Gate C·心理描写外化
Gate D·节奏打碎     → Gate E·对话去腔调 → Gate F·结尾去升华
+ 三刀流（斩逻辑链/砍形容词/拆长句）
+ 8 类必查（解释腔/作者报账/镜头脚本/先果后因…）
```

### ✅ 三层质检（OpenWrite）

- **字词级**：错别字/漏字/同音错字
- **句段级**：句式重复/指代断裂/时序跳跃
- **篇章级**：人名一致性/设定一致性/伏笔登记/钩子检测

### 🏆 黄金三章

逐章写作标准：穿越交代→系统激活→打脸→震惊→全场轰动，目标完读率 85%+。

## 快速开始

```bash
pip install fastapi uvicorn
python3 server.py
# → http://localhost:8080
```

## 设计系统

- **移动端** — 4Tab 底部导航（⌘仪表盘/🔌模型/✍️写作/⚙️设置）
- **桌面端** — 侧边栏导航 + 三栏布局（列表/主内容/详情面板）
- **写作 Tab** — InkOS 暖纸色调 `#faf6f0` + 噪点纹理 + Serif 阅读字体
- **全局** — 暗色 `#0a0a0f` + 电动蓝 `#5b8af7` + JetBrains Mono 数据
- **零前端依赖** — 纯 HTML/CSS/JS，单文件 54KB

## API（28 个端点）

### 网关管理（10 个）
```
GET    /api/health                     # 健康检查 + 统计
GET    /api/providers                  # 提供商列表
POST   /api/providers                  # 添加提供商
DELETE /api/providers/:id              # 删除
POST   /api/providers/:id/test         # 测试连接 + 拉模型
GET    /api/providers/:id/models       # 缓存模型列表
POST   /api/providers/:id/balance      # 查询余额
POST   /api/chat                       # 测试对话
GET    /api/tokens                     # 用量统计
POST   /api/tokens/reset               # 重置统计
```

### 写作工作台（14 个）
```
GET    /api/writing/books              # 书籍列表
POST   /api/writing/books              # 创建新书
GET    /api/writing/books/:id          # 书籍完整数据
DELETE /api/writing/books/:id          # 删除书籍
GET    /api/writing/books/:id/chapters           # 章节列表
POST   /api/writing/books/:id/chapters           # 创建/保存章节
GET    /api/writing/books/:id/chapters/:cid      # 获取章节
DELETE /api/writing/books/:id/chapters/:cid      # 删除章节
POST   /api/writing/books/:id/characters         # 保存角色
POST   /api/writing/books/:id/outline            # 保存大纲
POST   /api/writing/chat              # 写作对话（含书籍上下文）
```

### 写作工具（4 个隐式 API）
```
内存台账   → 浏览器 localStorage（结尾/角色状态/伏笔）
章节缓存   → localStorage
角色缓存   → localStorage
大纲缓存   → localStorage
```

## 借鉴与融合

| 项目 | 吸收的设计 |
|:--|:--|
| [InkOS](https://github.com/Narcooo/inkos) | 纸质文学配色·噪点纹理·Serif正文·折叠动画·消息流 |
| [oh-story-claudecode](https://github.com/worldwonderer/oh-story-claudecode) | 章节/角色/大纲三层结构·写前状态读取·上下文管理 |
| [chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill) | 写作工作流·偏好记忆·中断续写 |
| [OpenWrite](https://github.com/LearnPrompt/luban-skill) | 6门禁去AI·三层质检·黄金三章·记忆台账·19模块路由 |
| 鲁班工坊 | 验料→访行→过尺→慢刨→回炉 打磨流程 |

## License

MIT
