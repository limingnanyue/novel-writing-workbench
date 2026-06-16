# InkOS Design Patterns — 适用于Web写作工具的交互模式

> 提取自 `@actalk/inkos` v1.4.0+ 的设计语言。这些模式不仅适用于 InkOS 本身，也适用于任何小说写作 Web 工具。

## 1. 相位工作流条 (Phase Workflow Bar)

### InkOS 的实现
Inkos 的工作流是 `Plan → Write → Audit → Revise`，每个阶段有独立 Agent。

### 提取为通用模式
```
写作 → 自检 → AI检测 → 定稿保存
```
- **数字圆标**：1/2/3/4 表示当前阶段
- **箭头连接**：▸ 分隔符，视觉上形成管线
- **完成态**：自动标记 ✔（done class），用户看到进度
- **点击跳转**：点击阶段名可触发对应动作（如点击"AI检测"触发分析）

### 适用场景
任何有多步骤工作流的工具（写作、代码审查、数据分析）

## 2. 终端美学状态栏 (Terminal Status Line)

### InkOS 的实现
Inkos 在终端中输出 `[ Book ] [ Chapter ] [ Status ]` 格式的状态行。

### 提取为通用模式
```
chars: 1234 · words: 567 · ¶: 12 · dialog: 45% · ai: 良好 · ⏱: 4.1m
```
- **标签:值** 格式，省略不必要的单位
- **颜色编码**：良好(绿) / 及格(黄) / 差(红)
- **等宽字体**：JetBrains Mono / Fira Code
- **始终可见**：固定在底部，不随滚动消失

### 适用场景
编辑器底部状态栏、仪表盘状态指示

## 3. SVG 评分环 (Readability Score Ring)

### InkOS 的实现
Inkos 使用数值评分系统（0-100）来评估章节质量。

### 提取为通用模式
```html
<svg width="60" height="60" viewBox="0 0 60 60">
  <circle class="bg" cx="30" cy="30" r="25"/>
  <circle class="fg" cx="30" cy="30" r="25"
    stroke-dasharray="157" stroke-dashoffset="${offset}"/>
</svg>
```
- **环形进度条**：用 `stroke-dasharray` + `stroke-dashoffset` 实现
- **颜色三档**：>=80 绿 / >=60 黄 / <60 红
- **中心数字**：居中显示评分值
- **动画过渡**：`transition: stroke-dashoffset .8s ease`

### 适用场景
质量评分、进度指示、达标检测

## 4. 章节自动编号与命名 (Chapter Auto-Numbering)

### InkOS 的实现
Inkos 的章节存储在 `books/<book-name>/chapters/0001_章名.md`。

### 提取为通用模式
```python
existing = sorted(save_dir.glob("*.md"))
chapter_num = len(existing) + 1
filename = f"{chapter_num:04d}_{ts}_{safe_name}.md"
```
- **四位编号**：保证按名称排序即按章节顺序
- **时间戳附缀**：防止重名冲突
- **章节代号牌**：侧栏 `#1` `#2` 实时更新

### 适用场景
任何需要管理版本/顺序的文件系统

## 5. 深色终端主题 (Dark Terminal Theme)

### 色彩方案
```
--bg-deep:        #08080e    最深层背景
--bg-surface:     #0d0d18    面板/侧栏
--bg-card:        #12121f    卡片/项目
--bg-card-hover:  #181830    悬停态
--bg-elevated:    #1a1a30    弹窗/浮层
--border:         #1e1e35    默认边框
--border-focus:   #3a3a60    聚焦边框
--accent:         #4a7cff    电动蓝 (主要强调)
--accent-glow:    rgba(74,124,255,0.12) 强调背景
--success:        #34d399    成功绿
--warning:        #fbbf24    警告黄
--danger:         #f87171    危险红
--text-primary:   #e4e4f0    主文字
--text-secondary: #9090b0    次级文字
--text-muted:     #505068    弱化文字
```

### 设计原则
- **极低对比度的底色**（`#08080e` 几乎是黑的）让内容区成为视觉焦点
- **强调色只用于交互元素**（按钮、选中态、链接），不用于装饰
- **边框极细**（1px），用透明度控制层次而非粗边框
- **圆角克制**（6px/10px），不过度圆润

## 6. 工具面板分页 (Panel Tabs)

### InkOS 的实现
Inkos 通过 `inkos status`、`inkos review` 等命令切换不同视图。

### 提取为通用模式
- **三/四个并排标签**：分析 / 模块 / 章节
- **底部边框激活态**：底部 2px 彩色边框，取代背景变色
- **懒加载**：只在切换到对应标签时加载数据
- **空状态提示**：无数据时显示引导文字 + 图标

## 7. 写作建议引擎 (Writing Suggestions)

基于统计分析自动生成改进建议：
```
如果 dialog_ratio < 15%  → "对话占比偏低，建议增加对话推进剧情"
如果 dialog_ratio > 60%  → "对话占比偏高，加入动作和描写穿插"
如果 ai_density > 8      → "AI味关键词密度较高，建议去AI味"
如果 paragraph_avg > 200 → "段落偏长，建议适当拆分"
如果短句比 < 20%         → "短句偏少，多用短句调节节奏"
全部达标                → "整体质量不错，继续保持 ✨"
```

## 8. 响应式布局策略

| 断点 | 调整 |
|:-----|:------|
| <768px | 侧栏折叠为图标栏（只显示icon），文字隐藏 |
| <768px | 编辑器 padding 减半（28px → 16px） |
| <768px | 工作流条横向滚动，阶段文字隐藏只留编号 |
| 任意宽度 | 右侧面板可折叠（`collapsed` class），用 toggle 按钮控制 |

---

**来源：** `@actalk/inkos` (npm) + novel-creation-omnibus 40模块
**更新：** 2026-06-16 — Added ChatPage section
**适用场景：** 小说写作Web工具、任何需要InkOS风格UI的应用

## 9. ChatPage 对话式写作界面 (v4.4)

### InkOS Studio 的实现

InkOS Studio 的 `ChatPage.tsx` 是一个完整的对话式AI写作界面：

- **消息流**: `ChatMessage` 组件以气泡形式渲染用户/AI/工具消息
- **固定输入栏**: 底部 textarea + 发送按钮，`Enter` 发送，`Shift+Enter` 换行
- **快捷操作**: `QuickActions` 组件，常用命令以 chip 形式排列在输入栏上方
- **模型选择**: 下拉菜单切换 AI 模型
- **自动滚动**: `scrollRef` + `isChatScrollNearBottom()` 检测
- **流式指示**: 正在生成时显示加载动画 (`Loader2` + `Shimmer`)
- **工具执行**: `ToolExecutionSteps` 组件内联显示 agent 工具调用

### 提取为通用 Web 模式

```html
<div class="chat-msgs">  <!-- 消息列表，flex-direction:column, gap -->
  <div class="msg user">  <!-- 用户消息右对齐 -->
    <div class="m-avatar">👤</div>
    <div class="m-bubble">用户输入</div>
  </div>
  <div class="msg assistant">  <!-- AI消息左对齐 -->
    <div class="m-avatar">AI</div>
    <div class="m-bubble">AI响应</div>
  </div>
</div>
<div class="qa-bar">  <!-- Quick actions chips -->
  <span class="qa-chip">✍️ 写第1章</span>
  <span class="qa-chip">🔍 分析文风</span>
</div>
<div class="chat-bar">  <!-- 固定输入栏 -->
  <textarea placeholder="告诉 AI..."></textarea>
  <button class="send">↑</button>
</div>
```

### 关键CSS：

```css
.msg.user { align-self: flex-end; flex-direction: row-reverse }
.msg.assistant { align-self: flex-start }
.m-bubble { padding: 8px 12px; border-radius: 12px; max-width: 90% }
```

### 后端 API 模式：

```python
@app.post("/api/chat")
def chat_write(req: ChatInput):
    provider = get_first_provider()
    # Load book context if specified
    # Pass conversation history to AI
    # Return assistant response with tokens
```

### 错误处理（优雅降级）：

```python
except HTTPException as he:
    return {"role": "assistant", "content": f"[AI连接失败] {he.detail}..."}
```
— 不要抛出 502 让前端崩溃，而是返回一条 assistant 消息告诉用户出了什么问题。

### 适用场景

任何需要对话式AI交互的 Web 工具（写作助手、coding assistant、客服机器人等）
