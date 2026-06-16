# Hermes 工具使用注意事项

> 从本次会话（2026-06-16, novel-writing-workbench v3.5 开发）中发现的经验教训。

## 1. execute_code 中的文件读写陷阱

### ❌ 错误做法（会损坏文件）
```python
from hermes_tools import read_file, write_file

content = read_file("server.py")["content"]  # content 包含行号前缀！
# 返回内容格式: "     1|#!/usr/bin/env python3\n     2|...\n"
write_file("server.py", content)  # ❌ 把行号写入了文件！
```

### ✅ 正确做法
```python
from hermes_tools import terminal

# 方案 A: 用 terminal 读取和写入
result = terminal("cat server.py")  # 返回纯文本，无行号
# ... 处理 result["output"] ...
terminal("cat > server.py << 'EOF'\n" + processed_content + "\nEOF")

# 方案 B: 直接用 write_file 写全新内容
# （不经过 read_file 中转）
clean_content = """#!/usr/bin/env python3
new content here
"""
write_file("server.py", clean_content)  # ✅ 安全
```

### 为什么会这样
`read_file` 的设计是为人类阅读提供行号，返回的 content 字段包含 `行号|内容` 格式。这不是 BUG，但如果你把它当纯文本重新写回去，就会污染文件。

**根治方案**：永远不要用 read_file → write_file 做文件复制。用 terminal("cp a b") 或者 terminal("cat a") 读取内容。

## 2. GitHub Token 传参问题

### 症状
```bash
# ❌ 以下方式可能随机失败（token 被 shell 截断或转义）
python3 push_script.py "ghp_xxx...xxx"

# ❌ 环境变量方式也可能被 heredoc 吞掉
export TOKEN="ghp_xxx...xxx"
python3 -c "
import os
t = os.environ['TOKEN']  # 这里 t 可能是空字符串或截断版
"
```

### ✅ 可靠方案
```python
# 方案 A: 直接在 Python 脚本中硬编码（用完立即删除脚本）
t = "ghp_xxx...xxx"

# 方案 B: heredoc 内联（最可靠）
python3 << 'PYEOF'
t = "ghp_xxx...xxx"
# ... 使用 token ...
PYEOF
```

### 为什么会这样
不同 shell (bash/zsh/dash) 对 `$`、`!`、`\`、反引号等字符的转义规则不同。GitHub Token 是随机字符串，可能包含任意字符。传给子进程时会被 shell 二次解析。

## 3. 背景进程管理

### 启动服务
```python
terminal("python3 server.py", background=True, notify_on_complete=False)
# 返回 session_id，用于后续管理
```

### 操作
```python
process(action="log", session_id="proc_xxx")   # 查看完整日志
process(action="poll")                          # 检查是否还在运行
process(action="wait", timeout=60)              # 阻塞等待完成
process(action="kill", session_id="proc_xxx")   # 终止
```

### 重要
- 短服务（< 5分钟）直接用 foreground 模式 + 足够大的 timeout
- 长时间服务（服务器/批量任务）用 background + notify_on_complete
- 服务器启动后务必做健康检查：
  ```python
  time.sleep(2)
  health = terminal("curl -s http://localhost:8080/api/health")
  ```

## 4. 文件列表与内容查看

| 操作 | 命令 | 说明 |
|:-----|:------|:------|
| 列目录 | `ls -la path/` | 用 terminal |
| 查看文件内容 | `cat path/file.py` | 用 terminal（返回纯文本） |
| 搜索文件内容 | `grep -r "pattern" path/` | 用 terminal |
| 搜索文件名 | `find path/ -name "*.py"` | 用 terminal |
| 写入文件 | `cat > path/file << 'EOF'...EOF` 或 `write_file()` | 优先用 write_file |
| 编辑文件 | `sed` 或 `patch` 工具 | 慎用 sed，patch 更可靠 |

## 5. JSON 处理

当从 terminal 获取 JSON 输出时：
```python
result = terminal("curl -s http://localhost:8080/api/health")
import json
data = json.loads(result["output"])  # ✅ 直接解析
```

--- 

**更新：** 2026-06-16
**来源：** novel-writing-workbench v3.5 开发实战
