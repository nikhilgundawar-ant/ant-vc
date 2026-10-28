"""Build ant. Home documents for the fictional Quillwater Ventures fund.

Used by the Home QA harness and to seed the demo artifact. Everything here is fictional and the config carries
demo: true, so the page shows the "Example data" banner.

    python3 evals/demo.py --member aditi --out evals/runs/demo
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "engine"))
sys.path.insert(0, os.path.join(ROOT, "evals"))

from instinct import cli, homedb, safety  # noqa: E402
from instinct.util import dump, load  # noqa: E402

GOLD = os.path.join(ROOT, "evals", "golden")
CASES = os.path.join(ROOT, "evals", "cases")

# What Claude writes on top of the engine in a real run: three questions per prep card, drafts, CRM proposals.
QUESTIONS = {
    "Atlas Settlement": ["Where does the Bluepeak term sheet stand, and is 05 Nov still your decision date?",
                         "Can you send legal counsel's contact today so our lawyers can start?",
                         "Which two terms matter most to you before our markup goes out on 23 Oct?"],
    "Gravity Payouts": ["Which funds have sent offers, and what would make you choose us before 31 Oct?",
                        "Can you share the updated unit economics you planned to send on 16 Oct?",
                        "Who are the three gig platform references we can call this week?"],
    "Orbit Treasury": ["What is the plan to take runway past 12 months before tomorrow's board meeting?",
                       "When will the September MIS land, and what changed from plan?",
                       "Which hires in the plan can wait a quarter if revenue stays flat?"],
}


def truth_extraction() -> list[dict]:
    cases = load(os.path.join(CASES, "commitments.json"))
    world = load(os.path.join(GOLD, "world.json"))
    trs = {t["id"]: t for t in world["transcripts"]}
    return [{"transcript_id": c["transcript_id"], "owed_by": c["owed_by"], "owed_to": c["owed_to"], "what": c["what"], "due": c["due"],
             "quote": trs[c["transcript_id"]]["lines"][c["line"]]["text"]} for c in cases["commitments"]]


def inbound_for(b: dict) -> list[dict]:
    """Pitches as Claude reads them, flags included: a pitch that hides instructions for AI tools carries the flag and
    the instruction's own words, as inbound-triage step 2 writes them."""
    pitches = load(os.path.join(CASES, "inbound.json"))["pitches"]
    sender = {t["id"]: (((t.get("messages") or [{}])[0].get("from") or {}).get("email")) for t in b["threads"]}
    text = {t["id"]: " ".join(str(m.get("text") or m.get("body") or "") for m in (t.get("messages") or [])) for t in b["threads"]}
    out = []
    for p in pitches:
        if p["thread_id"] not in sender:
            continue
        flag = {}
        if p.get("injection"):
            body = text.get(p["thread_id"]) or ""
            hits = safety.detect_injection(body)
            at = body.find(hits[0]) if hits else -1
            said = re.split(r"(?<=[.!?])\s", body[at:])[0] if at >= 0 else str(p.get("injection_quote") or "")
            words = " ".join(said.split()[:15])  # the instruction's own words, up to 15
            flag = {"injection_flag": True, "injection_quote": words or None}
        out.append(dict(p["attrs"], thread_id=p["thread_id"], source_url=f"https://mail.google.com/mail/u/0/#all/{p['thread_id']}",
                        **({"from": sender[p["thread_id"]]} if sender.get(p["thread_id"]) else {}),
                        **({"revisit_check": REVISIT[p["thread_id"]]} if p["thread_id"] in REVISIT else {}), **flag))
    return out


# Drafts the morning brief saved to Gmail for the demo fund. Like the real skill, each uses only facts from its source:
# the meeting notes for a promise, the pitch for a reply. A missing fact is a bracketed gap for the user, never a guess.
DEMO_DRAFTS = {
    "aditi": {
        "intro arjun to raj malhotra at fable bank": {
            "to_name": "Arjun Khurana and Raj Malhotra", "cc": "raj.malhotra@fablebank.in",
            "subject": "Intro: Arjun Khurana (Gravity Payouts) and Raj Malhotra (Fable Bank)",
            "body": ("Hi Raj, Arjun,\n\nAs promised, connecting you two.\n\nRaj, Arjun founded Gravity Payouts. Payout volume crossed "
                     "four million dollars last month across three gig platforms, and they work with one sponsor bank today.\n\n"
                     "Arjun, Raj is at Fable Bank.\n\nI'll let you take it from here.\n\nAditi")},
        "send the term sheet markup": {
            "to_name": "Ishaan Verma", "subject": "Atlas Settlement: our term sheet markup",
            "body": ("Hi Ishaan,\n\nAs promised on our call on 20 Oct, here is our term sheet markup. It covers the two open points, "
                     "the option pool and the pro rata language, and the board seat we would take if we lead.\n\n"
                     "Happy to walk through it when we speak.\n\nAditi"),
            "context_extra": "Attach the markup before you send"},
    },
    "kabir": {
        "share the diligence checklist": {
            "to_name": "Siddharth Menon", "subject": "Kite Pay: our diligence checklist",
            "body": ("Hi Sid, Arun,\n\nAs promised at our check-in on 19 Oct, here is our diligence checklist. Thanks for the customer "
                     "reference list and the security audit report you are sending over.\n\nKabir"),
            "context_extra": "Attach the checklist before you send"},
        "send the cohort analysis questions": {
            "to_name": "Maya Chen", "subject": "Lumen Ledger: cohort analysis questions",
            "body": ("Hi Maya,\n\nAs promised, here are our cohort analysis questions, from the metrics in your data room:\n\n"
                     "1. Net revenue retention is 128%. How much of that comes from NBFCs growing their loan books, and how much from price?\n"
                     "2. For each monthly cohort since March, what share of customers is still live and growing?\n"
                     "3. The 3 NBFCs in onboarding: when do they go live, and what does a typical first year look like?\n\nKabir"),
            "context_extra": "Questions from the Lumen data room metrics in Drive (September 2026)"},
    },
    "meera": {
        "send the reference questions": {
            "to_name": "Abhishek Joshi", "subject": "Sable Fraud AI: reference questions for your customers",
            "body": ("Hi Abhishek,\n\nAs promised, here are our reference questions so you can brief your customers:\n\n"
                     "1. How long did it take to go live with Sable?\n2. What change have you seen in false positives since launch?\n"
                     "3. What would make you expand your use of Sable next year?\n\nThanks for the fraud loss benchmarks you are "
                     "sending over.\n\nMeera"),
            "context_extra": "The three questions are ant.'s suggestions, not from your notes: check them before you send"},
    },
    "tara": {
        "send the founder guest list": {
            "to_name": "Fatima Sheikh", "subject": "November founder dinner: guest list",
            "body": ("Hi Fatima,\n\nAs promised, the founder guest list for the November dinner so far:\n\n"
                     "1. Divya Raman, Nimbus Collect\n2. Pooja Malhotra, Mintrail\n3. Karthik Subramanian, Harbor Insure Stack\n\n"
                     "I will add Rahul from Tallyfin once he confirms. Could you send the venue shortlist when you have it?\n\nTara"),
            "context_extra": "Guests from the 22 Oct dinner planning invite"},
        "intro two cfo candidates": {
            "to_name": "Rahul Sharma", "subject": "Tallyfin: two CFO candidates",
            "body": ("Hi Rahul,\n\nAs promised, two CFO candidates for Tallyfin: George Thomas and Swati Kulkarni. Both are in our "
                     "network. Tell me who you would like to meet first, and I will introduce you this week.\n\nTara"),
            "context_extra": "Names from your CRM: the two people tagged CFO candidate. Check each is open to a move before you send"},
    },
    "vikram": {
        "answer the fee offset question": {
            "to_name": "Helen Park", "subject": "Fee offset on monitoring fees",
            "body": ("Hi Helen,\n\nApologies for the delay on the fee offset question your committee raised on 2 Sep.\n\n"
                     "[Add how monitoring fees offset the management fee under the Fund II agreement.]\n\n"
                     "Glad to go through it when we meet today.\n\nVikram"),
            "context_extra": "ant. looked in Drive and your notes for the Fund II agreement and found no fee offset clause. Add it before you send"},
    },
    "rohan": {
        "rupee rails": {
            "subject": "Re: Rupee Rails",
            "body": ("Hi {first},\n\nThanks for sending Rupee Rails our way. UPI infrastructure for banks is right in our focus, and live "
                     "with two banks is a strong start. Would {slot1} or {slot2} IST work for a 30-minute call?\n\nRohan"),
            "context_extra": "Slots from your calendar"},
    },
}
# What Claude found when it read a returning pitch against the revisit condition (the inbound-triage step).
REVISIT = {"in_paysa": {"met": True, "evidence": "two marketplaces live on payouts, $310K annualised revenue"},
           "in_ruplink": {"met": True, "evidence": "AA licence granted in September"}}


SLOTS = ("Mon 26 Oct at 11:00", "Tue 27 Oct at 16:00")  # free on the demo calendars


def free_slots(member: str, now_iso: str, n: int, avoid: set[str] | None = None) -> list[tuple[str, str]]:
    """n free half-hours on the member's calendar from the next working day, 10:00 to 17:00, each 30 minutes clear of any
    meeting, as (label, ISO start): each
    call draft of a morning offers its own two, and no time an open draft already offers is offered again."""
    from datetime import datetime, timedelta  # noqa: E402
    avoid = {str(x)[:16] for x in (avoid or set())}
    try:
        b = load(os.path.join(GOLD, "bundles", f"{'aditi' if member == 'solo' else member}.json"))
    except OSError:
        return [(x, "") for x in SLOTS]
    now = datetime.fromisoformat(now_iso)
    busy = []
    for e in b.get("events") or []:
        try:
            st, en = datetime.fromisoformat(e["start"]), datetime.fromisoformat(e.get("end") or e["start"])
        except (KeyError, ValueError):
            continue
        busy.append((st, en if en > st else st + timedelta(minutes=30)))
    out, day = [], now.replace(hour=0, minute=0, second=0, microsecond=0)
    while len(out) < n:
        day += timedelta(days=1)
        if day.weekday() >= 5:
            continue
        for hh in (10, 11, 12, 14, 15, 16):
            t = day.replace(hour=hh)
            # Thirty minutes clear on each side of any meeting: no call offered back to back with another.
            if any(st < t + timedelta(minutes=60) and en > t - timedelta(minutes=30) for st, en in busy) or t.isoformat()[:16] in avoid:
                continue
            out.append((f"{t.strftime('%a')} {t.day} {t.strftime('%b')} at {t.strftime('%H:%M')}", t.isoformat()))
            if len(out) >= n:
                break
    return out


def _swap_slots(body: str, old: list[str], new: tuple[str, str]) -> str:
    """Each old time for a new one, in one pass, so a new time that matches an old one is never swapped twice."""
    marks = [f"\x00{i}\x00" for i in range(len(old))]
    for o_, m_ in zip(old, marks):
        body = body.replace(_slot_label(o_), m_)
    for m_, n_ in zip(marks, new):
        body = body.replace(m_, n_)
    return body


def _slot_label(iso: str) -> str:
    from datetime import datetime  # noqa: E402
    t = datetime.fromisoformat(iso)
    return f"{t.strftime('%a')} {t.day} {t.strftime('%b')} at {t.strftime('%H:%M')}"


ASK_FOR = {"stage unknown": "which stage you are at", "round size not stated": "how much you are raising, and from whom",
           "traction not stated": "revenue and paying customers so far", "no paying customers": "who pays you today, and how much"}
DOCS = re.compile(r"\b(deck|list|notes|checklist|markup|memo|data|report|framework|model|questions|summary|plan|paragraph|letter)\b", re.I)


def _first(name: str | None) -> str:
    return str(name or "").split(" ")[0] or "there"


def template_draft(o: dict, user_first: str, slots: tuple[str, str] = SLOTS) -> dict:  # slots: two labels
    """A plain draft from an owed entry and nothing else, as the morning brief would write it: no fact it cannot source."""
    first = _first(o.get("to_name"))
    if o.get("kind") == "ask" and o.get("items"):
        # Several asks for the same colleague: one note, a paragraph each, the cash warnings first.
        paras = []
        for k, it in enumerate(o["items"], 1):
            ask_ = str(it.get("ask") or "").rstrip(".")
            ask_ = ask_[:1].lower() + ask_[1:]
            line = f"{k}. {it.get('company')}: {it.get('who') or 'the founder'} asked for {ask_}."
            if it.get("note_kind") == "board":
                warn = str(it.get("warning") or "").split(":")[0]
                line += f" One flag first: {warn[:1].lower() + warn[1:]}. Should we help them hire now?"
            elif (it.get("path") or {}).get("person"):
                p_ = it["path"]
                line += (f" You know {p_.get('person')}" + (f" at {p_.get('company')}" if p_.get("company") else "") +
                         ". Would you make the introduction?")
            paras.append(line)
        n = len(paras)
        body = (f"Hi {first},\n\n{['', 'One', 'Two', 'Three', 'Four'][n] if n < 5 else n} founder asks need you:\n\n" + "\n".join(paras) +
                ("\n\nIf you say yes to a hire, I will ask the team who knows someone." if any(it.get("note_kind") == "board" for it in o["items"]) else "")
                + f"\n\n{user_first}")
        return {"to_name": o.get("to_name"), "subject": f"Founder asks: {o.get('company')}", "body": body, "context_extra": None}
    if o.get("kind") == "ask":
        # A founder's ask, finished: to the contact you know, to the colleague who knows them, or to the team.
        p0 = o.get("path") or {}
        ask = str(o.get("ask") or "").rstrip(".")
        ask_l = ask[:1].lower() + ask[1:]
        who = o.get("who") or "The founder"
        co = o.get("company") or "one of our companies"
        tail = ""
        if o.get("also"):  # another email today reaches them too: one line links the two
            other = str((o["also"] or {}).get("to_name") or "").split(" ")[0]
            tail = f" Separately, my introduction to {other} is on its way today." if other else " Separately, another note from me is on its way today."
        if o.get("note_kind") == "board":
            # Cash is tight: the board partner decides whether the firm sources at all, before anyone else is asked.
            warn = str(o.get("warning") or "").split(":")[0]
            then = (f" If yes, {p0.get('colleague')} {'know' if p0.get('colleague') == 'You' else 'knows'} {p0.get('person')}, who could help."
                    if p0 and p0.get("person") else " If yes, I will ask the team who knows someone.")
            body = (f"Hi {first},\n\n{who} at {co} asked for {ask_l}. One flag first: {warn[:1].lower() + warn[1:]}. "
                    f"Should we help them hire now?{then}\n\n{user_first}")
            subject = f"{co}: {ask_l}, before we source"
        elif p0 and p0.get("colleague") == "You":
            body = (f"Hi {_first(p0.get('person'))},\n\n{who} at {co}, one of our portfolio companies, is looking for {ask_l}. "
                    f"Would you be open to an introduction? Happy to share more first.{tail}\n\n{user_first}")
            subject = f"An introduction: {co}"
        elif p0:
            body = (f"Hi {_first(p0.get('colleague'))},\n\n{who} at {co} asked for {ask_l}. You know {p0.get('person')}"
                    + (f" at {p0.get('company')}" if p0.get("company") else "") + ". Would you make the introduction? I can send a short blurb."
                    + (f" {o['warning']}." if o.get("warning") else "") + f"\n\n{user_first}")
            subject = f"An introduction for {co}: {p0.get('person')}"
        else:
            body = (f"Hi all,\n\n{who} at {co} asked for {ask_l}. ant. found no warm path in our network. "
                    f"Who knows someone who fits?\n\n{user_first}")
            subject = f"Can anyone help {co}?"
        return {"to_name": o.get("to_name"), "subject": subject, "body": body, "context_extra": None}
    if o.get("kind") == "ask_nudge":
        # One short nudge for a note with no reply in five working days: when you wrote, each ask in a line, nothing new.
        from datetime import date as _d  # noqa: E402
        on = _d.fromisoformat(o["sent_on"]) if o.get("sent_on") else None
        on_txt = f"{on.day} {on.strftime('%b')}" if on else "last week"
        items = o.get("items") or []
        hi = "Hi all" if "," in str(o.get("to") or "") else f"Hi {first}"

        def low(t: object) -> str:
            t = str(t or "").rstrip(".")
            return t[:1].lower() + t[1:]
        thanks = ""
        if (o.get("answered") or {}).get("companies"):  # they answered the rest of the note: thanks first, then only these
            cos = list(o["answered"]["companies"])
            names_ = cos[0] if len(cos) == 1 else ", ".join(cos[:-1]) + " and " + cos[-1]
            thanks = (f"Thanks for the {names_} intro. " if o["answered"].get("kind") == "made" else f"Thanks on {names_}. ")
        if thanks:
            body = (f"{hi},\n\n{thanks}And " + "; ".join(f"{it.get('company')}: {low(it.get('ask'))}" for it in items) +
                    f"? A quick yes or no is plenty.\n\n{user_first}")
        elif len(items) > 1:
            body = (f"{hi},\n\nBumping my note of {on_txt} on these founder asks:\n\n" +
                    "\n".join(f"- {it.get('company')}: {low(it.get('ask'))}" for it in items) +
                    f"\n\nA quick yes or no on each is plenty.\n\n{user_first}")
        else:
            it = items[0] if items else {}
            body = f"{hi},\n\nBumping my note of {on_txt} on {it.get('company')}: {low(it.get('ask'))}. A quick yes or no is plenty.\n\n{user_first}"
        subject = f"Re: {o['re']}" if o.get("re") else f"Founder asks: {o.get('company')}"
        return {"to_name": o.get("to_name"), "subject": subject, "body": body, "context_extra": None}
    if o.get("kind") == "holder":
        # One internal note to the partner whose view the drafts wait on: a line per draft, the late ones first, then any
        # decision near. No view of the user's own, and nothing the entry does not hold.
        from datetime import date as _d  # noqa: E402

        def day_(x: object) -> str:
            try:
                v_ = _d.fromisoformat(str(x)[:10])
                return f"{v_.strftime('%a')} {v_.day} {v_.strftime('%b')}"
            except ValueError:
                return ""
        lines = []
        for it in o.get("items") or []:
            # "Share feedback after the partner meeting" reads as what they wait for: "feedback after the partner meeting, for Omkar".
            what_ = re.sub(r"^(share|send|give|forward)\s+", "", str(it.get("what") or "").rstrip("."), flags=re.I)
            what_ = what_[:1].lower() + what_[1:]
            when_ = ("was due " if it.get("overdue") else "due ") + day_(it.get("due")) if it.get("due") else ""
            lines.append(f"- {it.get('company') or _first(it.get('to_name'))}: {what_}" + (f", for {_first(it.get('to_name'))}" if it.get("to_name") else "") +
                         (f", {when_}" if when_ else ""))
        for x in o.get("decisions") or []:
            lines.append(f"- {x.get('company')}: {x.get('what')}, decide by {day_(x.get('deadline'))}")
        n_ = len(o.get("items") or [])
        body = (f"Hi {first},\n\nA few founder emails wait on your view before I send them:\n\n" + "\n".join(lines) +
                f"\n\nA line on each is plenty, or ten minutes today if easier.\n\n{user_first}")
        # The subject follows what the note names now: a rebuild that drops a decision drops it from the subject too.
        subject = (f"Your view on {n_} founder email{'s' if n_ != 1 else ''}" +
                   (f" and {o['decisions'][0].get('company')}" if o.get("decisions") else ""))
        return {"to_name": o.get("to_name"), "subject": subject, "body": body, "context_extra": None}
    if o.get("kind") == "letter":
        # The quarterly letter from the fund's own figures; the partner's words and the deals stay as marked gaps.
        inp = o.get("inputs") or {}
        lines = []
        for f in inp.get("funds") or []:
            size = f"${f['size_usd'] / 1e6:.0f}M" if f.get("size_usd") else "[fund size]"
            lines.append(f"{f.get('name')}: {size}, {f.get('called_pct')}% called" if f.get("called_pct") is not None else f"{f.get('name')}: {size}")
        port, watch = [], []
        from datetime import date as _d  # noqa: E402

        def month_(m: str | None) -> str:
            try:
                y, mo = str(m or "").split("-")[:2]
                return _d(int(y), int(mo), 1).strftime("%b %Y")
            except (ValueError, TypeError):
                return str(m or "")
        flag_by = {x.get("company"): x for x in inp.get("flags") or []}

        def why(x: dict) -> str:  # the flag and its figure: why the company is on the watch list
            head_, det_ = str(x.get("headline") or "").strip(), str(x.get("detail") or "").strip().rstrip(".")
            return head_ + (f" ({det_})" if det_ and det_.lower() != head_.lower() else "")
        for r in (inp.get("portfolio") or [])[:15]:
            if r.get("revenue_usd") and r.get("plan_revenue_usd"):
                gap = (r["revenue_usd"] - r["plan_revenue_usd"]) / r["plan_revenue_usd"] * 100
                rev = (f"${r['revenue_usd'] / 1e3:.0f}K revenue in {month_(r.get('month'))}, "
                       + (f"{gap:.0f}% ahead of plan" if gap >= 0.5 else f"{-gap:.0f}% behind plan" if gap <= -0.5 else "on plan"))
                # A company well behind plan, or flagged, is on the watch list with the reason first, never among the highlights.
                if r["company"] in flag_by:
                    # The flag first; the month's revenue only when the flag is about something else (never the miss twice).
                    about_rev = re.search(r"\brevenue\b", str(flag_by[r["company"]].get("headline") or ""), re.I)
                    watch.append(f"- {r['company']}: {why(flag_by[r['company']])}" + ("" if about_rev else f". {rev[:1].upper()}{rev[1:]}"))
                elif gap <= -10:
                    watch.append(f"- {r['company']}: {-gap:.0f}% behind its revenue plan (${r['revenue_usd'] / 1e3:.0f}K in {month_(r.get('month'))})")
                else:
                    port.append(f"- {r['company']}: {rev}")
        named_ = {w.split(":")[0][2:] for w in watch}
        watch += [f"- {x['company']}: {why(x)}" for x in (inp.get("flags") or [])[:4] if x.get("company") not in named_]
        body = (f"Hi {first},\n\nHere is the Q3 LP letter draft for your review. Numbers come from the KPI history and the LP list; "
                "the brackets are yours to fill.\n\nFund summary\n" + ("\n".join(lines) or "[fund figures]") +
                "\n\nPortfolio highlights\n" + ("\n".join(port) or "[highlights]") +
                ("\n\nWatch list\n" + "\n".join(watch) if watch else "") +
                "\n\nNew investments\n[the quarter's new investments]\n\nFollow-ons and markdowns\n[follow-ons and markdowns]"
                "\n\nExits\n[none this quarter, or the exit]\n\nPipeline and market\n[In your words: what this quarter meant]"
                f"\n\nAsks\n[what we need from our LPs]\n\n{user_first}")
        return {"to_name": o.get("to_name"), "subject": f"{o.get('quarter') or 'Q3'} LP letter: draft for your review", "body": body,
                "context_extra": "Check every number against Carta before it goes to LPs"}
    if o.get("kind") == "lp_call":
        # A capital call still unpaid after two weeks: a polite note to the LP's contact, the amount and the date only.
        from datetime import date as _d  # noqa: E402
        when = _d.fromisoformat(o["call_date"]) if o.get("call_date") else None
        when_txt = f"{when.day} {when.strftime('%b')}" if when else "our last"
        amt = o.get("outstanding_usd") or 0
        amt_txt = f"${amt / 1e6:.2f}M".replace(".00M", "M") if amt >= 1e6 else f"${amt / 1e3:.0f}K"
        if o.get("again"):  # the second, shorter note: what is still due, and when you wrote
            sent_ = _d.fromisoformat(o["chased_on"]) if o.get("chased_on") else None
            body = (f"Hi {first},\n\nFollowing up on my note of {sent_.day} {sent_.strftime('%b')} " if sent_ else f"Hi {first},\n\nFollowing up on my last note ") + \
                (f"about the {o.get('fund') or 'fund'} capital call of {when_txt}: {amt_txt} is still to come from {o.get('lp')}. "
                 f"Could you let me know when we should expect it?\n\n{user_first}")
        else:
            body = (f"Hi {first},\n\nA quick note on the {o.get('fund') or 'fund'} capital call of {when_txt}: our records show {amt_txt} still to "
                    f"come from {o.get('lp')}. Could you let me know when we should expect it? Happy to resend the wire details if that helps.\n\n{user_first}")
        return {"to_name": o.get("to_name"), "subject": f"{o.get('fund') or 'Fund'}: capital call of {when_txt}", "body": body,
                "context_extra": "Check the amount against Carta before you send"}
    if o.get("kind") == "question":
        # Their question, answered in their thread. Only the user knows a timeline or a decision: one line to fill.
        q = str(o.get("question") or "")
        gap = ("[The timeline, in one line: diligence, partner meeting, term sheet]" if re.search(r"\btimeline|how long|when\b", q, re.I)
               else "[The answer, in one line]")
        body = (f"Hi {first},\n\nSorry for the slow reply" + (f" on your question: {q}" if q else ".") +
                f"\n\n{gap}\n\nHappy to talk it through on a call.\n\n{user_first}")
        subj = str(o.get("subject") or o.get("company") or "")
        return {"to_name": o.get("to_name") or o.get("company"), "subject": subj if subj.lower().startswith("re:") else f"Re: {subj}",
                "body": body, "context_extra": "ant. found no written answer in your notes or the CRM. Fill in the line before you send"}
    if o.get("kind") == "inbound_reply":
        company = o.get("company") or "your company"
        missing = [str(x) for x in o.get("missing") or []]
        if o.get("decision") == "call" or (o.get("revisit_check") or {}).get("met"):
            back = (o.get("revisit_check") or {}).get("evidence")
            lead = f"Good to see {back}: that was the bar we set when we last spoke. " if back else "It fits what we back, and we would like to hear more. "
            body = f"Hi {first},\n\nThanks for sending {company} our way. {lead}Would {slots[0]} or {slots[1]} IST work for a 30-minute call?\n\n{user_first}"
            subject, extra = f"Re: {company}", "Slots from your calendar"
        elif o.get("decision") == "more_info":
            asks = [ASK_FOR.get(m.lower(), "") for m in missing]
            if any(m.lower().startswith("adjacent") for m in missing):
                asks.append("which banks, lenders or other financial firms use it today")
            asks = [a for a in asks if a] or ["a short note on your customers and revenue so far"]
            body = (f"Hi {first},\n\nThanks for sending {company}. Before we take a call, could you share " +
                    (", ".join(asks[:-1]) + " and " + asks[-1] if len(asks) > 1 else asks[0]) + f"?\n\n{user_first}")
            subject, extra = f"Re: {company}", None
        else:
            # The engine's own deciding reason, said kindly; never a score, never a reason that did not decide it.
            why = o.get("why_pass") or "it sits outside the sectors we invest in"
            reason = why[:1].upper() + why[1:]
            body = (f"Hi {first},\n\nThank you for thinking of us for {company}. {reason}, so we will pass for now. "
                    f"If your plans change, we would be glad to hear from you again.\n\n{user_first}")
            subject, extra = f"Re: {company}", None
    else:
        what = str(o.get("what") or "").rstrip(".")
        low = what[:1].lower() + what[1:]
        m = re.match(r"^(send|share|forward)\s+(the\s+|our\s+|my\s+)?(.+)$", what, re.I)
        if m:
            thing = m.group(3)
            article = "our" if (m.group(2) or "").strip().lower() == "our" else "the"
            verb = "are" if re.search(r"[^s]s$", thing.split(" ")[0] if " on " in thing or " after " in thing else thing) else "is"
            if re.match(r"^(feedback|view|views|answer|thoughts|decision|update)\b", thing, re.I):
                # Words only the user can supply: the draft gives the email its shape, one short line to fill per part,
                # and says where ant. looked.
                kind = thing.split(" ")[0].lower()
                parts = {"feedback": ["[Where we landed, in one line]", "[What we liked]", "[What we would want to see next]"],
                         "view": ["[Our view, in one line]", "[The one or two reasons]", "[What would change our mind]"],
                         "views": ["[Our view, in one line]", "[The one or two reasons]", "[What would change our mind]"],
                         "answer": ["[The answer, in one line]", "[The source, with its clause or page]"],
                         "decision": ["[The decision, in one line]", "[The reason]", "[What happens next]"]}.get(
                    kind, ["[The main point, in one line]", "[The detail they need]"])
                body = (f"Hi {first},\n\nAs promised, here {verb} {article} {thing}.\n\n" + "\n".join(parts) +
                        f"\n\nHappy to talk it through.\n\n{user_first}")
                extra = f"ant. found no written {kind} in your notes or Drive. Fill in the {len(parts)} lines before you send" + \
                    (f". Check the firm's view with {_first(o['holder'])}, who sponsors the deal" if o.get("holder") else "")
            else:
                body = f"Hi {first},\n\nAs promised, here {verb} {article} {thing}.\n\n{user_first}"
                extra = f"Attach the {thing} before you send" if DOCS.search(thing) else None
        elif re.match(r"^(schedule|set up|book|arrange)\b", what, re.I) and o.get("with"):
            names = " and ".join(_first(w.get("name")) for w in o["with"])
            body = (f"Hi {first},\n\nAs promised, let's {low}. I have copied {names} here. Could you share two or three times that "
                    f"suit you next week?\n\n{user_first}")
            extra = f"{names} {'are' if len(o['with']) > 1 else 'is'} copied in and {'pick' if len(o['with']) > 1 else 'picks'} the time"
        elif re.match(r"^(schedule|set up|book|arrange)\b", what, re.I):
            body = (f"Hi {first},\n\nAs promised, let's {low}. Would {slots[0]} or {slots[1]} IST work for you?\n\n{user_first}")
            extra = "Slots from your calendar"
        else:
            body = f"Hi {first},\n\nFollowing up as promised: {low}.\n\n{user_first}"
            extra = None
        # The subject names the company and the thing in the reader's words, never the task line.
        thing_ = re.sub(r"^(send|share|forward|model|prepare|draft|write|review|set up|schedule|book|arrange)\s+(the\s+|my\s+)?", "",
                        what, flags=re.I)
        thing_ = re.sub(r"\s+after the (partner meeting|call|meeting)$", "", thing_, flags=re.I)
        if re.match(r"^(feedback|view|views|thoughts|decision|answer)\b", thing_, re.I):
            thing_ = "our " + thing_
        subject = f"{o['company']}: {thing_[:1].lower()}{thing_[1:]}" if o.get("company") else f"{thing_[:1].upper()}{thing_[1:]}"
    return {"to_name": o.get("to_name") or o.get("company"), "subject": subject, "body": body, "context_extra": extra}


def _redate(body: str, words: list, now_iso: str) -> str:
    """Days a draft named that no longer hold, as a date two working days out (never the day it is read), keeping the
    lead word: "this week" becomes "by Mon 2 Nov", "by Tue 27 Oct" becomes "by Mon 2 Nov", "Thu 29 Oct" "by Mon 2 Nov"."""
    from datetime import datetime, timedelta  # noqa: E402
    d, n = datetime.fromisoformat(now_iso).date(), 0
    while n < 2:
        d += timedelta(days=1)
        n += d.weekday() < 5
    lab = f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"
    body = re.sub(r"\s*(when|once) we (meet|speak|talk) today\.", " on a call if useful.", body)
    for w in words:
        lead = re.match(r"^(by|before|until|till|no later than|on or before)\s+", str(w), re.I)
        repl = {"tomorrow": f"on {lab}", "today": f"on {lab}", "this week": f"by {lab}", "end of the week": lab,
                "end of this week": lab, "next week": f"the week of {lab}"}.get(
            str(w).lower(), f"{lead.group(1)} {lab}" if lead else f"by {lab}" if re.search(r"\d", str(w)) else lab)
        body = re.sub(rf"\b(later |by |until |on )?{re.escape(str(w))}\b", repl, body, count=1, flags=re.I)
    return body


def _ask_owed(body: str, owe: list, user_first: str) -> str:
    """One line asking for what the reader owes you, before the sign-off, unless the draft already asks for it."""
    for t in owe[:1]:
        what = str(t.get("what") or "").rstrip(".")
        m = re.match(r"^(send|share|forward)\s+(.+)$", what, re.I)
        thing = m.group(2) if m else what
        if not thing or thing.lower() in body.lower():
            continue
        # Already asked in other words ("the venue shortlist" for "a shortlist of venues"): its key words are in an ask.
        keys_ = {w_ for w_ in re.findall(r"[a-z]{4,}", thing.lower()) if w_ not in ("send", "share", "when", "have", "with", "from", "your")}
        asks_ = [ln for ln in body.splitlines() if re.search(r"\b(could you|can you|please|send|share)\b", ln, re.I)]
        if keys_ and any(all(re.search(rf"\b{re.escape(k_[:-1] if k_.endswith('s') else k_)}", ln.lower()) for k_ in keys_) for ln in asks_):
            continue
        line = f"Could you also send {thing} when you have it?" if m else f"Could you also {what[:1].lower() + what[1:]}?"
        tail = f"\n\n{user_first}"
        body = body[:-len(tail)] + f"\n\n{line}" + tail if body.endswith(tail) else body + f"\n\n{line}"
    return body


def _also_line(body: str, what: str, user_first: str) -> str:
    """One line before the sign-off keeping a promise with no date: "Invite Rahul to the founders dinner" reads "I would
    also love you to join the founders dinner"."""
    m = re.match(r"^invite\s+\S+\s+to\s+(.+)$", what.strip().rstrip("."), re.I)
    line = f"I would also love you to join {m.group(1)}: I will send the details." if m else f"And as promised: {what[:1].lower() + what[1:].rstrip('.')}."
    if line.lower()[:40] in body.lower():
        return body
    tail = f"\n\n{user_first}"
    return body[:-len(tail)] + f"\n\n{line}" + tail if body.endswith(tail) else body + f"\n\n{line}"


def demo_drafts(member: str, owed: list[dict], now_iso: str, user_first: str | None = None) -> dict:
    """Drafts for everything the morning brief owes: the hand-written ones where they exist, a sourced template for the
    rest. Kept in Home, as on a Gmail connector with no create-draft tool: Open in Gmail fills a new message. A draft whose
    times passed gets two new ones; a draft written before a meeting with that person is brought up to date."""
    from datetime import datetime  # noqa: E402
    out = {}
    needs = [o for o in owed if o.get("old_slots") or
             (o.get("kind") == "inbound_reply" and (o.get("decision") == "call" or (o.get("revisit_check") or {}).get("met"))) or
             (o.get("kind") in (None, "promise") and not o.get("with") and re.match(r"^(schedule|set up|book|arrange)\b", str(o.get("what") or ""), re.I))]
    avoid = {x for o in owed for x in (o.get("avoid_slots") or []) + (o.get("old_slots") or [])}
    pool = free_slots(member, now_iso, 2 * len(needs), avoid) if needs else []
    for o in owed:
        k = needs.index(o) if o in needs else -1
        mine = (pool[2 * k], pool[2 * k + 1]) if k >= 0 and len(pool) > 2 * k + 1 else tuple((x, "") for x in SLOTS)
        labels = (mine[0][0], mine[1][0])
        if o.get("kind") == "reslot":
            body = _swap_slots(str(o.get("body") or ""), o.get("old_slots") or [], labels)
            d = {"to_name": o.get("to_name"), "subject": o.get("subject"), "body": body, "context_extra": None}
        elif o.get("kind") == "redate":
            # A day it named has come or gone: it moves two working days out.
            words_ = o.get("words") or []
            # A passed date never stays, whoever set it: one the user set also gets a line that owns the delay.
            body = _redate(str(o.get("body") or ""), words_, now_iso)
            if o.get("set_by") == "you":
                if any(re.search(r"\d", str(w_)) for w_ in words_) and "sorry this is late" not in body.lower():
                    tail_ = f"\n\n{user_first or member.capitalize()}"
                    body = body[:-len(tail_)] + "\n\nI am sorry this is late." + tail_ if body.endswith(tail_) else body + "\n\nI am sorry this is late."
            d = {"to_name": o.get("to_name"), "subject": o.get("subject"), "body": body, "context_extra": None}
        elif o.get("kind") == "narrow" and (o.get("dropped") or o.get("received")) and o.get("promises"):
            # One email for several promises, one closed since: the same email without the closed one's paragraphs, and
            # without the line asking for what already came in.
            stop_ = ("the", "and", "for", "two", "with", "send", "share", "our", "your", "when", "have")
            keys_ = {w_ for x_ in o.get("dropped") or [] for w_ in re.findall(r"[a-z]{3,}", str(x_.get("what") or "").lower()) if w_ not in stop_}
            got_ = {w_ for x_ in o.get("received") or [] for w_ in re.findall(r"[a-z]{4,}", str(x_.get("what") or "").lower()) if w_ not in stop_}
            paras_ = str(o.get("body") or "").split("\n\n")
            kept_ = [x_ for i_, x_ in enumerate(paras_) if i_ == 0 or i_ == len(paras_) - 1 or not (
                any(re.search(rf"\b{re.escape(k_)}", x_.lower()) for k_ in keys_) or
                (re.search(r"\b(could you|can you|please)\b", x_, re.I) and any(re.search(rf"\b{re.escape(k_)}", x_.lower()) for k_ in got_)))]
            d = {"to_name": o.get("to_name"), "subject": o.get("subject"), "body": "\n\n".join(kept_), "context_extra": None}
        elif o.get("kind") == "narrow":
            # A nudge whose asks moved on: the same nudge, for the asks still waiting, in the same thread.
            d = {**template_draft({**o, "kind": "ask_nudge"}, user_first or member.capitalize(), labels), "subject": o.get("subject")}
        elif o.get("kind") == "refresh":
            met = datetime.fromisoformat(o["met_on"])
            lines = str(o.get("body") or "").split("\n\n", 1)
            rest = lines[1] if len(lines) > 1 else ""
            rest = re.sub(r"\s*(when|once) we meet (today|tomorrow|on \w+)\.", " on a call if useful.", rest)
            met_ = list(dict.fromkeys(_first(n) for n in o.get("met_with") or []))
            greet = lines[0].lower()
            named = re.findall(r"[A-Z][a-z]+", lines[0][3:])
            # The greeting's own names ("Sid" for Siddharth): who was in the room, and who was not.
            there = [w for w in named if any(x.startswith(w) or w.startswith(x) for x in met_)] or (met_ if not named else [])
            others = [w for w in named if w not in there]
            when = f"{met.strftime('%a')} {met.day} {met.strftime('%b')}"
            if there and others:  # an intro to two people: only the one in the room hears "good to see you"
                hello = f"{' and '.join(there)}, good to see you on {when}. "
            elif there or not greet:
                hello = f"Good to see you on {when}. "
            else:
                hello = ""
            body = lines[0] + "\n\n" + hello + rest
            body = _swap_slots(body, o.get("old_slots") or [], labels)
            if o.get("slots"):  # times still ahead stay as offered
                mine = tuple((_slot_label(x), x) for x in o["slots"][:2]) + mine[len(o["slots"][:2]):]
                k = 0
            d = {"to_name": o.get("to_name"), "subject": o.get("subject"), "body": body, "context_extra": None}
        elif o.get("join") and o.get("undated"):
            # A promise with no date joins the draft already waiting for that person: that email, and one line for it.
            j_ = o["join"]
            d = {"to_name": o.get("to_name"), "subject": j_.get("subject"), "body": str(j_.get("body") or ""), "context_extra": None}
        else:
            key = str(o.get("what") or o.get("company") or "").lower()
            d = ((DEMO_DRAFTS.get(member) or {}).get(key) if o.get("kind") != "ask_nudge" else None) or \
                template_draft(o, user_first or member.capitalize(), labels)
        for ap_ in o.get("also_promises") or []:  # an undated promise to the same person rides in this email, in one line
            d = {**d, "body": _also_line(str(d.get("body") or ""), str(ap_.get("what") or ""), user_first or member.capitalize())}
        context = o.get("context") or ""
        if d.get("context_extra"):
            context = (context + ". " if context else "") + d["context_extra"]
        if o.get("kind") in ("refresh", "reslot") and o.get("old_context"):
            # A rewrite keeps what the old note asked of the user ("Fill in the 3 lines"), then adds its own check.
            kept_ = [x.strip().rstrip(".") for x in re.split(r"(?<=\.)\s+", str(o["old_context"]))
                     if (re.match(r"^(Fill in|Attach|Add|Check)\b", x.strip()) or "before you send" in x) and
                     not re.match(r"^(Written before|The times)\b", x.strip()) and not ("firm's view" in x and "firm's view" in context)
                     and x.strip().rstrip(".").lower() not in context.lower()]
            if kept_:
                head_, _, tail_ = context.partition(". Check the firm's view")
                context = head_ + "".join(f". {k_}" for k_ in kept_) + (f". Check the firm's view{tail_}" if tail_ else "")
        body = d["body"].replace("{first}", _first(o.get("to_name"))).replace("{slot1}", labels[0]).replace("{slot2}", labels[1])
        body = _ask_owed(body, o.get("they_owe") or [], user_first or member.capitalize())
        slots = [iso for (lab, iso) in mine if iso and lab in body] if k >= 0 else []
        out[o["id"]] = {"to": o.get("to"), "cc": d.get("cc") or o.get("cc"), "to_name": d.get("to_name") or o.get("to_name") or o.get("company"),
                        "subject": d["subject"], "body": body, "context": context, "slots": slots or None,
                        "commitment_id": o.get("commitment_id"), "commitment_ids": o.get("commitment_ids"),
                        "inbound_id": o.get("inbound_id"), "question_id": o.get("question_id"),
                        "action_id": o.get("action_id"), "note_kind": o.get("note_kind"), "action_ids": o.get("action_ids"),
                        "note_kinds": o.get("note_kinds"),
                        **({"asks_for": [t_.get("commitment_id") for t_ in o.get("they_owe") or [] if isinstance(t_, dict) and t_.get("commitment_id")]}
                           if o.get("they_owe") else {}),
                        **({"kind": "holder", "holds": [w_.get("draft") for w_ in o.get("items") or [] if w_.get("draft")],
                            "decisions": [{k_: x_.get(k_) for k_ in ("deal_id", "company", "deadline", "what")} for x_ in o.get("decisions") or []]}
                           if o.get("kind") == "holder" else {}),
                        "source_label": o.get("source_label") or "Meeting notes", "source_url": o.get("source_url"),
                        "in_gmail": False, "made_at": now_iso, "updated_at": now_iso}
        out[o["id"]] = {k_: v for k_, v in out[o["id"]].items() if v is not None}
    return out


def extras(member: str, now_iso: str) -> dict:
    if member == "vikram":
        # Banyan is Vikram's LP: the touch he tapped "Draft a note" on yesterday, written by the pulse and kept in Home.
        from instinct.util import sid  # noqa: E402
        drafts = {
            "dr_banyan": {
                "to_name": "Kunal at Banyan Family Office", "to": "kunal@banyanfo.in", "subject": "Quillwater Fund II: time before your re-up window?",
                "context": "No touch since 03 Aug. Their re-up window opens 05 Jan.", "action_id": sid("lp", "lp_banyan", "window", prefix="l"),
                "body": ("Hi Kunal,\n\nIt has been a while since we last spoke in August. Before your re-up window opens in January, I would "
                         "like to walk you through the Fund II portfolio. Would 30 minutes in the week of 10 Nov work?\n\nBest,\nVikram"),
                "source_label": "CRM", "source_url": "https://quillwater.affinity.co/companies/c_org_banyan_family_office", "in_gmail": False},
        }
        return {"drafts": drafts, "proposals": {"as_of": now_iso, "items": {}}}
    if member not in ("aditi", "solo"):
        return {"proposals": {"as_of": now_iso, "items": {}}}
    drafts = {}
    proposals = {
        "pr_gravity_next": {
            "type": "crm_update", "status": "proposed",
            # A solo GP has no partner prep: the same change, from their own notes.
            "title": "next step from your notes on 15 Oct" if member == "solo" else "next step from the partner prep on 15 Oct",
            "record": {"type": "deal", "id": "d_gravity", "name": "Gravity Payouts"},
            "fields": [{"field": "next_step", "current": "Decide on Monday" if member == "solo" else "Partner meeting Monday",
                        "proposed": "Reference calls with three gig platforms"},
                       {"field": "next_step_due", "current": "2026-10-26", "proposed": "2026-10-24"}],
            "source_label": "Meeting notes", "source_url": "https://notes.granola.ai/d/tr02"},
    }
    return {"drafts": drafts, "proposals": {"as_of": now_iso, "items": proposals}}


ASKS = [
    {"company": "Nimbus Collect", "company_id": "c_nimbus", "ask": "Intro to two banks as customers", "who": "Divya Raman", "kind": "intro",
     "date": "2026-10-13", "source_label": "Email", "source_url": "https://mail.google.com/mail/u/0/#all/th0343"},
    {"company": "Orbit Treasury", "company_id": "c_orbit", "ask": "Intros to senior engineers, two hires this quarter", "who": "Vikram Rao", "kind": "hiring",
     "date": "2026-10-11", "source_label": "Founder update", "source_url": "https://mail.google.com/mail/u/0/#all/upd_orbit"},
    {"company": "Kestrel Pay", "company_id": "c_kestrel", "ask": "Intros to senior engineers, two hires this quarter", "who": "Neel Bhatt", "kind": "hiring",
     "date": "2026-10-08", "source_label": "Founder update", "source_url": "https://mail.google.com/mail/u/0/#all/upd_kestrel"},
]


def preread_markdown(res: dict) -> str:
    """The Sunday pre-read as pipeline-watch writes it: built only from what the engine found, every line linked."""
    parts = res["parts"]
    lines = ["## Decisions needed"]
    for d in parts.get("decisions") or []:
        lines.append(f"- [{d['company']}]({d.get('source_url')}): {d['why']}")
    flags = parts.get("portfolio_flags") or []
    if flags:
        lines.append("## Portfolio flags")
        for f in flags[:4]:
            lines.append(f"- [{f['company']}]({f.get('source_url')}): {f['headline']}, {f['detail']}")
    calls = [r for r in parts.get("inbound") or [] if r.get("decision") == "call"][:3]
    if calls:
        lines.append("## Inbound worth discussing")
        for r in calls:
            lines.append(f"- [{r['company']}]({r.get('source_url')}): score {r['score']}" + (f", {r['facts']}" if r.get("facts") else ""))
    return "\n".join(lines)


def solo_bundle() -> dict:
    """Aditi's world as a one-person fund: no partners, and every pitch the firm received lands in her inbox."""
    b = load(os.path.join(GOLD, "bundles", "aditi.json"))
    b["firm"]["members"] = [m for m in b["firm"].get("members") or [] if m.get("email") == b["user"]["email"]]
    # A $30M solo fund writes smaller, earlier checks than the firm: its own thesis, not Quillwater's.
    th = dict(b.get("thesis") or {})
    th.update({"stages": ["pre-seed", "seed"], "check_min_usd": 250000, "check_max_usd": 1000000,
               "statement": ("A $30M solo fund backing India-first fintech infrastructure and B2B software for financial services, "
                             "pre-seed and seed, with first checks of $250K to $1M, in India and US-India cross-border. "
                             "No consumer lending without an in-house risk team, crypto trading platforms or D2C brands.")})
    b["thesis"] = th
    # A one-person fund: no partner meetings or syncs on the calendar, no CFO, and its own $30M Fund I with its LPs.
    dom = b["firm"]["domain"]
    me = b["user"]["email"]
    internal = {e["id"] for e in b["events"] if all(str(a.get("email") or "").endswith("@" + dom) for a in e.get("attendees") or [])
                and any(str(a.get("email") or "") != me for a in e.get("attendees") or [])}
    b["events"] = [e for e in b["events"] if e["id"] not in internal]
    b["transcripts"] = [t for t in b.get("transcripts") or [] if t.get("event_id") not in internal]
    b["firm"].update({"fund": "Fund I", "fund_size_usd": 30000000})
    scale = 30000000 / max(1, sum(int(l.get("commitment_usd") or 0) for l in b.get("lps") or []))
    for l in b.get("lps") or []:
        for k in ("commitment_usd", "called_usd", "paid_in_usd"):
            if l.get(k) is not None:
                l[k] = int(round(l[k] * scale / 10000.0) * 10000)
        l.update({"fund": "Fund I", "owner": me})
    # Her calendar and notes speak for one person too: a check-in, not a "partner check-in".
    def one_person(title: str) -> str:
        t = re.sub(r"\bpartner vote prep\b", "decision prep", str(title))
        t = re.sub(r"\bfirst partner call\b", "first call", t)
        return re.sub(r"\bpartner (check-in|prep)\b", r"\1", t)
    for e in b["events"]:
        e["title"] = one_person(e.get("title") or "")
    for t_ in b.get("transcripts") or []:
        t_["title"] = one_person(t_.get("title") or "")
    # Her CRM speaks for one person: every deal is hers, no colleague knows anyone, and no partner intro, partner vote
    # or IC on Monday.
    for d in (b.get("crm") or {}).get("deals") or []:
        d["owner"] = me
        d.pop("team", None)
    for p_ in (b.get("crm") or {}).get("people") or []:
        if isinstance(p_.get("strength_by_member"), dict):
            p_["strength_by_member"] = {k: v for k, v in p_["strength_by_member"].items() if k == me}
    for d in (b.get("crm") or {}).get("deals") or []:
        ns = str(d.get("next_step") or "")
        ns = re.sub(r"^Partner intro$", "Second call with the CEO", ns)
        ns = re.sub(r"^Partner vote$", "Your decision", ns)
        ns = re.sub(r"^(IC|Partner meeting) (on )?Monday$", "Decide on Monday", ns)
        if ns != str(d.get("next_step") or ""):
            d["next_step"] = ns
        if re.fullmatch(r"IC|Partner meeting", str(d.get("stage") or "")):
            d["stage"] = "Decision"
    pitches = {p["thread_id"] for p in load(os.path.join(CASES, "inbound.json"))["pitches"]}
    have = {t["id"] for t in b["threads"]}
    for m in ("rohan", "kabir", "meera"):
        for t in load(os.path.join(GOLD, "bundles", f"{m}.json"))["threads"]:
            if t["id"] in pitches and t["id"] not in have:
                b["threads"].append(t)
                have.add(t["id"])
    return b


_SHARED: list[dict] | None = None


def shared_notes() -> list[dict]:
    """Wednesday evening at the fictional fund: each deal owner tapped Share on their competing funds, and the pulse
    wrote one CRM note per deal. Every member's ant. reads them on Thursday, so the sync pack is the same for all."""
    global _SHARED
    if _SHARED is None:
        notes: dict[str, dict] = {}
        levels = load(os.path.join(CASES, "levels.json"))
        for m in ("aditi", "kabir", "meera", "rohan"):
            b = load(os.path.join(GOLD, "bundles", f"{m}.json"))
            with tempfile.TemporaryDirectory() as tmp:
                dump(b, os.path.join(tmp, "b.json"))
                import contextlib
                import io
                with contextlib.redirect_stdout(io.StringIO()):
                    cli.main(["setup", "--bundle", os.path.join(tmp, "b.json"), "--out", tmp, "--level", levels[m]])
                config = load(os.path.join(tmp, "config.json"))
            res = cli.build_all(b, config, {"snap": {}, "state": {}, "ratings": [], "versions": {}}, truth_extraction(), None, None, "daily")
            for k, v in res["snaps"]["proposals"]["items"].items():
                did = v["record"]["id"]
                if k.startswith("share_") and did not in notes:
                    notes[did] = {"id": f"note_shared_{did}", "deal_id": did, "text": v["fields"][0]["proposed"],
                                  "url": f"https://quillwater.affinity.co/notes/shared_{did}", "date": "2026-10-21T19:00:00+05:30"}
        _SHARED = list(notes.values())
    return [dict(n) for n in _SHARED]


def build(member: str = "aditi", home_url: str | None = None) -> dict[str, dict]:
    b = solo_bundle() if member == "solo" else load(os.path.join(GOLD, "bundles", f"{member}.json"))
    if member != "solo":
        b.setdefault("crm", {}).setdefault("notes", []).extend(shared_notes())
    b["demo"] = True
    level = "solo_gp" if member == "solo" else load(os.path.join(CASES, "levels.json"))[member]
    with tempfile.TemporaryDirectory() as tmp:
        bpath = os.path.join(tmp, "bundle.json")
        dump(b, bpath)
        import contextlib
        import io
        with contextlib.redirect_stdout(io.StringIO()):
            cli.main(["setup", "--bundle", bpath, "--out", tmp, "--level", level, "--home-url", home_url or "https://claude.ai/artifact/demo"])
        config = load(os.path.join(tmp, "config.json"))
    config["demo"] = True
    home = {"snap": {}, "state": {}, "ratings": [], "versions": {}}
    res = cli.build_all(b, config, home, truth_extraction(), inbound_for(b), None, "setup", None, {"asks": ASKS})
    snaps = res["snaps"]
    if member in ("aditi", "kabir"):
        snaps["digests"] = {"as_of": snaps["brief"]["as_of"], "items": {"preread": {
            "kind": "preread", "title": "Partner meeting pre-read", "markdown": preread_markdown(res), "as_of": "2026-10-18T18:00:00+05:30"}}}
    for card in snaps["prep"]["cards"].values():
        company = (card.get("who") or "").split(", ")[-1]
        if company in QUESTIONS:
            card["questions"] = QUESTIONS[company]
    ex = extras(member, snaps["brief"]["as_of"])
    who = "aditi" if member == "solo" else member
    user_first = _first((b.get("user") or {}).get("name"))
    drafts = {**demo_drafts(who, res["report"].get("owed") or [], snaps["brief"]["as_of"], user_first),
              **(ex.pop("drafts", {}) or {})}
    snaps["drafts"] = {"as_of": snaps["brief"]["as_of"], "items": drafts}
    cli.link_drafts(snaps["brief"], drafts)
    for doc_ in ("asks", "portfolio"):  # as the drafts command does
        cli.ready_hero(snaps.get(doc_), set(drafts), drafts)
    snaps.update(ex)
    snaps["scorecard"] = {"week": "2026-W43", "overall": 9, "catches": 4, "prep_on_time": "11/11", "commitments_closed": "7/8",
                          "crm_clean": "5/6", "noise": "3/41",
                          "change_note": "ant. now shows more signal items because you rated them: 6 useful, 0 not useful, 0 wrong.", "history": []}
    # What the demo fund has connected: Home's Settings shows these, and offers the rest.
    snaps["connectors"] = {"checked_at": snaps["brief"]["as_of"], "items": [
        {"name": "Gmail", "category": "email", "ok": True}, {"name": "Google Calendar", "category": "calendar", "ok": True},
        {"name": "Granola", "category": "notes", "ok": True}, {"name": "Affinity", "category": "crm", "ok": True},
        {"name": "Google Drive", "category": "drive", "ok": True}]}
    # Granola gives a summary with most notes: two demo notes carry one, the rest show "Write a TL;DR" in the side panel.
    for nid, text in (("tr03", "- Atlas wants our markup before 23 Oct; Bluepeak's term sheet is on the table.\n- Two terms matter most to them: the board seat and the option pool.\n- You owe the markup; they owe legal counsel's contact."),
                      ("tr13", "- Runway is under 9 months on the current plan.\n- The board will ask for a plan past 12 months.\n- The September MIS is late; the founder will send it before the board.")):
        if nid in ((snaps.get("notes") or {}).get("items") or {}):
            snaps["notes"]["items"][nid]["summary"] = text
    return snaps


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--member", default="aditi")
    ap.add_argument("--out", default=os.path.join(ROOT, "evals", "runs", "demo"))
    ap.add_argument("--home-url")
    a = ap.parse_args()
    snaps = build(a.member, a.home_url)
    os.makedirs(a.out, exist_ok=True)
    plan = homedb.write_plan(snaps, {"versions": {}}, a.out)
    dump(snaps, os.path.join(a.out, "snaps.json"))
    print(json.dumps({"documents": plan["documents"], "batch": os.path.join(a.out, "home", "batch.json")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
