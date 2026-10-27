"""Scheduled tasks and what is due on each run.

Two tasks per user: "ant." runs hourly on weekdays from the brief time, "ant. weekend" three times a day
at weekends. Every run asks `due()` what to do this hour, so the morning brief, the Monday digest, the Thursday
review, the Sunday week ahead and tuning ride on the hourly run: two approvals, no collisions, one run at a time.
"""

from __future__ import annotations

import hashlib
import os
from datetime import datetime, timedelta
from typing import Any

from .util import load, parse_dt, tzinfo

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
JOB_ORDER = ["tuning", "morning_brief", "week_ahead", "pipeline_review", "monday_digest"]
MODE_RANK = ["daily", "week_ahead", "review", "digest", "weekend", "pulse"]


def _spec(spec_path: str | None = None) -> dict[str, Any]:
    return load(spec_path or os.path.join(ROOT, "schedules.json"))


def _back(seed: str) -> int:
    """Fixed on-the-hour or half-hour times move 1 to 29 minutes earlier, spread by user so runs do not pile up."""
    return int(hashlib.sha1(seed.encode()).hexdigest(), 16) % 29 + 1


def run_minute(config: dict[str, Any]) -> tuple[int, int]:
    """(hour, minute) of the first weekday run: 31 to 44 minutes before the brief time, so a run that takes a quarter
    of an hour still lands the brief by then. The lead is spread by user so runs do not pile up, and never on :00 or :30."""
    hh, mm = (config.get("brief_time") or "07:00").split(":")
    total = int(hh) * 60 + int(mm) - 31 - _back((config.get("user_email") or config.get("user_name") or "instinct").lower()) % 14
    if total % 60 in (0, 30):
        total -= 1
    return (total // 60) % 24, total % 60


def plan(config: dict[str, Any], spec_path: str | None = None) -> dict[str, Any]:
    """When the two tasks run, in the user's local time: the minute, the weekday hours and the weekend hours."""
    spec = _spec(spec_path)
    first_hour, minute = run_minute(config)
    brief_hh = int((config.get("brief_time") or "07:00").split(":")[0])
    shifted = first_hour != brief_hh  # the first run sits in the hour before the brief, so every run does
    last_hour = max(first_hour, spec.get("last_hour", 20) - (1 if shifted else 0))
    weekend = [(h - 1) % 24 if shifted else h for h in spec.get("weekend_hours", [10, 14, 18])]
    return {"minute": minute, "weekday_hours": list(range(first_hour, last_hour + 1)), "weekend_hours": weekend}


def day_runs(config: dict[str, Any], now: datetime, spec_path: str | None = None) -> list[datetime]:
    """Every scheduled run on now's date, in the user's local time."""
    p = plan(config, spec_path)
    hours = p["weekend_hours"] if now.weekday() >= 5 else p["weekday_hours"]
    return [now.replace(hour=h, minute=p["minute"], second=0, microsecond=0) for h in sorted(hours)]


def next_run(config: dict[str, Any], now: datetime, spec_path: str | None = None) -> datetime:
    """The next scheduled run after this one: weekday hours from the first run, weekend hours on Saturday and Sunday."""
    p = plan(config, spec_path)
    for day in range(8):
        d = (now + timedelta(days=day)).date()
        for hour in sorted(p["weekend_hours"] if d.weekday() >= 5 else p["weekday_hours"]):
            at = now.replace(year=d.year, month=d.month, day=d.day, hour=hour, minute=p["minute"], second=0, microsecond=0)
            if at > now + timedelta(minutes=10):
                return at
    return now + timedelta(hours=1)


def build(config: dict[str, Any], profiles: dict[str, Any] | None = None, spec_path: str | None = None) -> list[dict[str, Any]]:
    spec = _spec(spec_path)
    tz = config.get("tz") or "UTC"
    home_url = config.get("home_url") or "(your ant. Home link)"
    p = plan(config, spec_path)
    minute, first_hour, last_hour = p["minute"], p["weekday_hours"][0], p["weekday_hours"][-1]
    weekend = ",".join(str(h) for h in p["weekend_hours"])
    tasks = []
    for t in spec["tasks"]:
        cron = (t["cron"].replace("{minute}", str(minute)).replace("{first_hour}", str(first_hour))
                .replace("{last_hour}", str(last_hour)).replace("{weekend_hours}", weekend))
        tasks.append({"key": t["key"], "name": t["name"], "cron_expression": f"CRON_TZ={tz} {cron}",
                      "notifications": {"push": bool(t.get("push"))}, "prompt": t["prompt"].replace("{home_url}", home_url)})
    return tasks


def _at(text: str, config: dict[str, Any]) -> tuple[int, int]:
    text = text.replace("{brief_time}", config.get("brief_time") or "07:00")
    hh, mm = text.split(":")
    return int(hh), int(mm)


CONNECTOR_KEYS = ("email", "calendar", "notes", "crm", "drive", "lps")


def next_brief(config: dict[str, Any], now: datetime, spec_path: str | None = None) -> str:
    """When the next morning brief is ready, in words: "07:00 tomorrow" or "Mon 07:00" (never today's, already built)."""
    job = _spec(spec_path)["jobs"]["morning_brief"]
    hh, mm = _at(job["at"], config)
    local = now.astimezone(tzinfo(config.get("tz") or "UTC"))
    day = local.date() + timedelta(days=1)
    while day.weekday() not in job["days"]:
        day += timedelta(days=1)
    when = f"{hh:02d}:{mm:02d}"
    return f"{when} tomorrow" if day == local.date() + timedelta(days=1) else f"{day.strftime('%a')} {when}"


def due(config: dict[str, Any], home: dict[str, Any], now: datetime | None = None, weekend_prompt: bool = False,
        profiles: dict[str, Any] | None = None, spec_path: str | None = None) -> dict[str, Any]:
    """What this run should do. Reads the runs rows for the lock, for jobs already done today and for the window start."""
    spec = _spec(spec_path)
    profiles = profiles or load(os.path.join(ROOT, "ontology", "profiles.json"))
    tz = config.get("tz") or "UTC"
    now = (now or datetime.now(tzinfo(tz))).astimezone(tzinfo(tz))
    level = config.get("level") or "partner"
    wanted = set((profiles["profiles"].get(level) or profiles["profiles"]["partner"])["schedules"])
    # A run that found its guard off read nothing and stopped: it neither holds the lock nor moves the window.
    runs = sorted((r for r in home.get("runs") or [] if r.get("status") != "guard_off"), key=lambda r: str(r.get("started") or ""))
    notes: list[str] = []
    lock = timedelta(minutes=spec.get("lock_minutes", 50))
    for r in reversed(runs):
        started = parse_dt(r.get("started"), tz)
        if started and not r.get("finished") and timedelta(0) <= now - started < lock:
            return {"run": False, "reason": f"Another ant. run started at {started.strftime('%H:%M')} and is still going.",
                    "jobs": [], "build_mode": None}
        if started and not r.get("finished") and now - started >= lock:
            notes.append(f"The run that started at {started.strftime('%a %H:%M')} did not finish.")
            break
    today = now.date()
    done_today = set()
    for r in runs:
        started = parse_dt(r.get("started"), tz)
        if started and started.date() == today and r.get("finished") and not r.get("errors_fatal"):
            done_today.update(r.get("jobs") or [])
    jobs = []
    for key in JOB_ORDER:
        job = spec["jobs"].get(key)
        if not job or key not in wanted or key in done_today or now.weekday() not in job["days"]:
            continue
        hh, mm = _at(job["at"], config)
        at = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
        # Runs start 31 to 44 minutes before the hour they serve, so a job is due from an hour before its time.
        if at - timedelta(minutes=60) <= now < at + timedelta(minutes=90):
            jobs.append(key)
    weekend = weekend_prompt or now.weekday() >= 5
    modes = [spec["jobs"][j]["mode"] for j in jobs if spec["jobs"][j].get("mode")] + ["weekend" if weekend else "pulse"]
    build_mode = min(modes, key=lambda m: MODE_RANK.index(m) if m in MODE_RANK else 99)
    jobs.append("weekend_pulse" if weekend else "pulse")
    finished = [r for r in runs if r.get("finished")]
    cap = timedelta(hours=spec.get("window_cap_hours", 72))
    last_start = parse_dt(finished[-1].get("started"), tz) if finished else None
    # No finished run on record (a fresh Home, or rows pruned): look back the full three days rather than guess.
    window_start = max(last_start, now - cap) if last_start else now - cap
    # Each connector reads from the last run that read it: an hour it was busy or down is read again, never skipped.
    windows = {}
    for key in CONNECTOR_KEYS:
        # The last finished run that read this connector: a pulse that read no LP list does not move the LP window.
        good = next((r for r in reversed(finished) if key not in (r.get("unavailable") or {}) and
                     ("read" not in r or key in (r.get("read") or []))), None)
        start = parse_dt(good.get("started"), tz) if good else None
        windows[key] = (max(start, now - cap) if start else now - cap).isoformat()
    return {"run": True, "jobs": jobs, "build_mode": build_mode, "window_start": window_start.isoformat(), "windows": windows,
            "started": now.isoformat(), "run_id": "r" + now.strftime("%Y%m%dT%H%M"), "local_time": now.strftime("%a %H:%M"),
            "labels": [spec["jobs"][j]["label"] for j in jobs if j in spec["jobs"]], "notes": notes}
