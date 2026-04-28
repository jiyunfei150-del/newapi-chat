#!/usr/bin/env python3
"""New API Chat - OpenAI 兼容网关调用工具"""

import argparse
import json
import os
import sys
from pathlib import Path
from urllib import request, error

BASE_URL = "https://ai.pocketcity.com"
API_KEY = "sk-LjCi2U6C3HG6msZew5MF6rMQNoqIWASoBLElnL6upA3uMLu9"
STATE_FILE = Path(__file__).parent.parent / ".current_model"
DEFAULT_MAX_TOKENS = 4096


def _headers():
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }


def _request(method: str, path: str, body: dict | None = None, stream: bool = False):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    req = request.Request(url, data=data, headers=_headers(), method=method)
    try:
        return request.urlopen(req, timeout=60)
    except error.HTTPError as e:
        err_body = e.read().decode(errors="replace")
        print(f"HTTP {e.code}: {err_body}", file=sys.stderr)
        sys.exit(1)
    except error.URLError as e:
        print(f"连接失败: {e.reason}", file=sys.stderr)
        print("请确认当前机器是否在内网环境中（需访问 10.164.3.242）", file=sys.stderr)
        sys.exit(1)


def _get_current_model() -> str | None:
    if STATE_FILE.exists():
        return STATE_FILE.read_text().strip()
    return None


def _set_current_model(model_id: str):
    STATE_FILE.write_text(model_id)


# ── Commands ──────────────────────────────────────────────


def cmd_list(_args):
    """列出可用模型"""
    resp = _request("GET", "/v1/models")
    data = json.loads(resp.read())
    models = data.get("data", [])
    if not models:
        print("没有可用模型")
        return
    models.sort(key=lambda m: m.get("id", ""))
    print(f"共 {len(models)} 个可用模型:\n")
    for m in models:
        print(f"  {m['id']}")


def cmd_switch(args):
    """切换当前模型"""
    _set_current_model(args.model_id)
    print(f"已切换到模型: {args.model_id}")


def cmd_current(_args):
    """查看当前模型"""
    model = _get_current_model()
    if model:
        print(f"当前模型: {model}")
    else:
        print("尚未选择模型，请使用 switch 命令设置")


def cmd_chat(args):
    """非流式对话"""
    model = args.model or _get_current_model()
    if not model:
        print("错误: 未指定模型，请先使用 switch 命令或 --model 参数", file=sys.stderr)
        sys.exit(1)

    messages = _build_messages(args)
    body = {
        "model": model,
        "messages": messages,
        "stream": False,
        "max_tokens": args.max_tokens,
    }

    resp = _request("POST", "/v1/chat/completions", body)
    data = json.loads(resp.read())

    choice = data.get("choices", [{}])[0]
    content = choice.get("message", {}).get("content", "")
    print(content)

    usage = data.get("usage")
    if usage:
        print(f"\n--- tokens: prompt={usage.get('prompt_tokens', '?')}, "
              f"completion={usage.get('completion_tokens', '?')}, "
              f"total={usage.get('total_tokens', '?')} ---", file=sys.stderr)


def cmd_stream(args):
    """流式对话"""
    model = args.model or _get_current_model()
    if not model:
        print("错误: 未指定模型，请先使用 switch 命令或 --model 参数", file=sys.stderr)
        sys.exit(1)

    messages = _build_messages(args)
    body = {
        "model": model,
        "messages": messages,
        "stream": True,
        "max_tokens": args.max_tokens,
    }

    resp = _request("POST", "/v1/chat/completions", body, stream=True)

    full_content = []
    for line in resp:
        line = line.decode("utf-8").strip()
        if not line or not line.startswith("data: "):
            continue
        payload = line[6:]
        if payload == "[DONE]":
            break
        try:
            chunk = json.loads(payload)
            delta = chunk.get("choices", [{}])[0].get("delta", {})
            text = delta.get("content", "")
            if text:
                print(text, end="", flush=True)
                full_content.append(text)
        except json.JSONDecodeError:
            continue

    print()


def _build_messages(args) -> list[dict]:
    """构建消息列表，支持历史对话"""
    messages = []
    if args.history:
        history_path = Path(args.history)
        if history_path.exists():
            with open(history_path, "r", encoding="utf-8") as f:
                messages = json.load(f)
        else:
            print(f"警告: 历史文件 {args.history} 不存在，将忽略", file=sys.stderr)
    messages.append({"role": "user", "content": args.prompt})
    return messages


# ── CLI ───────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="New API Chat - OpenAI 兼容网关调用工具"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list", help="列出可用模型")
    sub.add_parser("current", help="查看当前模型")

    p_switch = sub.add_parser("switch", help="切换当前模型")
    p_switch.add_argument("model_id", help="模型 ID")

    for name, help_text in [("chat", "非流式对话"), ("stream", "流式对话")]:
        p = sub.add_parser(name, help=help_text)
        p.add_argument("prompt", help="对话内容")
        p.add_argument("--model", help="临时指定模型（不改变默认）")
        p.add_argument("--history", help="历史对话 JSON 文件路径")
        p.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS,
                        help=f"最大生成 token 数（默认 {DEFAULT_MAX_TOKENS}）")

    args = parser.parse_args()

    handlers = {
        "list": cmd_list,
        "switch": cmd_switch,
        "current": cmd_current,
        "chat": cmd_chat,
        "stream": cmd_stream,
    }
    handlers[args.command](args)


if __name__ == "__main__":
    main()
