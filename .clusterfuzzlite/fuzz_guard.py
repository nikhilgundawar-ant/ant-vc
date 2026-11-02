"""Fuzz the scheduled-run guard. It reads tool calls that a hostile email may have shaped.

Promise: for any call, each verdict function ends with None (allow) or a reason (refuse), in good time. main() turns
a raise into a refusal, so a raise is safe, but it is still a crash here so we can look at it. The one known case, a
null byte in a path, is skipped below: os.path.realpath refuses it, so main() refuses the call.
"""
import json
import os
import sys

import atheris

HERE = os.path.dirname(os.path.abspath(__file__))
for folder in (HERE, os.path.join(HERE, "hooks"), os.path.join(HERE, "..", "hooks")):
    if os.path.isfile(os.path.join(folder, "guard.py")):
        sys.path.insert(0, folder)

with atheris.instrument_imports():
    import guard

CWD = "/tmp/ant-fuzz"
TOOLS = ["Bash", "Write", "Edit", "Read", "Artifact", "ArtifactData", "mcp__Gmail__create_draft",
         "mcp__Google_Calendar__create_event", "mcp__Notion__notion-update-page", "mcp__Supabase__execute_sql", "WebFetch"]


def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    text = fdp.ConsumeUnicodeNoSurrogates(4096)
    if "\x00" in text:
        return
    for result in (guard.bash_verdict(text, CWD), guard.sql_verdict(text), guard.file_verdict(text, CWD), guard.read_verdict(text, CWD)):
        assert result is None or isinstance(result, str)
    try:
        args = json.loads(text)
    except (ValueError, RecursionError):
        args = {"command": text}
    if not isinstance(args, dict):
        args = {"command": text}
    ctx = {"cwd": CWD, "homes": set(), "transcript": None}
    result = guard.verdict(fdp.PickValueInList(TOOLS), args, ctx)
    assert result is None or isinstance(result, str)


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
