#!/usr/bin/env python3
"""Send one AI XP request and print the full raw response for debugging."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import anthropic


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for line in path.read_text(encoding="utf-8").splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#") or "=" not in raw:
            continue
        key, value = raw.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def get_setting(name: str, env_file_values: dict[str, str], default: str | None = None) -> str | None:
    return os.getenv(name) or os.getenv(name.upper()) or env_file_values.get(name) or env_file_values.get(name.upper()) or default


def build_prompt(name: str, description: str, frequency: str, difficulty: int, static_xp: int) -> str:
    return (
        "You are an XP evaluator for a gamified habit tracker.\n"
        "Evaluate this habit and return a fair XP reward.\n\n"
        f"Habit: {name}\n"
        f"Description: {description or 'N/A'}\n"
        f"Frequency: {frequency}\n"
        f"Difficulty: {difficulty}/5\n"
        f"Static baseline XP: {static_xp}\n\n"
        "Consider the effort, impact, and consistency required.\n"
        "Return ONLY valid JSON: {\"xp\": <integer>, \"reasoning\": \"<short explanation>\"}\n"
        f"The XP must be between {int(static_xp * 0.5)} and {int(static_xp * 2.0)}."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Inspect full Anthropic response for HabitQuest XP prompt.")
    parser.add_argument("--name", default="Read 20 pages")
    parser.add_argument("--description", default="Read a technical book chapter")
    parser.add_argument("--frequency", default="daily", choices=["once", "daily", "weekly", "monthly"])
    parser.add_argument("--difficulty", type=int, default=3)
    parser.add_argument("--static-xp", type=int, default=30)
    parser.add_argument("--max-tokens", type=int, default=200)
    args = parser.parse_args()

    env_values = load_env_file(Path("src/backend/.env"))
    api_key = get_setting("anthropic_api_key", env_values)
    model = get_setting("ai_model", env_values, "claude-haiku-4-5-20251001")

    if not api_key:
        raise SystemExit("Missing anthropic_api_key. Set it in env or src/backend/.env.")

    client = anthropic.Anthropic(api_key=api_key)
    prompt = build_prompt(args.name, args.description, args.frequency, args.difficulty, args.static_xp)

    response = client.messages.create(
        model=model,
        max_tokens=args.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )

    print("=== RAW RESPONSE OBJECT ===")
    if hasattr(response, "model_dump_json"):
        print(response.model_dump_json(indent=2))
    else:
        print(repr(response))

    print("\n=== CONTENT BLOCKS ===")
    for idx, block in enumerate(getattr(response, "content", []), start=1):
        block_dict = block.model_dump() if hasattr(block, "model_dump") else {"repr": repr(block)}
        print(f"[{idx}] {json.dumps(block_dict, indent=2)}")


if __name__ == "__main__":
    main()
