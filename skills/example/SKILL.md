---
name: example
description: >
  Use this skill when the user asks to count words in text or a file.
  Triggered by: "how many words", "word count", "count words in".
tools:
  - Read
  - Bash
---

1. If given a file path, read the file with the Read tool first.
2. Count words by splitting on whitespace.
3. Report: total word count, unique word count, average word length.
4. For files larger than 10 MB, use `wc -w <path>` via Bash instead of reading the full content.
5. Keep the response to one short paragraph — no preamble, no sign-off.
