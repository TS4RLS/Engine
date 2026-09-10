"""
Shared config.json helpers.

config.json is JSONC (plain JSON plus `//` line comments) rather than
strict JSON, so it can carry inline documentation for every setting. This
module has the pieces every script that touches config.json needs:
  - strip_comments()/parse_jsonc() to read it
  - dump_commented() to write it back out with a `// description` comment
    above every known setting (used by config_editor.py so saving through
    the CLI never loses the comments)
"""

import json


def strip_comments(text: str) -> str:
    """Strip `//` line comments that fall outside string literals."""
    out = []
    in_string = False
    escape = False
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if in_string:
            out.append(ch)
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            i += 1
            continue
        if ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] not in "\r\n":
                i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def _escape_lazy_backslashes(text: str) -> str:
    # Allow single backslashes in paths (e.g. "C:\Users\...") instead of
    # requiring users to hand-escape them as "C:\\Users\\...".
    placeholder = "\x00"
    text = text.replace("\\\\", placeholder)
    text = text.replace("\\", "\\\\")
    text = text.replace(placeholder, "\\\\")
    return text


def parse_jsonc(text: str) -> dict:
    return json.loads(_escape_lazy_backslashes(strip_comments(text)))


def dump_commented(cfg: dict, settings, path: str) -> None:
    """Write cfg as JSON with a `// description` comment above every key
    that appears in `settings` (an iterable of (key, kind, description,
    ...) tuples, e.g. config_editor.SETTINGS), in that order. Any keys in
    cfg not covered by `settings` are appended afterwards, uncommented, so
    nothing is ever silently dropped."""
    known_keys = {entry[0] for entry in settings}
    descriptions = {entry[0]: entry[2] for entry in settings}
    ordered = [entry[0] for entry in settings if entry[0] in cfg]
    ordered += [key for key in cfg if key not in known_keys]

    lines = ["{"]
    for i, key in enumerate(ordered):
        comment = descriptions.get(key)
        if comment:
            lines.append(f"    // {comment}")
        comma = "," if i < len(ordered) - 1 else ""
        lines.append(f"    {json.dumps(key)}: {json.dumps(cfg[key])}{comma}")
    lines.append("}")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
