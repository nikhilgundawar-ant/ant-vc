#!/usr/bin/env python3
"""Build the golden test world for ant. for VCs.

Writes:
  evals/golden/world.json            everything, firm-wide
  evals/golden/bundles/<member>.json what each person's connectors would return (their mail, calendar, notes + shared CRM)
  evals/cases/*.json                 the planted answers every eval scores against

Deterministic: same output on every run. All people, companies, funds and LPs are fictional.
"""

from __future__ import annotations

import json
import math
import os
import random
import re
import sys
from datetime import date, datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from spec_content import (BRIEF_TRUTH, COMPETING, DEPARTURES, INBOUND, INTRO_THREADS, KPIS, MEETINGS_AHEAD,  # noqa: E402
                          NEWSLETTERS, NOT_COMPETING, RELATIONSHIPS, TARGETS, TRANSCRIPTS)
from spec_firm import (DEALS, DUPLICATES, EXTRA_PEOPLE, FIRM, FIRM_SITE, FOUNDERS, GMAIL_SECOND, HARD_NEGATIVES,  # noqa: E402
                       LP_CALLED_PCT, LP_LAST_CALL, LP_OWNER, LP_PAID_IN_PCT, LPS, MEMBERS, NOW, OTHERS, PASSES, PORTFOLIO, REVIEW_CASES, THESIS, TZ)

R = random.Random(42)
NOW_DT = datetime.fromisoformat(NOW)
TODAY = NOW_DT.date()
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CASES = os.path.join(ROOT, "evals", "cases")
STAGE_LABEL = {"inbound": "Inbound", "screening": "Screening", "first_meeting": "First Meeting", "second_meeting": "Second Meeting",
               "diligence": "Due Diligence", "partner_meeting": "IC", "term_sheet": "Term Sheet", "closing": "Closing",
               "portfolio": "Portfolio", "passed": "Passed"}
MEMBER = {m["key"]: m for m in MEMBERS}
MEMBER_BY_EMAIL = {m["email"]: m for m in MEMBERS}
ASKING = {"orbit": "Ask: any intros to senior backend engineers would help us hire the two this quarter.",
          "kestrel": "Ask: we would love intros to senior backend engineers for the two roles."}
INBOUND_NOTES = {"ledgerly": "US only, no India link. Round-two VC panel (Rohan): an India-first fund passes on this."}


def at(days_ago: float, hour: int | None = None, minute: int = 0) -> str:
    d = NOW_DT - timedelta(days=days_ago)
    h = hour if hour is not None else R.choice([9, 10, 11, 12, 14, 15, 16, 17, 18])
    return d.replace(hour=h, minute=minute, second=0, microsecond=0).isoformat()


def gmail_url(tid: str) -> str:
    return f"https://mail.google.com/mail/u/0/#all/{tid}"


def cal_url(eid: str) -> str:
    return f"https://calendar.google.com/calendar/event?eid={eid}"


def notes_url(tid: str) -> str:
    return f"https://notes.granola.ai/d/{tid}"


def crm_url(kind: str, rid: str) -> str:
    return f"https://quillwater.affinity.co/{kind}/{rid}"


def drive_url(fid: str) -> str:
    return f"https://drive.google.com/file/d/{fid}/view"


# ---------------------------------------------------------------- people and companies

people: dict[str, dict] = {}          # email -> person record (fixture truth)
truth_person: dict[str, str] = {}     # email -> canonical email (true identity)


def add_person(name, email, title=None, company=None, domain=None, role="other", crm=False):
    people[email] = {"name": name, "email": email, "title": title, "company": company, "domain": domain, "role": role, "crm": crm}
    truth_person.setdefault(email, email)


for m in MEMBERS:
    add_person(m["name"], m["email"], m["title"], FIRM["name"], FIRM["domain"], "colleague")

companies: dict[str, dict] = {}
for key, name, domain, sector, hq, entry, check in PORTFOLIO:
    companies[key] = {"id": f"c_{key}", "name": name, "domain": domain, "status": "portfolio", "sectors": [sector], "hq": hq,
                      "entry_stage": entry, "check_usd": check, "url": crm_url("companies", f"c_{key}"), "description": sector}
for (key, cname, domain, sector, hq, stage, days, owner, rnd, raise_usd, nstep, ndue, crm_last, extra) in DEALS:
    if extra.get("portfolio_key"):
        continue
    status = "passed" if stage == "passed" else "pipeline"
    companies[key] = {"id": f"c_{key}", "name": cname, "domain": domain, "status": status, "sectors": [sector], "hq": hq,
                      "url": crm_url("companies", f"c_{key}"), "description": sector}
for comp_key, plist in FOUNDERS.items():
    comp = companies.get(comp_key)
    for name, email, title in plist:
        add_person(name, email, title, comp["name"] if comp else None, comp["domain"] if comp else None, "founder", crm=True)
org_ids = {}
for key, name, email, title, cname, cdomain, role in OTHERS:
    add_person(name, email, title, cname, cdomain, role, crm=True)
    if cname and cname not in org_ids:
        org_key = re.sub(r"[^a-z0-9]+", "_", cname.lower()).strip("_")
        status = {"co_investor": "fund", "lp": "lp"}.get(role, "other")
        org_ids[cname] = f"c_org_{org_key}"
        companies[f"org_{org_key}"] = {"id": org_ids[cname], "name": cname, "domain": cdomain, "status": status, "sectors": [],
                                       "hq": None, "url": crm_url("companies", org_ids[cname]), "description": role}
for name, email, title, cname, cdomain in EXTRA_PEOPLE:
    add_person(name, email, title, cname, cdomain, "other", crm=False)
for canon, dname, demail, how, rule in DUPLICATES:
    add_person(dname, demail, people[canon]["title"], people[canon]["company"], people[canon]["domain"] if not demail.endswith(("gmail.com", "yahoo.com")) else None,
               people[canon]["role"], crm=False)
    truth_person[demail] = canon
    if demail in GMAIL_SECOND:
        second = GMAIL_SECOND[demail]
        add_person(dname, second, people[canon]["title"], None, None, people[canon]["role"], crm=False)
        truth_person[second] = canon
for canon, dname, demail in REVIEW_CASES:
    add_person(dname, demail, people[canon]["title"], people[canon]["company"], people[canon]["domain"], people[canon]["role"], crm=False)
    truth_person[demail] = canon  # same human; the right answer is a review row, not a silent merge
for inb in INBOUND:
    key, cname, domain, fname, femail = inb[0], inb[1], inb[2], inb[3], inb[4]
    if femail not in people:
        add_person(fname, femail, "Founder", cname, domain, "founder", crm=False)

# ---------------------------------------------------------------- threads and events

threads: list[dict] = []
events: list[dict] = []
tcount = [0]
ecount = [0]


def new_thread(subject, date_iso, messages, participants, labels=None, tid=None):
    tcount[0] += 1
    tid = tid or f"th{tcount[0]:04d}"
    threads.append({"id": tid, "subject": subject, "date": max(m["date"] for m in messages), "url": gmail_url(tid),
                    "participants": participants, "messages": messages, "labels": labels or [],
                    "snippet": messages[-1]["text"][:140]})
    return tid


def p_of(email, name=None):
    rec = people.get(email, {})
    return {"name": name or rec.get("name") or email.split("@")[0].title(), "email": email}


def msg(email, date_iso, text, name=None):
    return {"from": p_of(email, name), "date": date_iso, "text": text}


def new_event(title, start_iso, minutes, attendees, eid=None, description=None):
    ecount[0] += 1
    eid = eid or f"ev{ecount[0]:04d}"
    start = datetime.fromisoformat(start_iso)
    end = start + timedelta(minutes=minutes)
    events.append({"id": eid, "title": title, "start": start.isoformat(), "end": end.isoformat(), "url": cal_url(eid),
                   "attendees": attendees, "description": description})
    return eid


ROLE_EVENT = {
    "aditi": ["{c}: catch-up", "Coffee with {f}", "{c}: partner check-in"],
    "kabir": ["{c}: diligence", "{c}: diligence follow-up", "Call with {f}"],
    "meera": ["Intro call: {c}", "First call: {c}", "{c} <> Quillwater"],
    "rohan": ["Screening call: {c}", "Intro call: {c}"],
    "tara": ["Hiring sync: {c}", "Founder ask: {c}", "Community event planning"],
    "vikram": ["LP check-in: {c}", "{c}: quarterly check-in", "Fund admin: {c}"],
}
ROLE_SUBJECT = {
    "aditi": ["{c} update", "Quick question", "Following up", "LP intro request", "Board pack for {c}"],
    "kabir": ["{c} diligence", "Data room access", "Diligence questions", "Follow-up on our call"],
    "meera": ["{c} deck", "Pitch deck and next steps", "Raising our seed round", "Follow-up"],
    "rohan": ["Pitch deck: {c}", "Raising our pre-seed", "Market map question", "Screening notes"],
    "tara": ["Hiring: senior roles at {c}", "Founder ask: customer intro", "Community event", "Talent pool"],
    "vikram": ["Capital call notice", "Q3 NAV question", "Quarterly report", "Fund II update", "Audit timeline"],
}
BODIES = ["Thanks for the time today, really useful.", "Sharing a quick update on where things stand.", "Following up on our conversation.",
          "Happy to set up a call next week.", "Attaching the notes from our discussion.", "Let me know what you need from us."]

for mkey, rels in RELATIONSHIPS.items():
    member = MEMBER[mkey]
    for email, n_meet, n_thread, last_days in rels:
        rec = people[email]
        kinds = ["meeting"] * n_meet + ["thread"] * n_thread
        R.shuffle(kinds)
        total = len(kinds)
        span = max(0, 115 - last_days)
        step = span / max(1, total - 1) if total > 1 else 0
        cname = rec.get("company") or rec["name"]
        first = rec["name"].split()[0]
        for i, kind in enumerate(kinds):
            days = last_days + (i * step if i else 0)
            if kind == "meeting":
                title = R.choice(ROLE_EVENT[mkey]).format(c=cname, f=first)
                new_event(title, at(days), R.choice([30, 45]), [p_of(member["email"]), p_of(email)])
            else:
                when = at(days)
                subject = R.choice(ROLE_SUBJECT[mkey]).format(c=cname)
                earlier = (datetime.fromisoformat(when) - timedelta(hours=R.choice([3, 20, 26]))).isoformat()
                msgs = [msg(email, earlier, R.choice(BODIES)), msg(member["email"], when, R.choice(BODIES))] if R.random() < 0.6 else \
                       [msg(member["email"], earlier, R.choice(BODIES)), msg(email, when, R.choice(BODIES))]
                new_thread(subject, when, msgs, [p_of(member["email"]), p_of(email)])

# Weekly internal partner meetings and past board meetings shape each person's calendar.
for w in range(1, 13):
    day = TODAY - timedelta(days=TODAY.weekday()) - timedelta(days=7 * (w - 1))
    new_event("Monday partner meeting", datetime(day.year, day.month, day.day, 10, 0, tzinfo=NOW_DT.tzinfo).isoformat(), 60,
              [p_of(MEMBER[k]["email"]) for k in ("aditi", "kabir", "meera", "rohan")])
# The series runs ahead: next Monday's meeting is already on everyone's calendar. Its own id keeps every other id stable.
_next_mon = TODAY - timedelta(days=TODAY.weekday()) + timedelta(days=7)
_start = datetime(_next_mon.year, _next_mon.month, _next_mon.day, 10, 0, tzinfo=NOW_DT.tzinfo)
events.append({"id": "ev_pm_next", "title": "Monday partner meeting", "start": _start.isoformat(),
               "end": (_start + timedelta(minutes=60)).isoformat(), "url": cal_url("ev_pm_next"),
               "attendees": [p_of(MEMBER[k]["email"]) for k in ("aditi", "kabir", "meera", "rohan")], "description": None})
BOARDS = [("aditi", "orbit", 91, ["vikram@orbittreasury.in", "lata@orbittreasury.in"]), ("aditi", "kestrel", 63, ["neel@kestrelpay.in"]),
          ("aditi", "ledgerline", 34, ["mohan@ledgerline.io"]), ("aditi", "quanta", 55, ["harsh@quantarails.com"]),
          ("kabir", "cardinal", 27, ["zara@cardinalrisk.ai"]), ("kabir", "ferro", 69, ["anjali@ferrocredit.com"]),
          ("vikram", "orbit", 91, ["lata@orbittreasury.in"])]
for mkey, ckey, days, exts in BOARDS:
    new_event(f"{companies[ckey]['name']} board meeting", at(days, 10), 120, [p_of(MEMBER[mkey]["email"])] + [p_of(e) for e in exts])
for m in ("rohan",):
    for d in (4, 11, 18, 25):
        new_thread("Sourcing list: AA and UPI infra", at(d), [msg(MEMBER["rohan"]["email"], at(d), "Updated the sourcing list and market map.")],
                   [p_of(MEMBER["rohan"]["email"]), p_of(MEMBER["kabir"]["email"])])
for d in (6, 20, 34):
    new_thread("Capital call notice: Fund II", at(d), [msg(MEMBER["vikram"]["email"], at(d), "Draft capital call notice for review.")],
               [p_of(MEMBER["vikram"]["email"]), p_of("tom@ledgerlane.fund")])
for d in (9, 23):
    # The October ask copies Aditi, the board partner: it reaches Home from her own mailbox, not only Tara's.
    new_thread("Founder ask: customer intro to banks", at(d), [msg("divya@nimbuscollect.in", at(d + 0.2), "Could you intro us to two banks?"),
               msg(MEMBER["tara"]["email"], at(d), "On it, will share a shortlist.")], [p_of(MEMBER["tara"]["email"]), p_of("divya@nimbuscollect.in")] +
               ([p_of(MEMBER["aditi"]["email"])] if d == 9 else []))

# Duplicates: the same person under a second address.
DUP_MEMBER = {"maya@lumenledger.com": ("kabir", 5), "farhan@zenotreasury.com": ("meera", 10), "neha@trellisapi.in": ("meera", 8),
              "ishaan@atlassettle.com": ("aditi", 6), "siddharth@kitepay.in": ("kabir", 7), "abhishek.joshi@sablefraud.ai": ("meera", 9),
              "vikram@orbittreasury.in": ("aditi", 12), "katherine@ironwoodcomply.com": ("aditi", 4), "leena@embercredit.in": ("meera", 6),
              "nisha@brightvault.io": ("aditi", 72), "tanvi@vaultline.in": ("rohan", 6), "rhea@paysa.in": ("rohan", 8)}
for canon, dname, demail, how, rule in DUPLICATES:
    if how in ("same_event",):
        continue  # already together on a calendar invite in MEETINGS_AHEAD
    mkey, days = DUP_MEMBER[canon]
    member = MEMBER[mkey]["email"]
    if how == "thread":
        new_thread(f"Re: {people[canon]['company']}", at(days), [msg(demail, at(days), "Sharing the latest numbers as discussed.", dname)],
                   [p_of(member), p_of(demail, dname)])
    elif how == "same_thread":
        new_thread(f"{people[canon]['company']}: documents", at(days), [msg(canon, at(days), "Copying my personal address as well.")],
                   [p_of(member), p_of(canon), p_of(demail, dname)])
    else:  # gmail pairs: work + personal together once, then the second spelling alone
        new_thread(f"{people[canon]['company']}: from my personal address", at(days),
                   [msg(demail, at(days), "Writing from my personal email, work address copied.", dname)], [p_of(member), p_of(canon), p_of(demail, dname)])
        second = GMAIL_SECOND[demail]
        new_thread("Quick note", at(days + 12), [msg(second, at(days + 12), "Sending this from my phone.", dname)], [p_of(member), p_of(second, dname)])
for canon, dname, demail in REVIEW_CASES:
    new_thread("Model assumptions", at(15), [msg(demail, at(15), "Attached the model assumptions.", dname)], [p_of("kabir@quillwater.vc"), p_of(demail, dname)])
new_thread("Alumni giving and LP circles", at(30), [msg("priya.nair@northgate-alumni.example", at(30), "Would you speak at our alumni investor evening?")],
           [p_of("vikram@quillwater.vc"), p_of("priya.nair@northgate-alumni.example")])
new_thread("Angel co-invest", at(40), [msg("anita.dalal@gmail.com", at(40), "Happy to co-invest alongside you on the next fintech deal.")],
           [p_of("aditi@quillwater.vc"), p_of("anita.dalal@gmail.com")])

for a, b, mkey, days, subject in INTRO_THREADS:
    member = MEMBER[mkey]["email"]
    new_thread(subject, at(days), [msg(member, at(days + 0.5), f"Connecting you two, I think there's a lot to talk about."),
                                   msg(a, at(days), "Thanks for the intro, moving you to BCC.")], [p_of(member), p_of(a), p_of(b)])

# Transcripts and their meetings.
transcripts = []
commitment_truth = []
trap_truth = []
for tr in TRANSCRIPTS:
    att_emails = [MEMBER[k]["email"] for k in tr["members"]] + tr["externals"]
    attendees = [p_of(e) for e in att_emails]
    eid = new_event(tr["title"], tr["date"], 45, attendees, eid=f"ev_{tr['id']}")
    start = datetime.fromisoformat(tr["date"])
    lines = []
    for i, ln in enumerate(tr["lines"]):
        speaker, text = ln[0], ln[1]
        stamp = (datetime(2000, 1, 1) + timedelta(seconds=40 + i * 47)).strftime("%H:%M:%S")
        lines.append({"t": stamp, "speaker": speaker, "text": text})
        if len(ln) > 2 and isinstance(ln[2], dict):
            c = ln[2]
            commitment_truth.append({"transcript_id": tr["id"], "line": i, "owed_by": c["owed_by"], "owed_to": c["owed_to"], "what": c["what"],
                                     "due": c["due"], "kw": c["kw"]})
        elif len(ln) > 2 and isinstance(ln[2], str):
            trap_truth.append({"transcript_id": tr["id"], "line": i, "why": ln[2]})
    transcripts.append({"id": tr["id"], "event_id": eid, "title": tr["title"], "date": tr["date"], "attendees": attendees,
                        "url": notes_url(tr["id"]), "lines": lines})

for eid, mkeys, exts, start, minutes, title in MEETINGS_AHEAD:
    new_event(title, start, minutes, [p_of(MEMBER[k]["email"]) for k in mkeys] + [p_of(e) for e in exts], eid=eid)

# Inbound pitches.
inbound_truth = []
for (key, cname, domain, fname, femail, sector, stage, raise_usd, hq, traction, team, expected, inj, mkey) in INBOUND:
    days = R.choice([0.4, 0.8, 1.2, 2, 3, 4, 5]) if key not in ("paysa", "ruplink", "sutra", "coinvault", "glowkart") else \
        {"paysa": 1.1, "ruplink": 5.1, "sutra": 2.1, "coinvault": 2.1, "glowkart": 1.1}[key]
    money = f"${raise_usd / 1_000_000:.1f}M".replace(".0M", "M") if raise_usd else None
    raise_line = f"We're raising a {money} {stage} round." if money and stage else "We're raising our first institutional round."
    text = (f"Hi {MEMBER[mkey]['name'].split()[0]}, I'm {fname}, founder of {cname}. We're building {sector}. {traction} {team} "
            f"{raise_line} We're based in {hq}. Would love 30 minutes to walk you through the deck.").replace("  ", " ")
    if inj:
        text += f"\n\n{inj}"
    subject = f"{cname}: {stage or 'early'} pitch deck"
    tid = new_thread(subject, at(days), [msg(femail, at(days), text, fname)], [p_of(MEMBER[mkey]["email"]), p_of(femail, fname)],
                     labels=["inbound"], tid=f"in_{key}")
    inbound_truth.append({"key": key, "company": cname, "domain": domain, "thread_id": tid, "member": mkey, "expected": expected,
                          "injection": bool(inj), "attrs": {"name": cname, "domain": domain, "sector": sector, "stage": stage,
                                                             "raise_usd": raise_usd, "hq": hq, "traction": traction, "team": team},
                          **({"note": INBOUND_NOTES[key]} if key in INBOUND_NOTES else {})})

competing_truth = []
for (dkey, sender, sname, when, subject, text, mkey, deadline) in COMPETING:
    member = MEMBER[mkey]["email"]
    tid = new_thread(subject, when, [msg(member, (datetime.fromisoformat(when) - timedelta(hours=26)).isoformat(), "Thanks, good to catch up."),
                                     msg(sender, when, text, sname)], [p_of(member), p_of(sender, sname)], tid=f"cmp_{dkey}")
    competing_truth.append({"deal_key": dkey, "thread_id": tid, "deadline": deadline})
not_competing_ids = []
for (dkey, sender, sname, when, subject, text, mkey) in NOT_COMPETING:
    member = MEMBER[mkey]["email"]
    parts = [p_of(member), p_of(sender, sname)]
    if dkey == "prism":
        parts = [p_of(member), p_of("sanjay@prismlend.com")]
    tid = new_thread(subject, when, [msg(sender, when, text, sname)], parts, tid=f"neg_{dkey or len(not_competing_ids)}")
    not_competing_ids.append(tid)

# Portfolio updates, sent from each company's updates@ address.
portfolio_kpis = {}
update_truth = {}
for ckey, rows in KPIS.items():
    comp = companies[ckey]
    sep = rows[-1]
    when = at(R.choice([10, 11, 12, 13, 14, 15, 16, 17]))
    deps = DEPARTURES.get(ckey, [])
    team = f" Team: {deps[0]['name']}, our {deps[0]['role']}, is leaving at the end of October." if deps else " Team: hiring two engineers this quarter."
    if ckey in ASKING:  # a status line is not an ask; these two founders ask for help
        team += f" {ASKING[ckey]}"
    text = (f"Hi investors, here is the September update for {comp['name']}. Revenue: ${sep[1] / 1000:.0f}K (plan ${sep[2] / 1000:.0f}K). "
            f"Monthly burn: ${sep[3] / 1000:.0f}K. Cash in bank: ${sep[4] / 1_000_000:.2f}M. Logo churn: {sep[5]:.1f}%.{team}")
    recips = ["aditi@quillwater.vc", "kabir@quillwater.vc", "vikram@quillwater.vc", "tara@quillwater.vc"]
    sender = f"updates@{comp['domain']}"
    add_person(f"{comp['name']} Updates", sender, None, comp["name"], comp["domain"], "other")
    tid = new_thread(f"{comp['name']}: September investor update", when, [msg(sender, when, text)],
                     [p_of(sender)] + [p_of(r) for r in recips], labels=["portfolio_update"], tid=f"upd_{ckey}")
    series = []
    for i, (month, rev, plan, burn, cash, churn) in enumerate(rows):
        series.append({"month": month, "revenue_usd": rev, "plan_revenue_usd": plan, "burn_usd": burn, "cash_usd": cash, "churn_pct": churn,
                       "departures": deps if i == len(rows) - 1 else [], "source_url": gmail_url(tid) if i == len(rows) - 1 else crm_url("files", f"kpi_{ckey}_{month}")})
    portfolio_kpis[comp["id"]] = series
    update_truth[ckey] = {"thread_id": tid, "september": series[-1]}

for i, (email, name, subject) in enumerate(NEWSLETTERS):
    member = MEMBERS[i % len(MEMBERS)]["email"]
    add_person(name, email, None, None, None, "other")
    new_thread(subject, at(R.choice([0.5, 1, 2, 3])), [msg(email, at(1), f"{subject}. Read the full issue online.")], [p_of(member), p_of(email)],
               labels=["newsletter"])

# The Prism email that keeps it fresh even though the CRM says 20 days.
new_thread("Re: model questions", at(2), [msg("sanjay@prismlend.com", at(2), "Answers to your model questions attached.")],
           [p_of("kabir@quillwater.vc"), p_of("sanjay@prismlend.com")], tid="prism_fresh")

# ---------------------------------------------------------------- CRM, LPs, passes, drive

def strength_formula(meet, thread, last):
    raw = min(100, 12 * meet + 3 * thread)
    return int(round(raw * (0.5 + 0.5 * math.exp(-last / 60))))


strength_by: dict[str, dict[str, int]] = {}
for mkey, rels in RELATIONSHIPS.items():
    for email, nm, nt, last in rels:
        strength_by.setdefault(email, {})[MEMBER[mkey]["email"]] = strength_formula(nm, nt, last)

crm_people = []
for email, rec in people.items():
    if not rec.get("crm"):
        continue
    comp_id = None
    for c in companies.values():
        if c.get("domain") and rec.get("domain") == c["domain"]:
            comp_id = c["id"]
            break
    pid = "P-" + str(len(crm_people) + 101)
    crm_people.append({"id": pid, "name": rec["name"], "email": email, "company_id": comp_id, "title": rec.get("title"),
                       "url": crm_url("persons", pid), "strength_by_member": strength_by.get(email, {})})

crm_deals = []
deal_key_to_id = {}
for (key, cname, domain, sector, hq, stage, days, owner, rnd, raise_usd, nstep, ndue, crm_last, extra) in DEALS:
    did = f"d_{key}"
    deal_key_to_id[key] = did
    comp_key = extra.get("portfolio_key") or key
    crm_deals.append({
        "id": did, "company_id": companies[comp_key]["id"], "company_name": cname, "stage": STAGE_LABEL[stage],
        "stage_entered": (TODAY - timedelta(days=days)).isoformat(), "owner": MEMBER[owner]["email"], "round": rnd, "raise_usd": raise_usd,
        "next_step": nstep, "next_step_due": (TODAY + timedelta(days=ndue)).isoformat() if ndue is not None else None,
        "last_contact": (TODAY - timedelta(days=crm_last)).isoformat(), "quiet": False, "url": crm_url("opportunities", did),
    })

passes = [{"id": f"pass_{i:02d}", "company": c, "domain": d, "date": dt, "reason": r, "revisit_trigger": t, "by": MEMBER[b]["email"],
           "source_url": crm_url("notes", f"pass_{i:02d}")} for i, (c, d, dt, r, t, b) in enumerate(PASSES)]

lp_last = {}
lps = []
for (lid, name, ckey, commit, start, end, last_days) in LPS:
    contact = next(e for k, n, e, *_ in OTHERS if k == ckey)
    lps.append({"id": lid, "name": name, "fund": "Fund II", "commitment_usd": commit, "reup_window_start": start, "reup_window_end": end,
                "contacts": [contact], "last_touch": (TODAY - timedelta(days=last_days)).isoformat(), "reporting": "quarterly",
                "called_usd": round(commit * LP_CALLED_PCT), "paid_in_usd": round(commit * LP_PAID_IN_PCT.get(lid, LP_CALLED_PCT)),
                "last_call_date": LP_LAST_CALL, "owner": MEMBER[LP_OWNER.get(lid, "vikram")]["email"],
                "source_url": crm_url("companies", org_ids.get(name, lid))})
    lp_last[lid] = last_days

DRIVE = []
MEMO_DOCS = {
    "lumen": "Lumen Ledger metrics, September 2026. ARR: $2.4M. Growth: 9% month on month for six months. Customers: 12 NBFCs live, 3 in onboarding. "
             "Net revenue retention: 128%. Gross margin: 78%. Burn: $310K a month. Cash: $4.1M. Round: Series A, raising $8M.",
    "kite": "Kite Pay metrics, September 2026. Merchants live: 46. Monthly payment volume: $18M. Take rate: 0.35%. Revenue run-rate: $760K. "
            "Burn: $140K a month. Cash: $1.9M. Round: Seed, raising $3M.",
    "gravity": "Gravity Payouts metrics, September 2026. Payout volume: $4.2M a month. Gig platforms live: 3. Revenue run-rate: $540K. "
               "Gross margin: 61%. Burn: $120K a month. Cash: $1.4M. Round: Seed, raising $3M.",
    "atlas": "Atlas Settlement metrics, September 2026. Brokers live: 7. Daily settlements: 85,000. ARR: $3.1M. Growth: 7% month on month. "
             "Burn: $380K a month. Cash: $5.2M. Round: Series A, raising $9M.",
    "ironwood": "Ironwood Compliance metrics, September 2026. Banks live: 5. ARR: $1.8M. Pipeline: 14 banks. Logo churn: 0%. "
                "Burn: $260K a month. Cash: $3.3M. Round: Series A, raising $6M.",
}
for dkey, text in MEMO_DOCS.items():
    fid = f"dr_{dkey}_metrics"
    DRIVE.append({"id": fid, "name": f"{companies[dkey]['name']} - data room - metrics", "url": drive_url(fid), "text": text, "company": companies[dkey]["name"]})
CRM_NOTES = {
    "lumen": "Kabir: strong founder-market fit, Maya ran reconciliation ops at a large NBFC. Risk: concentration, top 3 customers are 52% of ARR.",
    "kite": "Kabir: Sid is a repeat founder. Risk: payment orchestration is crowded; differentiation is the routing engine.",
    "gravity": "Aditi: Arjun knows gig platforms deeply. Risk: single sponsor bank dependency.",
    "atlas": "Aditi: category leader in broker settlement. Risk: regulatory changes to settlement cycles.",
    "ironwood": "Aditi: Katherine sold compliance software to banks for a decade. Risk: long bank sales cycles, 9 months on average.",
}
crm_notes = [{"id": f"note_{k}", "deal_id": deal_key_to_id[k], "text": v, "url": crm_url("notes", f"note_{k}")} for k, v in CRM_NOTES.items()]
EMPATHY = {"Ishaan Verma": drive_url("em_ishaan_verma"), "Maya Chen": drive_url("em_maya_chen")}

world = {
    "fictional": "Every person, company, fund and LP in this file is fictional.",
    "now": NOW, "tz": TZ, "firm": {**FIRM, "members": [{"name": m["name"], "email": m["email"], "title": m["title"]} for m in MEMBERS]},
    "thesis": {**THESIS, "confirmed": True}, "firm_site": FIRM_SITE,
    "crm": {"system": "affinity", "companies": list(companies.values()), "people": crm_people, "deals": crm_deals, "notes": crm_notes},
    "passes": passes, "lps": lps, "portfolio_kpis": portfolio_kpis, "drive": DRIVE, "empathy_maps": EMPATHY,
    "threads": threads, "events": events, "transcripts": transcripts,
}


def bundle_for(mkey: str) -> dict:
    email = MEMBER[mkey]["email"]
    th = [t for t in threads if any(p["email"] == email for p in t["participants"])]
    ev = [e for e in events if any(a["email"] == email for a in e["attendees"])]
    trs = [t for t in transcripts if any(a["email"] == email for a in t["attendees"])]
    return {
        "fictional": world["fictional"], "now": NOW, "tz": TZ, "user": {"name": MEMBER[mkey]["name"], "email": email},
        "firm": world["firm"], "thesis": world["thesis"], "crm": world["crm"], "passes": passes, "lps": lps,
        "portfolio_kpis": portfolio_kpis, "empathy_maps": EMPATHY, "threads": th, "events": ev, "transcripts": trs,
    }


def write(obj, *path):
    full = os.path.join(*path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


write(world, HERE, "world.json")
for m in MEMBERS:
    write(bundle_for(m["key"]), HERE, "bundles", f"{m['key']}.json")

# ---------------------------------------------------------------- cases (the answers)

groups: dict[str, set] = {}
for email, canon in truth_person.items():
    groups.setdefault(canon, set()).add(email)
review_emails = {canon: demail for canon, _, demail in REVIEW_CASES}
merge_groups = [sorted(v) for k, v in groups.items() if len(v) > 1 and k not in review_emails]
write({"merge_groups": merge_groups, "never_merge": [[a, b, why] for a, b, why in HARD_NEGATIVES],
       "review_pairs": [[c, d] for c, d in review_emails.items()],
       "truth_person": truth_person}, CASES, "resolution.json")
write({m["key"]: m["level"] for m in MEMBERS}, CASES, "levels.json")
stale_truth = {"kabir": ["Vertex Card Issuing", "Banyan Risk Cloud", "Cobalt AA"], "meera": ["Halo Reconcile", "Copperleaf Collect", "Mosaic Wealth Infra"],
               "rohan": ["Clearpath Recon", "Ruplink"],
               # Solace's partner vote is due tomorrow: a deal whose next step is due today or tomorrow is moving, not stale.
               "aditi": ["Sterling AA"]}
write({"by_owner": stale_truth, "never_stale_for_owner": {"kabir": ["Prism Lending OS", "Lumen Ledger", "Kite Pay"]}}, CASES, "stale.json")
write({"positives": [{"company": next(c["name"] for c in companies.values() if c["id"] == f"c_{x['deal_key']}"), **x} for x in competing_truth],
       "negative_threads": not_competing_ids}, CASES, "competing.json")
write({"commitments": commitment_truth, "traps": trap_truth, "total": len(commitment_truth)}, CASES, "commitments.json")
write({"pitches": inbound_truth}, CASES, "inbound.json")
write({"flags": [{"company": "Orbit Treasury", "kind": "runway"}, {"company": "Kestrel Pay", "kind": "burn"},
                 {"company": "Ferro Credit Cloud", "kind": "revenue"}, {"company": "Tallyfin", "kind": "key_departure"},
                 {"company": "Saffire KYC", "kind": "churn"}], "updates": update_truth}, CASES, "portfolio.json")
write({"alerts": [{"lp_id": "lp_northgate", "breach": True}, {"lp_id": "lp_banyan", "breach": True},
                  {"lp_id": "lp_tidewater", "breach": False}, {"lp_id": "lp_peregrine", "breach": False}]}, CASES, "lp.json")
write({"targets": [{"company": c, "has_path": h} for c, h in TARGETS], "user": "aditi",
       "decay": {"aditi": ["Dev Malhotra", "Nisha Grover", "Kunal Shetty", "Omar Siddiqui"]}}, CASES, "network.json")
write({m: [{"kind": k, "key": v} for k, v in items] for m, items in BRIEF_TRUTH.items()}, CASES, "brief.json")
prep_truth = []
for eid, mkeys, exts, start, minutes, title in MEETINGS_AHEAD:
    if not exts:
        continue
    prep_truth.append({"event_id": eid, "member": mkeys[0], "title": title, "start": start,
                       "open_commitments_with": [c["what"] for c in commitment_truth
                                                 if any(people.get(e, {}).get("name") in (c["owed_by"], c["owed_to"]) for e in exts)]})
write({"meetings": prep_truth}, CASES, "prep.json")
write({"deals": [{"key": k, "deal_id": deal_key_to_id[k], "company": companies[k]["name"], "drive_doc": f"dr_{k}_metrics", "note": f"note_{k}"}
                 for k in MEMO_DOCS]}, CASES, "memo.json")

print(json.dumps({"threads": len(threads), "events": len(events), "transcripts": len(transcripts), "commitments": len(commitment_truth),
                  "traps": len(trap_truth), "people": len(people), "companies": len(companies), "deals": len(crm_deals),
                  "inbound": len(inbound_truth), "lps": len(lps), "merge_groups": len(merge_groups)}, indent=1))
