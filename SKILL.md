---
name: newapi-chat
description: >-
  Call AI models via the New API gateway (OpenAI-compatible) at ai.pocketcity.com.
  List available models, switch current model, send chat completions (streaming/non-streaming).
  Use when the user wants to call New API, list models, switch models, or chat with AI models
  through the internal gateway.
---

# New API Chat Skill

通过内部 AI 网关（兼容 OpenAI 格式）调用不同 AI 模型进行对话。

## 接入信息

- Base URL: `https://ai.pocketcity.com/`
- 内网 IP: `10.164.3.242`
- 协议: OpenAI Chat Completions API 兼容
- API Key 存放于工具脚本中，无需额外配置

## 使用方式

所有操作通过 `scripts/newapi.py` 脚本完成。

### 1. 列出可用模型

```bash
python scripts/newapi.py list
```

返回当前 API Key 有权限使用的所有模型 ID 列表。

### 2. 切换模型

```bash
python scripts/newapi.py switch <model_id>
```

将当前选用模型切换为指定的 `model_id`，并写入本地状态文件 `~/.cursor/skills/newapi-chat/.current_model`。

### 3. 查看当前模型

```bash
python scripts/newapi.py current
```

显示当前选用的模型 ID。

### 4. 发起对话（非流式）

```bash
python scripts/newapi.py chat "你的问题"
```

使用当前选用模型发起非流式对话，返回完整响应。

### 5. 发起对话（流式）

```bash
python scripts/newapi.py stream "你的问题"
```

使用当前选用模型发起流式对话，逐步输出响应内容。

### 6. 指定模型对话（不切换默认）

```bash
python scripts/newapi.py chat "你的问题" --model gpt-4o
python scripts/newapi.py stream "你的问题" --model gpt-4o
```

临时使用指定模型对话，不改变当前默认模型。

### 7. 多轮对话

```bash
python scripts/newapi.py chat "你的问题" --history history.json
python scripts/newapi.py stream "你的问题" --history history.json
```

传入历史对话文件进行多轮对话。历史文件格式为 JSON 数组：

```json
[
  {"role": "system", "content": "你是一个助手"},
  {"role": "user", "content": "之前的问题"},
  {"role": "assistant", "content": "之前的回答"}
]
```

### 8. 设置 max_tokens

```bash
python scripts/newapi.py chat "你的问题" --max-tokens 2048
```

默认 max_tokens 为 4096。

## 注意事项

- 此 skill 是独立封装的功能模块，不会替换或影响 Cursor 当前使用的主模型
- 需要在能访问 `10.164.3.242` 的网络环境下运行
- 如果脚本提示连接超时，请确认当前机器是否在内网环境中
