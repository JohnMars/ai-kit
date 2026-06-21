"""
Thin wrapper around `claude -p` so the evaluator uses the Claude Code
subscription (OAuth) instead of a bare ANTHROPIC_API_KEY.
"""
from __future__ import annotations
import json
import subprocess
import tiktoken

_enc = tiktoken.get_encoding("cl100k_base")  # close enough to Claude's tokenizer


def count_tokens(text: str) -> int:
    """Local token approximation — no API call, no overhead."""
    return len(_enc.encode(text))


def call(
    prompt: str,
    system: str = "",
    model: str = "claude-haiku-4-5-20251001",
    json_schema: dict | None = None,
) -> tuple[str, int]:
    """
    Run a non-interactive Claude call via `claude -p`.
    Returns (result_text, total_tokens_used).
    """
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "json",
        "--model", model,
    ]
    if system:
        cmd += ["--system-prompt", system]
    if json_schema:
        cmd += ["--json-schema", json.dumps(json_schema)]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"claude -p failed: {proc.stderr.strip()}")

    data = json.loads(proc.stdout)
    if data.get("is_error"):
        raise RuntimeError(f"claude error: {data.get('result', 'unknown')}")

    usage = data.get("usage", {})
    tokens_used = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
    return data["result"], tokens_used
