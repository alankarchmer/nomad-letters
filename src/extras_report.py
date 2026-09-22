"""Aggregate cached Jev answers for the five extra features.

Writes:
  extras_results.json   data the page embeds (no letter text)
  writer_paths.json     paragraphs that need a one-line note (reading paths, voice highlights)
  writer_ask.json       questions with their best passages, for drafting answers
"""
import collections, json, re
from pathlib import Path
import jev_extras as X
import jev_pipeline as jp
import build

S = Path(__file__).resolve().parent
from paths import DATA, PRIVATE
P = X.PARAS
LBL = {l["id"]: (l["mon"] if "mon" in l else None) for l in build.L}
MON = {"06": "Jun", "12": "Dec"}


def label(doc_id):
    if doc_id == "preamble": return "2021 preamble"
    if doc_id == "postamble": return "2021 postscript"
    y, m = doc_id.split("-"); return f"{MON[m]} {y} letter"


def get(job):
    v = X.CACHE.get(jp.key_for(job["state"], job["questions"]))
    return v["answers"] if v else None


def exp_choice(probs, values):
    """Expected value over the options that carry a value, renormalised; plus the weight of evidence."""
    w = sum(probs.get(k, 0) for k in values)
    if w <= 0: return None, 0.0
    return sum(probs.get(k, 0) * v for k, v in values.items()) / w, w


def main(groups):
    out = {}

    # ---------------- reading paths
    cand = collections.defaultdict(list)
    for j in groups["paths"]:
        a = get(j)
        if not a: continue
        i = j["ref"]
        for cid, sc in a.items():
            cand[cid].append((sc["score"], X.idea_p(i, cid), i))
    paths, writer_paths = {}, {}
    for cid, rows in cand.items():
        rows.sort(key=lambda r: -(r[0] + 0.3 * r[1]))
        pick, used, texts = [], set(), set()
        for s, p, i in rows:
            key = re.sub(r"[^a-z]", "", P[i]["text"].lower())
            if P[i]["id"] in used or s < 1.3 or any(key[:150] in k2 or k2[:150] in key for k2 in texts): continue
            pick.append((s, p, i)); used.add(P[i]["id"]); texts.add(key)
            if len(pick) == 5: break
        pick.sort(key=lambda r: r[2])
        paths[cid] = [dict(ref=f"{cid}-{k+1}", i=i, letter=P[i]["letter"], page=P[i]["page"], score=round(s, 2)) for k, (s, p, i) in enumerate(pick)]
        writer_paths[cid] = dict(idea=X.IDEA_DESC[cid], paragraphs=[dict(ref=f"{cid}-{k+1}", source=label(P[i]["id"]), pdf_page=P[i]["page"], text=P[i]["text"]) for k, (s, p, i) in enumerate(pick)])
    out["paths"] = paths

    # ---------------- scorecard
    TRAITS = {
        "price": {"expensive": 0, "fair": 1 / 3, "discount": 2 / 3, "deep_discount": 1},
        "sharing": {"keeps": 0, "shares": 1},
        "owner": {"hired": 0, "owner": 1},
        "capital": {"poor": 0, "mixed": 0.5, "good": 1},
        "character": {"poor": 0, "good": 1},
    }
    per = collections.defaultdict(lambda: dict(n=0, roles=collections.Counter(), tr={t: [0.0, 0.0] for t in TRAITS}, view=[0.0, 0.0], by_letter=collections.defaultdict(lambda: [0.0, 0.0])))
    for j in groups["scorecard"]:
        a = get(j)
        if not a: continue
        i, key = j["ref"]; c = per[key]; c["n"] += 1
        for r, pr in a["role"]["probabilities"].items(): c["roles"][r] += pr
        for t, vals in TRAITS.items():
            v, w = exp_choice(a[t]["probabilities"], vals)
            if v is not None: c["tr"][t][0] += v * w; c["tr"][t][1] += w
        w = 1 - a["role"]["probabilities"].get("passing", 0)
        v = a["view"]["score"] / 3
        c["view"][0] += v * w; c["view"][1] += w
        bl = c["by_letter"][P[i]["letter"]]; bl[0] += v * w; bl[1] += w
    sc = []
    for r in build.Hrows:
        c = per.get(r["key"])
        if not c: continue
        tot = sum(c["roles"].values()) or 1
        roles = {k: round(v / tot, 3) for k, v in c["roles"].items()}
        traits = {t: (round(s / w, 3) if w >= 0.35 else None, round(w, 2)) for t, (s, w) in c["tr"].items()}
        view = (round(c["view"][0] / c["view"][1], 3) if c["view"][1] >= 0.35 else None, round(c["view"][1], 2))
        timeline = [round(c["by_letter"][li][0] / c["by_letter"][li][1], 3) if c["by_letter"].get(li) and c["by_letter"][li][1] >= 0.3 else None for li in range(24)]
        sc.append(dict(key=r["key"], n=c["n"], roles=roles, traits=traits, view=view, timeline=timeline))
    out["scorecard"] = sc

    # ---------------- influence
    inf = collections.defaultdict(lambda: dict(n=0, roles=collections.Counter(), links=collections.Counter(), letters=collections.Counter()))
    for j in groups["influence"]:
        a = get(j)
        if not a: continue
        i, key = j["ref"]; d = inf[key]; d["n"] += 1; d["letters"][P[i]["letter"]] += 1
        up = a["use"]["probabilities"]
        for r, pr in up.items(): d["roles"][r] += pr
        w = 1 - up.get("passing", 0)
        for cid, pr in a["idea"]["probabilities"].items():
            if cid != "none": d["links"][cid] += w * pr
    people = []
    for key, d in inf.items():
        if d["n"] < 2: continue
        tot = sum(d["roles"].values()) or 1
        people.append(dict(key=key, name=X.PEOPLE[key][0], n=d["n"], roles={k: round(v / tot, 3) for k, v in d["roles"].items()},
                           links={k: round(v, 3) for k, v in d["links"].items() if v >= 0.05}, letters=sorted(d["letters"])))
    people.sort(key=lambda p: -p["n"])
    out["influence"] = people

    # ---------------- voice
    vals = []
    for j in groups["voice"]:
        a = get(j)
        if not a: continue
        i = j["ref"]
        vals.append((i, a["humour"]["score"] / 2, a["candour"]["score"] / 2, a["critique"]["score"] / 2, a["story"]["noul"]))
    series = {k: [None] * 24 for k in ("humour", "candour", "critique", "story")}
    for li in range(24):
        rows = [(v, P[v[0]]["words"]) for v in vals if P[v[0]]["letter"] == li]
        wsum = sum(w for _, w in rows)
        for k, col in (("humour", 1), ("candour", 2), ("critique", 3), ("story", 4)):
            series[k][li] = round(sum(v[col] * w for v, w in rows) / wsum, 3)
    tops, writer_voice = {}, {}
    for k, col, n in (("humour", 1, 10), ("candour", 2, 6), ("critique", 3, 6)):
        ranked = sorted(vals, key=lambda v: -v[col]); pick, seen = [], set()
        for v in ranked:
            if P[v[0]]["id"] in seen: continue
            pick.append(v); seen.add(P[v[0]]["id"])
            if len(pick) == n: break
        pick.sort(key=lambda v: v[0])
        tops[k] = [dict(ref=f"{k}-{m+1}", i=v[0], letter=P[v[0]]["letter"], page=P[v[0]]["page"], value=round(v[col], 3)) for m, v in enumerate(pick)]
        writer_voice[k] = [dict(ref=f"{k}-{m+1}", source=label(P[v[0]]["id"]), pdf_page=P[v[0]]["page"], text=P[v[0]]["text"]) for m, v in enumerate(pick)]
    out["voice"] = dict(series=series, tops=tops)

    # ---------------- ask
    pool, cands = X.ask_candidates()
    ask, writer_ask = [], []
    jobs = {j["ref"]: j for j in groups["ask"]}
    for qid, q in X.ASK:
        a = get(jobs[qid])
        if not a: continue
        scored = sorted([(a[f"p{k}"]["score"], idx) for k, idx in enumerate(cands[qid])], reverse=True)
        hits = [(s, idx) for s, idx in scored if s >= 1.5][:6]
        partial = not hits
        if partial: hits = [(s, idx) for s, idx in scored if s >= 1.0][:2]
        entry = dict(qid=qid, q=q, partial=partial, answered=round(a["answered"]["noul"], 3),
                     hits=[dict(doc=pool[idx]["id"], letter=pool[idx]["letter"], page=pool[idx]["page"], score=round(s, 2)) for s, idx in hits])
        ask.append(entry)
        writer_ask.append(dict(qid=qid, question=q, passages=[dict(n=k, source=label(pool[idx]["id"]), pdf_page=pool[idx]["page"], relevance=round(s / 3, 2), text=pool[idx]["text"]) for k, (s, idx) in enumerate(hits)]))
    out["ask"] = ask

    out["letter_pages"] = [[min(p["page"] for p in P if p["letter"] == li), max(p["page"] for p in P if p["letter"] == li)] for li in range(24)]
    (DATA / "extras_results.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    (PRIVATE / "writer_paths.json").write_text(json.dumps(dict(paths=writer_paths, voice=writer_voice), ensure_ascii=False, indent=1))
    (PRIVATE / "writer_ask.json").write_text(json.dumps(writer_ask, ensure_ascii=False, indent=1))

    # console summary
    print("paths:", {cid: len(v) for cid, v in paths.items()})
    print("scorecard companies:", len(sc))
    for c in sorted(sc, key=lambda c: -(c["view"][0] or 0))[:6]:
        print(f"   {c['key']:<12} view {c['view'][0]}  traits " + " ".join(f"{t}={v[0]}" for t, v in c["traits"].items()))
    print("influence people:", [(p["name"], p["n"], max(p["links"], key=p["links"].get) if p["links"] else None) for p in people[:10]])
    print("voice humour by letter:", series["humour"])
    print("ask: answered", sum(1 for e in ask if e["answered"] >= 0.5), "of", len(ask), "; no strong hits:", [e["qid"] for e in ask if not e["hits"]])
