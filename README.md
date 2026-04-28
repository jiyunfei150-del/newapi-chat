# newapi-chat

通过内部 AI 网关（兼容 OpenAI 格式）调用不同 AI 模型进行对话的命令行工具。

## 环境要求

- Python 3.10+
- 能访问 `https://ai.pocketcity.com` 的网络环境

## 安装

```bash
git clone https://github.com/jiyunfei150/newapi-chat.git
cd newapi-chat
```

无需安装任何依赖，使用 Python 标准库。

## 使用方式

### 列出可用模型

```bash
python scripts/newapi.py list
```

### 切换模型

```bash
python scripts/newapi.py switch gpt-4o
```

### 查看当前模型

```bash
python scripts/newapi.py current
```

### 发起对话（非流式）

```bash
python scripts/newapi.py chat "你好，介绍一下自己"
```

### 发起对话（流式，打字机效果）

```bash
python scripts/newapi.py stream "你好，介绍一下自己"
```

### 临时指定模型（不切换默认）

```bash
python scripts/newapi.py chat "你好" --model claude-3-5-sonnet
python scripts/newapi.py stream "你好" --model gpt-4o
```

### 多轮对话

```bash
python scripts/newapi.py chat "继续上面的话题" --history history.json
```

历史文件格式：

```json
[
  {"role": "system", "content": "你是一个助手"},
  {"role": "user", "content": "之前的问题"},
  {"role": "assistant", "content": "之前的回答"}
]
```

### 设置最大 Token 数

```bash
python scripts/newapi.py chat "写一篇长文" --max-tokens 8192
```

## 说明

- 默认 `max_tokens` 为 4096
- 当前选用模型保存在 `.current_model` 文件中
- 如连接超时，请确认当前网络环境是否可访问内网服务
