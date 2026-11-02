"""Fuzz the engine's first steps on a connector bundle: people resolution and the relationship graph.

Raw bytes rarely make a useful bundle, so this starts from a trimmed copy of a fictional golden bundle and lets the
fuzzer rewrite the text in its threads, events and transcripts: subjects, names, addresses, dates, bodies. That is the part an outsider controls by
sending an email or an invite. No such rewrite may crash the engine. The bundle's shape comes from ant.'s own steps,
so swapping a list for a number is out of scope here.
"""
import copy
import json
import os
import sys

import atheris

HERE = os.path.dirname(os.path.abspath(__file__))
for folder in (os.path.join(HERE, "engine"), os.path.join(HERE, "..", "engine")):
    if os.path.isdir(os.path.join(folder, "instinct")):
        sys.path.insert(0, folder)

with atheris.instrument_imports():
    from instinct import graph, stages
    from instinct.resolve import resolve_people

if os.path.isdir(os.path.join(HERE, "ontology")):  # the packaged fuzzer carries it next to this file
    stages.ROOT = HERE

for path in (os.path.join(HERE, "aditi.json"),
             os.path.join(HERE, "..", "evals", "golden", "bundles", "aditi.json")):
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            SEED = json.load(fh)
        break
for key in ("threads", "events", "transcripts", "lps", "portfolio_kpis", "passes", "empathy_maps"):
    if isinstance(SEED.get(key), list):
        SEED[key] = SEED[key][:6]
crm = SEED.get("crm")
if isinstance(crm, dict):
    for key, value in crm.items():
        if isinstance(value, list):
            crm[key] = value[:12]


def spots(node, out):
    """Every (container, key) that holds a string, so any text field can be rewritten."""
    pairs = node.items() if isinstance(node, dict) else enumerate(node) if isinstance(node, list) else ()
    for key, value in pairs:
        if isinstance(value, str):
            out.append((node, key))
        else:
            spots(value, out)
    return out


def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    bundle = copy.deepcopy(SEED)
    where = []
    for key in ("threads", "events", "transcripts"):  # outsiders reach these, never "now", "tz" or "user"
        spots(bundle.get(key), where)
    for _ in range(fdp.ConsumeIntInRange(1, 16)):
        container, key = fdp.PickValueInList(where)
        container[key] = fdp.ConsumeUnicodeNoSurrogates(128)
    graph.build(bundle, resolve_people(bundle))


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
