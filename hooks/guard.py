#!/usr/bin/env python3
"""ant. guard, a PreToolUse hook.

Scheduled ant. runs read strangers' email every hour with nobody watching, so they run on an allowlist. A session
is a scheduled run when any user message in its transcript carries the marker `[ant-vc-scheduled-run]`. In such a
session a tool call goes through only if it is one of these:

  - reading: the user's own connectors (list, get, search, read, query, fetch and the like), loading tools and skills,
    the task list, and files in the work folder or the plugin;
  - writing ant. Home: ArtifactData on the Home link named in the scheduled prompt only, writes to `snap/*` and
    `runs/*`, deletes of old `ratings/*` and `runs/*`. Never `state/*`: only the user's taps write that. A read saves
    only into the work folder (`out_dir`), and a write loads only files from the work folder or the plugin (`file_path`);
  - CRM field updates and notes (Notion: page properties only). The guard cannot see Home's approvals; the engine lists
    only the changes the user approved, and the skill applies only those;
  - a calendar hold on the user's own calendar: a fixed shape with nobody invited, at any depth;
  - a new email draft (never one that sends, and never an edit of a draft already saved);
  - files: Write, Edit, Read, Grep and Glob inside the work folder (`instinct-work`) only (reads may also use the
    plugin's own files), never the engine copy or the plugin;
  - the shell: the ant. engine (`python3 -I -S instinct-engine/instinct.py`, run from inside the work folder) and a
    short list of file commands (cd, mkdir, cp, ls, cat, head, tail, wc, date, echo, test), each with its own plain
    options only, every path inside the work folder, nothing that reaches the network;
  - databases: one read-only SELECT with plain functions, nothing that calls out.

Everything else is denied: sending, sharing, deleting, web fetches and searches, browsers, the user's devices,
scheduling, sub-agents, publishing pages, and writes to any other app. Every other session passes through untouched.
If the transcript cannot be read, the call passes (we cannot tell it is a scheduled run). So every scheduled run
starts with a canary, `echo instinct-guard-canary`, which this guard always refuses: if the canary runs, the guard is
not on, and the run stops before it reads anything. Once a run is known to be scheduled, any error denies.
"""

import json
import os
import re
import shlex
import sys

MARK = "[ant-vc-scheduled-run]"
CANARY = "instinct-guard-canary"
WORK_DIR = "instinct-work"
REASON = ("ant.'s scheduled checks only read your tools, update ant. Home, change CRM fields and notes, hold time on "
          "your own calendar, save drafts and run the engine. Make a draft or a proposal in ant. Home instead.")
PLUGIN_ROOT = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
ENGINE_DIR = "instinct-engine"
HOME_LINK = re.compile(r"https://claude\.ai/(?:code/)?artifact/[A-Za-z0-9_\-]+")

# Tool names are read as words: "outlook_email_search" reads, "search_and_send" does not.
WRITE_WORDS = {"send", "reply", "forward", "share", "trash", "delete", "remove", "archive", "spam", "unsubscribe", "trigger",
               "schedule", "permission", "permissions", "invite", "publish", "post", "upload", "comment", "comments", "label",
               "move", "merge", "transfer", "execute", "exec", "run", "create", "update", "set", "add", "edit", "patch",
               "write", "insert", "import", "copy", "duplicate", "restore", "respond", "apply", "enable", "disable", "cancel",
               "mark", "unmark", "untrash", "sign", "stop", "spawn", "submit", "start", "install", "connect", "approve",
               "convert", "react", "reaction", "pin", "enroll", "sequence", "assign", "resolved", "verify", "draft", "batch",
               "resolve", "push", "sync", "rename", "notify", "dial", "tweet", "save", "put", "purge", "wipe", "clear", "reset",
               "revoke", "grant", "kill", "terminate", "close", "reopen", "lock", "unlock", "mute", "unmute", "follow",
               "unfollow", "vote", "book", "reserve", "pay", "charge", "refund", "deploy", "rollback", "revert", "commit",
               "migrate", "provision", "generate", "compose", "sms", "broadcast", "announce", "alert", "accept", "decline",
               "reject", "complete", "snooze", "unsnooze", "transition", "track", "attach", "detach", "link", "unlink",
               "join", "leave", "kick", "ban", "upsert", "replace", "append", "prepend", "modify", "configure", "setup",
               "register", "subscribe", "invoke", "ingest", "export", "print", "fax"}
# A read on any other server starts or ends with one of these verbs ("get_deal", "email_search"), never "status_flip",
# "check_out" or "view_as", and carries no joining word: "get_and_send" is two actions.
STRICT_READ = {"list", "get", "search", "read", "query", "fetch", "find", "describe", "retrieve", "download", "count", "lookup",
               "discover"}
JOINS_AND_FLIPS = {"and", "then", "or", "plus", "also", "flip", "toggle", "switch", "out", "as", "impersonate", "become",
                   "login", "logout", "signin", "signout", "blast", "webhook", "webhooks"}
# The servers ant. reads every hour: only their known read tools pass as reads, by exact name (after the prefix is
# dropped); their drafts, holds and record updates still go through the rules below. Anything new on them is refused.
KNOWN_READS = [
    (re.compile(r"gmail"), {"search_threads", "get_thread", "get_message", "list_drafts", "get_draft", "list_labels"}),
    (re.compile(r"google_calendar|gcal"), {"list_events", "get_event", "search_events", "list_calendars", "suggest_time"}),
    (re.compile(r"google_drive|gdrive"), {"search_files", "read_file_content", "get_file_metadata", "list_recent_files",
                                          "download_file_content", "get_file_permissions"}),
    (re.compile(r"granola"), {"list_meetings", "get_meetings", "get_meeting_transcript", "query_granola_meetings",
                              "list_meeting_folders", "get_account_info", "get_meeting_attachment"}),
    (re.compile(r"slack"), {"search_public", "search_public_and_private", "search_channels", "search_users", "read_thread",
                            "read_channel", "read_user_profile", "read_canvas", "read_file", "read_list", "list_channel_members",
                            "list_user_channels", "get_reactions"}),
    (re.compile(r"notion"), {"search", "fetch", "get_comments", "get_users", "get_self", "get_teams", "get_groups",
                             "query_data_sources", "query_multiple_data_sources", "query_meeting_notes", "list_recent_pages",
                             "list_favorite_pages", "list_private_pages", "list_shared_pages", "list_page_backlinks",
                             "calendar_list_events", "calendar_list_calendars", "calendar_list_contacts",
                             "calendar_list_coworkers_events", "calendar_list_calendar_resources", "get_file_download_urls",
                             "download_attachment", "memory_search"}),
]
# Company and fund data providers. A read there names a read verb ("get_fund", "list_lps") or only the data it
# returns ("company_profile", "capital_accounts"): every word a known data noun. Any other word (email, remit, payout,
# release, settle, and whatever comes next) is refused, so an outbound or money-moving tool never passes as a read.
DATA_SERVERS = re.compile(r"pitchbook|harmonic|crunchbase|carta|cbinsights|dealroom|tracxn")
DATA_WRITE = {"issue", "exercise", "redeem", "wire", "distribute", "allocate", "file", "certify", "void"}  # fund-admin actions
DATA_NOUNS = {
    "company", "companies", "profile", "profiles", "organization", "organizations", "org", "orgs", "person", "persons", "people",
    "investor", "investors", "investment", "investments", "fund", "funds", "funding", "fundings", "round", "rounds", "deal", "deals",
    "capital", "account", "accounts", "lp", "lps", "gp", "gps", "portfolio", "portfolios", "holding", "holdings", "valuation",
    "valuations", "cap", "table", "tables", "captable", "security", "securities", "stakeholder", "stakeholders", "commitment",
    "commitments", "calls", "distributions", "transactions", "fees", "expenses", "metrics", "financials", "report", "reports",
    "statement", "statements", "document", "documents", "filing", "filings", "news", "signal", "signals", "employee", "employees",
    "headcount", "team", "teams", "founder", "founders", "contact", "contacts", "acquisition", "acquisitions", "exit", "exits",
    "market", "markets", "comparable", "comparables", "comps", "summary", "summaries", "detail", "details", "overview", "info",
    "information", "by", "id", "ids", "name", "names", "domain", "domains", "for", "of", "all", "latest", "recent", "history", "nav",
    "navs", "performance", "partner", "partners", "entity", "entities", "web", "traffic", "website", "websites", "similar",
    "competitor", "competitors", "industry", "industries", "sector", "sectors", "region", "regions", "tag", "tags", "notes",
    "quarter", "quarters", "period", "periods", "balance", "balances", "position", "positions", "ownership", "shares"}
DATA_READ = {"enrich"}  # a data provider's own word for a read: "enrich_company" returns a profile, changes nothing
# Data nouns that are also verbs: "contact_lps", "fund_account", "shares_documents" and "calls_investors" read as
# orders. A name made only of nouns may not start with one of these, nor end on (or be) one in its plain form
# ("account_fund", "lps_contact", "contact"), unless it ends with a word that says it returns facts ("fund_performance",
# "contact_details"). A plural at the end or alone is a noun: "contacts", "capital_calls" and "funds" read.
VERB_NOUNS = {"contact", "contacts", "fund", "funds", "tag", "tags", "exit", "exits", "report", "reports", "market", "markets",
              "signal", "signals", "name", "names", "balance", "balances", "partner", "partners", "document", "documents",
              "position", "positions", "shares", "calls"}
VERB_PLAIN = {"contact", "fund", "tag", "exit", "report", "market", "signal", "name", "balance", "partner", "document", "position",
              "share", "call"}
ABOUT_NOUNS = {"details", "detail", "profile", "profiles", "summary", "summaries", "performance", "history", "metrics", "overview",
               "info", "information", "financials", "valuation", "valuations"}
# A CRM's own read names: "view_records" and "batch_read_objects" read; "view_as" and "batch_update" do not.
CRM_READ_EXTRA = {"view"}
# What a scheduled run may change in snap/config: the Sunday tuning's own fields, merged in, nothing else.
TUNING_KEYS = {"weights", "today_items", "dwell_scale", "tuned_at", "updated_at"}
CRM_SERVER = re.compile(r"(affinity|attio|hubspot|salesforce|pipedrive|copper|folk|streak|airtable|close_crm|closecrm|"
                        r"\bcrm\b|_crm|crm_|notion)", re.I)
CRM_WRITE = re.compile(r"^(update|patch|edit|set_field|add_note|create_note|add_field_value|update_field_value)", re.I)
CRM_NEVER = {"delete", "remove", "trash", "archive", "merge", "move", "send", "email", "sequence", "enroll", "workflow",
             "webhook", "share", "permission", "permissions", "template", "schema", "attribute", "attributes", "property",
             "properties", "field", "fields", "definition", "list", "lists", "import", "export", "bulk", "skill", "skills",
             "data", "source", "database", "view", "owner", "user", "users", "team", "member", "members"}
CRM_RECORD_FIELDS = {"field", "fields"}  # "update_field_value" names a record's field, not the schema
DRAFT = re.compile(r"^(create_draft|draft_create|create_email_draft|gmail_create_draft|create_message_draft)$", re.I)
EVENT = re.compile(r"(create_event|event_create|insert_event|create_events)", re.I)
SQL_WRITE = re.compile(r"\b(insert|update|delete|drop|alter|truncate|grant|revoke|create|merge|upsert|copy|call|do|"
                       r"execute|vacuum|set|reset|lock|comment|security|listen|notify|refresh|into|prepare|load|import|"
                       r"cluster|reindex|discard|checkpoint)\b", re.I)
NO_SERVERS = re.compile(r"^mcp__(claude-code-remote|remote-devices|claude-device|claude-in-chrome|claude_in_chrome|Claude_Browser|"
                        r"computer|browser|visualize|minimi|memory|widgets|claude_ai|claude_docs|claude-docs|figma|postfast|postiz)", re.I)
# A database read: one SELECT (or WITH ... SELECT) that calls only plain functions, never one that reaches out.
SQL_OK_FUNCS = {"count", "sum", "min", "max", "avg", "lower", "upper", "coalesce", "nullif", "length", "trim", "date_trunc", "date",
                "now", "to_char", "cast", "round", "greatest", "least", "array_agg", "string_agg", "json_agg", "jsonb_agg",
                "json_build_object", "jsonb_build_object", "extract", "abs", "concat", "substring", "replace", "split_part", "age",
                "position", "row_number", "rank", "exists", "in", "any", "all", "not", "and", "or", "as", "from", "join", "on",
                "where", "select", "values", "with", "over", "filter", "using", "case", "when", "then", "else", "interval", "ilike",
                "like", "between", "is", "distinct", "union", "lateral", "partition", "by", "order", "group", "having", "limit"}
BUILTIN_OK = {"Read", "Glob", "Grep", "ToolSearch", "Skill", "TaskCreate", "TaskUpdate", "TaskList", "TaskGet",
              "SendUserMessage", "ListConnectors"}
# Keys that bring another person into an event, at any depth.
INVITE_KEY = re.compile(r"(attendee|guest|invit|participant|recipient|resource|organizer|optional_?attendee)", re.I)
REPEAT_KEY = re.compile(r"(recurr|rrule|repeat)", re.I)
CALENDAR_KEY = re.compile(r"^(calendar_?id|calendar)$", re.I)
# A hold on Google Calendar: these keys only, on the primary calendar, as a plain event.
HOLD_KEYS = {"summary", "title", "startTime", "endTime", "start", "end", "description", "calendarId", "calendar_id", "timeZone",
             "allDay", "availability", "colorId", "useDefaultReminders", "overrideReminders", "visibility", "location"}
NOTION_PAGE_KEYS = {"page_id", "command", "properties", "allow_async"}

SECRETS = re.compile(r"(/\.ssh/|/\.aws/|/\.gnupg/|/\.config/gcloud|/\.netrc|/\.git-credentials|\.env(\b|$)|credential|"
                     r"secret|token|password|id_rsa|id_ed25519|\.pem$|\.key$|/etc/shadow)", re.I)
SHELL_OK = {"cd", "mkdir", "cp", "ls", "cat", "head", "tail", "wc", "date", "echo", "test", "[", "true", "pwd", "python3", "python"}
# Each command's options, whole words only. No allowed option names a program, a file to write or a file of inputs, so a
# path can never hide inside an option (`sort -o/x`, `date -f/x`, `--compress-program=x`): those commands are not here.
_TEST_OPT = re.compile(r"^-([a-zA-Z]|eq|ne|lt|le|gt|ge|nt|ot|ef)$")
SHELL_OPTS = {
    "cd": re.compile(r"^$"), "pwd": re.compile(r"^$"), "true": re.compile(r"^$"), "cat": re.compile(r"^-n$"),
    "mkdir": re.compile(r"^-p$"), "cp": re.compile(r"^-(r|R|p|f|rp|pr|rf|fr|Rp|pR)$"), "ls": re.compile(r"^-[lahtrRS1d]+$"),
    "head": re.compile(r"^-(n|c)?\d*$"), "tail": re.compile(r"^-(n|c)?\d*$"), "wc": re.compile(r"^-[lcwm]+$"),
    "date": re.compile(r"^(-u|--utc|-R|-d|-I(date|hours|minutes|seconds|ns)?|--iso-8601(=(date|hours|minutes|seconds|ns))?)$"),
    "echo": re.compile(r"^-(n|e|E)$"), "test": _TEST_OPT, "[": _TEST_OPT,
}
NETWORK = re.compile(r"(curl|wget|\bnc\b|netcat|ssh|scp|rsync|ftp|telnet|/dev/(tcp|udp)|https?://|\bgit\b|\bpip3?\b|npm|npx|"
                     r"urllib|requests|socket|http\.client|smtplib|base64\s+-d)", re.I)


def scheduled_text(path):
    """The text of the user message that carries the marker, or "" when no user message does. Any user row counts,
    whatever comes before it; tool results do not."""
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i > 50000:
                break
            if MARK not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if row.get("type") != "user":
                continue
            content = (row.get("message") or {}).get("content")
            if isinstance(content, str) and MARK in content:
                return content
            if isinstance(content, list):
                texts = [c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"]
                if any(MARK in t for t in texts):
                    return " ".join(texts)
    return ""


def _link_id(url):
    return re.split(r"[/\-]", str(url or "").strip().rstrip("/"))[-1]


def _inside(path, folder):
    return path == folder or path.startswith(folder.rstrip(os.sep) + os.sep)


def _real(path, cwd):
    p = os.path.expanduser(str(path))
    return os.path.realpath(p if os.path.isabs(p) else os.path.join(cwd, p))


def _in_engine(real, cwd):
    """The engine copy, and the run's recipient list: only the engine writes either, never a tool call."""
    rel = os.path.relpath(real, cwd)
    # Compared in lower case: on a Mac, RECIPIENTS.json and Instinct-Engine are the same files.
    return ENGINE_DIR in rel.lower().split(os.sep) or os.path.basename(real).lower() == "recipients.json"


def work_root(cwd):
    """The run's work folder: `instinct-work` in the session folder, or the one the shell is already inside."""
    real = os.path.realpath(cwd or os.getcwd())
    parts = real.split(os.sep)
    if WORK_DIR in parts:
        i = len(parts) - 1 - parts[::-1].index(WORK_DIR)
        return os.sep.join(parts[: i + 1]) or os.sep
    return os.path.join(real, WORK_DIR)


def file_verdict(path, cwd):
    """Write and Edit: inside the work folder only, never the engine copy or the plugin."""
    if not path:
        return "A file write needs a path."
    real = _real(path, cwd)
    work = work_root(cwd)
    if _inside(real, PLUGIN_ROOT):
        return "Scheduled checks never change ant.'s own files."
    if not _inside(real, work):
        return "Scheduled checks write files only in their work folder (instinct-work)."
    if _in_engine(real, work):
        return "Scheduled checks never change the engine copy."
    return None


def read_verdict(path, cwd):
    """Read, Grep and Glob: the work folder and the plugin's own files, never keys or tokens."""
    real = _real(path or cwd, cwd)
    if SECRETS.search(real):
        return "Scheduled checks never read keys, tokens or passwords."
    if not (_inside(real, work_root(cwd)) or _inside(real, PLUGIN_ROOT)):
        return "Scheduled checks read files only in their work folder and the plugin."
    return None


ENGINE_SCRIPT = os.path.join(PLUGIN_ROOT, "engine", "instinct.py")
HEREDOC = re.compile(r"<<-?[ \t]*(['\"])(\w+)\1([^\n]*)\n(?:.*?\n)?[ \t]*\2[ \t]*(?=\n|$)", re.S)


def bash_verdict(command, cwd=None):
    """The engine and plain file commands, inside the work folder. A quoted heredoc's body is data; every other word is
    checked: no network, no substitution, variables or brace expansion, no environment changes, each command's own short
    list of options, and every path inside the work folder (reads may also use the plugin's files). Writes never touch
    the engine copy, which changes only by copying the plugin's own files. Python runs only the engine, isolated
    (`-I`), from inside the work folder."""
    session = os.path.realpath(cwd or os.getcwd())
    cwd0 = work_root(session)
    cmd = str(command or "")
    if CANARY in cmd:
        return "ant. guard is on: this scheduled check runs on its allowlist."
    cmd = cmd.replace("${CLAUDE_PLUGIN_ROOT}", PLUGIN_ROOT).replace("$CLAUDE_PLUGIN_ROOT", PLUGIN_ROOT)
    # Quoted heredocs (cat > bundle.json <<'EOF' ... EOF) are file content, not commands. The rest of the opening line
    # stays, so a redirect written after the marker is still checked. An unquoted heredoc expands $( ), so it stays.
    cmd = HEREDOC.sub(lambda m: m.group(3), cmd)
    cmd = re.sub(r"\d*>&\d+", " ", cmd)  # 2>&1 joins two outputs and writes no file
    if NETWORK.search(cmd):
        return "Scheduled checks never reach the network from the shell."
    if "$" in cmd or "`" in cmd or "<(" in cmd or ">(" in cmd:
        return "Scheduled checks run plain commands only: no substitution or variables."
    if "{" in cmd or "}" in cmd:
        return "Scheduled checks run plain commands only: no brace expansion."
    if "<<" in cmd:
        return "Write files with a quoted heredoc (<<'EOF') or the Write tool."
    if re.search(r"(^|[^&])&([^&]|$)", cmd) or ">|" in cmd:
        return "Scheduled checks run plain commands only: nothing in the background."
    here = session
    for seg in re.split(r"\n|;|&&|\|\||\|", cmd):
        seg = seg.strip()
        if not seg or seg.startswith("#"):
            continue
        # Redirections write files: each target must sit in the work folder, outside the engine copy.
        targets = re.findall(r"\d*>>?\s*([^\s<>|;&]+)", seg)
        seg_cmd = re.sub(r"\d*>>?\s*[^\s<>|;&]+", " ", seg)
        inputs = re.findall(r"\d*<\s*([^\s<>|;&]+)", seg_cmd)
        seg_cmd = re.sub(r"\d*<\s*[^\s<>|;&]+", " ", seg_cmd)
        if re.search(r"[<>]", seg_cmd):
            return "Scheduled checks run plain commands only."
        for t in inputs:
            real = _real(t.strip("'\""), here)
            if not (_inside(real, cwd0) or _inside(real, PLUGIN_ROOT)) or SECRETS.search(real):
                return "Scheduled checks read files only in their work folder and the plugin."
        for t in targets:
            if t in ("/dev/null",):
                continue
            real = _real(t.strip("'\""), here)
            if not _inside(real, cwd0) or _in_engine(real, cwd0):
                return "Scheduled checks write files only in their work folder, never the engine copy."
        try:
            words = shlex.split(seg_cmd)
        except ValueError:
            return "Scheduled checks run plain commands only."
        if not words:
            continue
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", words[0]):
            return "Scheduled checks never change the environment of a command."
        exe, args = words[0], words[1:]
        if "/" in exe or exe not in SHELL_OK:
            return f"Scheduled checks may run the ant. engine and file commands, not {os.path.basename(exe)}."
        paths = [w for w in args if not w.startswith("-") or w == "-"] + inputs
        if any(SECRETS.search(_real(w, here)) for w in paths):
            return "Scheduled checks never read keys, tokens or passwords."
        if exe in ("python3", "python"):
            i, flags = 0, set()
            while i < len(args) and args[i].startswith("-"):
                if not re.match(r"^-[ISBEsu]+$", args[i]):
                    return "Scheduled checks run Python only for the ant. engine."
                flags.update(args[i][1:])
                i += 1
            if "I" not in flags:
                return "Run the engine isolated: python3 -I -S instinct-engine/instinct.py ..."
            if i >= len(args):
                return "Scheduled checks run Python only for the ant. engine."
            script, rest = _real(args[i], here), args[i + 1:]
            if script == ENGINE_SCRIPT and rest == ["check"]:
                continue  # the plugin's own engine, checking itself, reads and writes nothing
            if not (os.path.basename(script) == "instinct.py" and os.path.basename(os.path.dirname(script)) == ENGINE_DIR
                    and _inside(script, cwd0)):
                return "Scheduled checks run Python only for the ant. engine."
            if not _inside(here, cwd0):
                return "Run the engine from inside the work folder: cd instinct-work && python3 -I -S instinct-engine/instinct.py ..."
            for w in rest:
                val = w.split("=", 1)[1] if w.startswith("--") and "=" in w else ("" if w.startswith("-") else w)
                if val and not (_inside(_real(val, here), cwd0) or _inside(_real(val, here), PLUGIN_ROOT)):
                    return "The engine reads and writes only in the work folder."
                if val and _in_engine(_real(val, here), cwd0):
                    return "The engine never writes into its own copy."
            continue
        for w in args:
            if w.startswith("-") and w != "-" and not SHELL_OPTS[exe].match(w):
                return f"Scheduled checks run {exe} with its plain options only, not {w}."
        if exe == "cd":
            if len(paths) != 1 or paths[0] in ("-", "~") or inputs:
                return "Scheduled checks move only into their work folder: cd instinct-work."
            target = _real(paths[0], here)
            if not _inside(target, cwd0):
                return "Scheduled checks stay in their work folder (instinct-work)."
            here = target
            continue
        writes = paths if exe == "mkdir" else paths[-1:] if exe == "cp" else []
        reads = paths[:-1] if exe == "cp" else [] if exe in ("mkdir", "echo", "true", "pwd") else \
            [] if exe == "date" else paths
        for w in writes:
            real = _real(w, here)
            if not _inside(real, cwd0):
                return "Scheduled checks write files only in their work folder."
            if _in_engine(real, cwd0) and not (exe == "cp" and reads and
                                                all(_inside(_real(r, here), os.path.join(PLUGIN_ROOT, "engine")) for r in reads)):
                return "Scheduled checks copy the engine only from the plugin's own engine folder."
        for w in reads:
            real = _real(w, here)
            if not (_inside(real, cwd0) or _inside(real, PLUGIN_ROOT)):
                return "Scheduled checks read files only in their work folder and the plugin."
    return None


SQL_CALL = re.compile(r'((?:"[^"]*"|[A-Za-z_][\w$]*)(?:\s*\.\s*(?:"[^"]*"|[A-Za-z_][\w$]*))*)\s*\(')


def sql_verdict(sql):
    """One SELECT (or WITH ... SELECT) that calls only plain functions: no writes, no second statement, and nothing
    that reaches out (net.http_post, dblink, a stored procedure). Comments, dollar quotes, escape strings and quoted
    function names are refused, so nothing can hide a call."""
    body = re.sub(r"'(?:[^'\\]|'')*'", "''", str(sql or ""))  # plain string literals are data
    if re.search(r"(/\*|\*/|--|\$|\\|\b[EUB]&?'|\bU&)", body, re.I):
        return "Scheduled checks read databases with plain queries only."
    if not re.match(r"^\s*(select|with)\b", body, re.I) or SQL_WRITE.search(body) or ";" in body.strip().rstrip(";"):
        return "Scheduled checks only read from databases."
    for fn in SQL_CALL.findall(body):
        name = fn.replace('"', "").replace(" ", "")
        if "." in name or '"' in fn or name.lower() not in SQL_OK_FUNCS:
            return f"Scheduled checks read databases with plain queries only, not {name}()."
    return None


def _deep_invites(value):
    """True when anyone else is brought into an event, at any depth."""
    if isinstance(value, dict):
        for k, v in value.items():
            if INVITE_KEY.search(str(k)) and v not in (None, "", [], {}, False, 0):
                return True
            if str(k) in ("eventType",) and str(v).upper() not in ("", "DEFAULT", "EVENT_TYPE_UNSPECIFIED"):
                return True  # an out-of-office event declines meetings on the user's behalf
            if str(k) in ("notificationLevel", "sendUpdates", "sendNotifications") and str(v).upper() not in ("", "NONE", "FALSE", "0"):
                return True
            if _deep_invites(v):
                return True
    elif isinstance(value, list):
        return any(_deep_invites(v) for v in value)
    return False


def _deep_keys(value, rx):
    """(key, value) pairs whose key matches, at any depth."""
    out = []
    if isinstance(value, dict):
        for k, v in value.items():
            if rx.search(str(k)):
                out.append((str(k), v))
            out += _deep_keys(v, rx)
    elif isinstance(value, list):
        for v in value:
            out += _deep_keys(v, rx)
    return out


def event_verdict(server, args):
    if _deep_invites(args):
        return "A hold goes on your calendar with nobody invited."
    if any(v not in (None, "", [], {}, False) for _, v in _deep_keys(args, REPEAT_KEY)):
        return "A hold is one event, never a repeating one."
    for _, v in _deep_keys(args, CALENDAR_KEY):
        cal = v.get("calendarId") or v.get("calendar_id") or v.get("id") if isinstance(v, dict) else v
        if cal not in (None, "", "primary"):
            return "A hold goes on your own primary calendar."
    if "google" in server and "calendar" in server:
        extra = sorted(k for k in args if k not in HOLD_KEYS)
        if extra:
            return "A hold is a plain event on your own calendar: " + ", ".join(extra) + " is not part of one."
        if str(args.get("calendarId") or args.get("calendar_id") or "primary") != "primary":
            return "A hold goes on your primary calendar."
        if str(args.get("visibility") or "default").lower() not in ("default", "private"):
            return "A hold keeps the calendar's own visibility."
    return None


def artifact_verdict(args, homes, cwd=None):
    """ArtifactData only on the Home link the scheduled prompt names. A read saves into the work folder only, and a
    write loads its data only from the work folder or the plugin, never from anywhere else on the machine."""
    if not homes or _link_id(args.get("url")) not in homes:
        return "Scheduled checks read and write only the ant. Home named in their prompt."
    cwd = cwd or os.getcwd()
    if args.get("out_dir") is not None:
        why = file_verdict(args.get("out_dir"), cwd)
        if why:
            return "Scheduled checks save Home only into their work folder (instinct-work)."
    for w in [args] + [x for x in (args.get("writes") or []) if isinstance(x, dict)]:
        if w.get("file_path") is not None:
            why = read_verdict(w.get("file_path"), cwd)
            if why:
                return why
    action = args.get("action")
    if action in ("get", "list", "query", "profiles"):
        return None
    writes = args.get("writes") if action == "batch" else [{"op": action, "collection": args.get("collection"), "doc_id": args.get("doc_id"),
                                                             "data": args.get("data"), "file_path": args.get("file_path")}]
    if not isinstance(writes, list) or not writes:
        return REASON
    for w in writes:
        if not isinstance(w, dict):
            return REASON
        if w.get("url") and _link_id(w.get("url")) not in homes:
            return "Scheduled checks write only to the ant. Home named in their prompt."
        top = str(w.get("collection") or "").split("/")[0]
        op = w.get("op")
        if op == "delete":
            if top not in ("ratings", "runs"):
                return "Scheduled checks delete only old ratings and old run rows."
        elif op in ("set", "update", "str_replace"):
            if top not in ("snap", "runs"):
                return "Scheduled checks write only ant.'s snapshots and run rows; your taps own state."
            if str(w.get("collection") or "").strip("/") == "snap" and w.get("doc_id") == "config" or \
                    str(w.get("collection") or "").strip("/") == "snap/config":
                why = config_verdict(op, w, cwd)
                if why:
                    return why
        else:
            return REASON
    return None


def config_verdict(op, w, cwd):
    """A scheduled run changes snap/config only as the Sunday tuning does: an update of the tuned fields, with sane
    values. The level, thesis, Home link, firm members and brief time belong to setup and settings."""
    why = "Scheduled checks change only the tuned fields of your settings (weights, items in Today, the stale-deal pace)."
    if op != "update":
        return why
    data = w.get("data")
    if data is None and w.get("file_path"):
        path = str(w.get("file_path"))
        path = path if os.path.isabs(path) else os.path.join(cwd or os.getcwd(), path)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, ValueError):
            return why
    if not isinstance(data, dict) or not data or set(data) - TUNING_KEYS:
        return why
    weights = data.get("weights")
    if weights is not None and not (isinstance(weights, dict) and all(isinstance(v, (int, float)) and 0 <= v <= 5 for v in weights.values())):
        return why
    items = data.get("today_items")
    if items is not None and not (isinstance(items, int) and 3 <= items <= 15):
        return why
    scale = data.get("dwell_scale")
    if scale is not None and not (isinstance(scale, (int, float)) and 0.5 <= scale <= 3):
        return why
    return None


def verdict(tool, args, ctx=None):
    """None to allow; a reason to deny. Only called in scheduled sessions."""
    ctx = ctx or {}
    cwd = ctx.get("cwd") or os.getcwd()
    if tool in BUILTIN_OK:
        if tool in ("Read", "Grep", "Glob"):
            if tool == "Glob" and (SECRETS.search(str(args.get("pattern") or "")) or
                                   re.search(r"(^[/~]|\.\.)", str(args.get("pattern") or ""))):
                return "Scheduled checks search only inside their work folder and the plugin."
            if tool == "Grep" and re.search(r"(^[/~]|\.\.)", str(args.get("glob") or "")):
                return "Scheduled checks search only inside their work folder and the plugin."
            return read_verdict(args.get("file_path") or args.get("path"), cwd)
        return None
    if tool in ("Write", "Edit"):
        return file_verdict(args.get("file_path"), cwd)
    if tool == "Bash":
        return bash_verdict(args.get("command"), cwd)
    if tool == "ArtifactData":
        return artifact_verdict(args, ctx.get("homes") or set(), cwd)
    if tool == "Artifact":
        # Listing finds Home. A read of a page is allowed; a read that saves a published file or an asset (`path`,
        # `paths`, `out_dir`) could write anywhere, so a scheduled check never asks for one.
        if args.get("action") == "list":
            return None
        if args.get("action") == "read":
            if any(args.get(k) for k in ("path", "paths", "out_dir")):
                return "Scheduled checks read a page itself, never save its files."
            return None
        return "Scheduled checks never publish, delete or open pages."
    if not tool.startswith("mcp__"):
        return REASON  # WebFetch, WebSearch, Agent, NotebookEdit, scheduling, notifications and any tool not listed above
    if NO_SERVERS.search(tool):
        return "Scheduled checks never use browsers, your devices, memory or scheduling."
    server, _, short = tool[5:].partition("__")
    srv = re.sub(r"[^a-z0-9]+", "_", server.lower())
    short = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", short)  # getJiraIssue reads as get_jira_issue
    name = re.sub(r"[^a-z0-9]+", "_", short.lower()).strip("_")
    for prefix in (srv + "_", "slack_", "notion_", "gmail_", "google_", "gcal_", "drive_", "outlook_", "m365_"):
        if name.startswith(prefix):
            name = name[len(prefix):]  # "slack_search_public" reads as "search_public"
    seq = [w for w in name.split("_") if w]
    words = set(seq)
    if re.search(r"execute_sql|run_sql|sql_query", name):
        return sql_verdict(str(args.get("query") or args.get("sql") or ""))
    known = next((reads for pat, reads in KNOWN_READS if pat.search(srv)), None)
    if known is not None:
        if name in known:
            return None
    elif DATA_SERVERS.search(srv):
        bad = words & (WRITE_WORDS | JOINS_AND_FLIPS | DATA_WRITE)
        verbs = STRICT_READ | DATA_READ
        # A name of nouns alone that opens with a noun that is also a verb, or ends on (or is) one in its plain form, is an
        # order, unless it ends on what it returns.
        order = bool(seq) and seq[-1] not in ABOUT_NOUNS and ((len(seq) > 1 and seq[0] in VERB_NOUNS) or seq[-1] in VERB_PLAIN)
        if seq and not bad and ((seq[0] in verbs or seq[-1] in verbs) and words <= verbs | DATA_NOUNS | {"view"} or
                                words <= DATA_NOUNS and not order):
            return None
    else:
        core = seq[1:] if len(seq) > 1 and seq[0] == "batch" and seq[1] in STRICT_READ else seq  # "batch_read_objects" reads
        verbs = STRICT_READ | (CRM_READ_EXTRA if CRM_SERVER.search(srv) else set())
        if core and (core[0] in verbs or core[-1] in STRICT_READ) and not set(core) & (WRITE_WORDS | JOINS_AND_FLIPS):
            return None
    if DRAFT.match(name):
        if any(re.search(r"send", str(k), re.I) and v for k, v in args.items()):
            return "A draft is saved, never sent."
        return draft_recipients_verdict(args, ctx.get("cwd"), ctx.get("transcript"))
    if EVENT.search(name):
        return event_verdict(srv, args)
    if "notion" in srv:
        # Notion as a CRM: a database row's properties, nothing else.
        if name != "update_page" or args.get("command") != "update_properties" or set(args) - NOTION_PAGE_KEYS or not args.get("properties"):
            return "In Notion, scheduled checks change only a record's properties."
        return None
    if CRM_SERVER.search(srv) and CRM_WRITE.match(name):
        bad = (words - CRM_RECORD_FIELDS if "value" in words else words) & CRM_NEVER
        if bad or re.search(r"(in_trash|archived|deleted|is_archived)", json.dumps(args), re.I):
            return "Scheduled checks change only a CRM record's fields and notes."
        return None
    return REASON


EMAIL = re.compile(r"^[A-Za-z0-9._%+'-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")
# Where a draft's words live. Everything else in a draft call is read for addresses, at any depth.
BODY_KEYS = re.compile(r"^(subject|body|text|html|html_?body|plain|plain_?text|content|snippet|signature|title|message_?body|"
                       r"body_?html|body_?text|text_?body|preview)$", re.I)
# Where a connector's result names people: message headers, invites, CRM people. Never a message's text.
HEADER_KEYS = re.compile(r"^(from|to|cc|bcc|sender|reply_?to|recipients?|to_?recipients|cc_?recipients|bcc_?recipients|attendees?|"
                         r"organizer|participants?|email|emails|email_?address(es)?|address|creator|owner|members?|contacts?)$", re.I)
HEADER_LINE = re.compile(r"^\s*(from|to|cc|bcc|reply-to|attendees?|organizer)\s*:(.*)$", re.I | re.M)


def _pieces(text):
    """The address-like pieces of a string: 'Ann <a@b.co>, c@d.co' gives a@b.co and c@d.co; names are dropped."""
    return [x for x in re.split(r"[\s,;<>()\[\]\"]+", str(text)) if "@" in x]


def _raw_headers(raw):
    import base64
    try:
        txt = base64.urlsafe_b64decode(str(raw) + "=" * (-len(str(raw)) % 4)).decode("utf-8", "replace")
    except Exception:
        return ["undecodable@raw.invalid"]
    head = txt.split("\r\n\r\n")[0].split("\n\n")[0]
    return [p for m in HEADER_LINE.finditer(head) for p in _pieces(m.group(2))]


def _draft_addresses(v, out, key=""):
    if key and BODY_KEYS.match(key):
        return
    if key.lower() == "raw" and isinstance(v, str):
        out.extend(_raw_headers(v))
        return
    if isinstance(v, str):
        out.extend(_pieces(v))
    elif isinstance(v, dict):
        for k, x in v.items():
            _draft_addresses(x, out, str(k))
    elif isinstance(v, list):
        for x in v:
            _draft_addresses(x, out, key)


def _header_addresses(v, out, under=False):
    """Addresses a connector really returned: only under header-like keys, at any depth, never from a message's text."""
    if isinstance(v, dict):
        for k, x in v.items():
            if BODY_KEYS.match(str(k)):
                continue
            _header_addresses(x, out, under or bool(HEADER_KEYS.match(str(k))))
    elif isinstance(v, list):
        for x in v:
            _header_addresses(x, out, under)
    elif isinstance(v, str) and under:
        out.update(p.lower() for p in _pieces(v) if EMAIL.match(p))


def transcript_people(path):
    """Every address a connector read returned in this run, from the transcript itself: tool results of `mcp__` tools
    only (Gmail, Calendar, the CRM and the like), header fields only. The run cannot add to this by writing a file."""
    names, out = {}, set()
    if not path:
        return out
    with open(path, encoding="utf-8", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i > 50000:
                break
            if '"tool_use"' not in line and '"tool_result"' not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            content = (row.get("message") or {}).get("content")
            if not isinstance(content, list):
                continue
            for c in content:
                if not isinstance(c, dict):
                    continue
                if c.get("type") == "tool_use":
                    names[c.get("id")] = str(c.get("name") or "")
                elif c.get("type") == "tool_result":
                    tool = names.get(c.get("tool_use_id"), "")
                    if not tool.startswith("mcp__") or NO_SERVERS.search(tool):
                        continue
                    body = c.get("content")
                    texts = [body] if isinstance(body, str) else [b.get("text", "") for b in body or [] if isinstance(b, dict)]
                    for t in texts:
                        try:
                            _header_addresses(json.loads(t), out)
                        except (ValueError, TypeError):
                            for m in HEADER_LINE.finditer(str(t)):
                                out.update(p.lower() for p in _pieces(m.group(2)) if EMAIL.match(p))
    return out


def draft_recipients_verdict(args, cwd, transcript=None):
    """Recipient lock: a scheduled run drafts only to people the user already deals with. An address passes only when
    it is on the build's list (`run/recipients.json`, from header fields) AND a connector returned it in this run's own
    transcript, in a header field. Every value in the call is read, at any depth, apart from its subject and body; an
    address ant. cannot read plainly (non-ASCII, a look-alike letter) is refused."""
    found = []
    _draft_addresses(args or {}, found)
    if not found:
        return "A draft needs a recipient the user already knows."
    odd = [a for a in found if not EMAIL.match(a)]
    if odd:
        return "A scheduled check saves no draft to an address it cannot read plainly: " + ", ".join(odd[:2]) + "."
    found = {a.lower() for a in found}
    path = os.path.join(work_root(cwd), "run", "recipients.json")
    try:
        with open(path, encoding="utf-8") as fh:
            known = {str(x).lower() for x in json.load(fh) if isinstance(x, str)}
    except Exception:
        return "No recipient list for this run, so a scheduled check saves no draft. It waits in ant. Home."
    seen = transcript_people(transcript) if transcript else set()
    new = sorted(found - (known & seen))
    if new:
        return ("A scheduled check drafts only to people already in your threads, invites or CRM. Not saved: "
                + ", ".join(new[:3]) + ". Write to them yourself from ant. Home if you mean to.")
    return None


def deny(why):
    sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                        "permissionDecisionReason": why}}))


def main():
    try:
        event = json.load(sys.stdin)
        path = event.get("transcript_path")
        text = scheduled_text(path) if path else ""
    except Exception:
        return 0  # cannot tell this is a scheduled run: never block the user's own work
    if not text:
        return 0
    try:
        ctx = {"cwd": event.get("cwd") or os.getcwd(), "homes": {_link_id(u) for u in HOME_LINK.findall(text)}, "transcript": path}
        why = verdict(str(event.get("tool_name") or ""), event.get("tool_input") or {}, ctx)
    except Exception:
        why = "The ant. guard could not check this call, so a scheduled check does not make it."
    if why:
        deny(why)
    return 0


if __name__ == "__main__":
    sys.exit(main())
