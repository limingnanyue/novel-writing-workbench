# Web 工具部署架构参考

> 提取自 novel-writing-workbench 在本次会话中从 v1.0 → v3.5 的架构演进。
> 适用于需要同时支持移动端 + 服务端部署的轻量级 Web 写作/工具类项目。

## 1. 后端框架选择

| 选项 | 本项目的选择 | 原因 |
|:-----|:------------|:------|
| Web框架 | FastAPI | 已安装、异步原生、内建 Swagger、Pydantic 校验 |
| 服务器 | uvicorn | FastAPI 推荐、轻量、可直接 python 启动无需 gunicorn |
| CORS | CORSMiddleware allow_origins=["*"] | 开发阶段全放通；生产环境应限制具体域名 |

**不选 Flask 的原因**：未安装且 FastAPI 功能更强。不选 Node.js 的原因：用户环境中 Python 已就绪。

## 2. 环境变量设计

| 变量 | 默认值 | 作用 |
|:-----|:-------|:------|
| `HOST` | `0.0.0.0` | 监听地址，生产需要显式设置 |
| `PORT` | `8080` | 避免与常见端口(80/443/3000/8000)冲突 |
| `DATA_DIR` | `./data` | 数据持久化路径，Docker 应挂载卷到此 |
| `DEBUG` | `""` | 设为 `1` `true` `yes` 开启 uvicorn info 日志 |

**设计原则**：最少变量原则——只有 4 个环境变量，每个都有一个合理的默认值。避免用配置文件。

## 3. 模块自动发现策略

```python
MODULES_CANDIDATES = [
    BASE_DIR / ".." / "novel-creation-omnibus" / "references" / "modules",  # 相邻项目
    BASE_DIR / "modules",       # 项目内
    DATA_DIR / "modules",       # 数据目录
    Path.home() / ".hermes" / "skills" / "novel-creation-omnibus" / "references" / "modules",  # Hermes 技能目录
]
```

**为什么这么做**：不假定模块一定在某个固定位置。允许用户通过软链接、Docker 挂载、项目目录结构三种方式提供模块。

## 4. 数据持久化路径

```
DATA_DIR/
├── chapters/            # 用户写作章节，自动编号 0001_章名.md
├── covers/              # 生成的 SVG 封面
├── token_usage.json     # Token 消耗统计
└── ai_providers.json    # 自定义 AI 提供商配置
```

**Docker 挂载建议**：
```yaml
volumes:
  - workbench_data:/data   # 持久化数据
  # - /path/to/modules:/app/modules  # 可选：挂载写作模块
```

## 5. 部署方式对比

| 方式 | 启动命令 | 适合场景 | 注意事项 |
|:-----|:---------|:---------|:---------|
| 直接运行 | `python3 server.py` | 本地开发/内网 | 需 pip3 install fastapi uvicorn |
| Docker | `docker-compose up -d` | 生产环境 | 含健康检查，自动重启 |
| systemd | `sudo bash deploy/deploy.sh` | Linux 服务器 | 使用 www-data 用户，隔离运行 |
| Nginx反代 | 参考 deploy/nginx.conf | 公网访问 | 建议加 SSL + 限制 IP |

## 6. Token 估算方法（无 AI API 调用时）

不使用实际 AI API 调用（避免产生费用），采用统计公式估算：

```python
def estimate_tokens(text: str) -> int:
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
    english = len(re.findall(r'[a-zA-Z]+', text))
    return max(1, int(chinese * 0.6 + english * 1.3))
```

- 中文字符 × 0.6（基于 GPT 系列 tokenizer 的近似）
- 英文单词 × 1.3（英文 token 化通常 1 词 ≈ 1.3 tokens）
- 最小值 1（避免除以零）

## 7. 封面生成架构

生成的是纯 SVG（非图片），优点是：
- **零依赖**：不需要 PIL/Pillow/ImageMagick
- **零存储成本**：SVG 文件通常 1-3KB
- **可缩放**：从手机屏幕到印刷尺寸都清晰
- **可编辑**：用户可用任何文本编辑器修改
- **可组合**：通过 f-string 直接嵌入文字，无需字体安装

8种预设风格的配色方案存储在 `COVER_PRESETS` 字典中，每个风格包含：
- `bg`: SVG 渐变背景色
- `accent`: 强调色（边框、标签）
- `text`: 文字颜色

```python
COVER_PRESETS = {
    "fantasy": {"bg": "linear-gradient(135deg, #1a0533, #0d1b3e)", "accent": "#c084fc", "text": "#f0e6ff"},
    "romance": {"bg": "linear-gradient(135deg, #2d1b2e, #1a0a0f)", "accent": "#f472b6", "text": "#fce7f3"},
    # ... 等等
}
```

## 8. 移动端布局策略

使用 `@media(min-width: 768px)` 断点实现双态：
- **手机 (<768px)**：底部导航栏、全屏弹出面板、44px+触控区、safe-area 适配
- **桌面 (≥768px)**：侧栏导航、右侧固定面板（380px 宽度）

核心原则：**CSS 驱动，零 JS 断点判断**。所有布局变化通过 CSS class 切换实现。

### safe-area 适配
```css
padding-top: calc(6px + env(safe-area-inset-top, 0px));
padding-bottom: env(safe-area-inset-bottom, 0px);
```

## 9. 关键决策记录

| 决策 | 选择 | 放弃的方案 |
|:-----|:-----|:----------|
| 前端架构 | 纯 HTML/CSS/JS SPA | React/Vue（增加构建步骤和依赖） |
| 数据存储 | 文件系统（JSON + Markdown） | SQLite/MySQL（增加运维复杂度） |
| 认证 | 无（内网部署） | JWT/OAuth（增加用户摩擦） |
| 模块源 | 自动发现多路径 | 硬编码路径 |
| 封面格式 | SVG | PNG/JPG（需图像库） |
| 移动端 | CSS media query | 独立移动端页面/vue-router |

---

**更新：** 2026-06-16
**关联项目：** novel-writing-workbench v3.5
