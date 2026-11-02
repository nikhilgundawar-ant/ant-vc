"""Fuzz the engine's text handling on untrusted strings: email bodies, sender fields, titles and memo sources.

Promise: no raise, no regex blow-up (libFuzzer's timeout catches that), and the documented return types.
"""
import os
import sys

import atheris

HERE = os.path.dirname(os.path.abspath(__file__))
for folder in (os.path.join(HERE, "engine"), os.path.join(HERE, "..", "engine")):
    if os.path.isdir(os.path.join(folder, "instinct")):
        sys.path.insert(0, folder)

with atheris.instrument_imports():
    from instinct import names, safety, util


def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    a = fdp.ConsumeUnicodeNoSurrogates(2048)
    b = fdp.ConsumeUnicodeNoSurrogates(512)

    hits = safety.detect_injection(a)
    assert all(isinstance(hit, str) and hit for hit in hits)
    safety.numbers_in(a)
    report = safety.check_memo([{"text": a, "source": "s"}], {"s": b})
    assert isinstance(report, dict)

    util.parse_dt(b)
    util.parse_date(b)
    assert isinstance(util.norm_email(b), str)
    assert isinstance(util.domain_of(b), str)
    util.is_freemail(b)
    assert isinstance(util.slug(a), str)
    assert len(util.clip(a, 80)) <= 81
    assert isinstance(util.fit_line(a), str)
    assert isinstance(util.fit_sentences(a, 120), str)
    assert isinstance(util.clean_title(b, a), str)
    assert isinstance(util.acronyms(a), str)

    assert isinstance(names.normalize_name(b), str)
    names.split_name(b)
    assert isinstance(names.name_from_email(b), str)
    assert isinstance(names.first_relation(a[:64], b[:64]), str)
    names.display_name([a[:64], b[:64]])


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
