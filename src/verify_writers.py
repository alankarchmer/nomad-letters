"""Check the drafted notes and answers before they go on the page.

  1. Copying: flag any run of 5+ consecutive words shared with the source text (terms of art allowed).
  2. Grounding: Jev judges each note / answer sentence against its source passages
     (Choice supports / contradicts / says_nothing, as in the fact-check).

  python3 verify_writers.py          copy check + dry-run counts
  python3 verify_writers.py --live   also ask Jev (cached)
"""
import asyncio, json, os, re, sys
from pathlib import Path
import jev_pipeline as jp

S = Path(__file__).resolve().parent
from paths import DATA, PRIVATE
ALLOWED = ["scale economics shared", "scale efficiencies shared", "destination analysis", "robustness ratio", "super-high-quality thinkers",
           "super high-quality thinkers", "equity yield curve", "terminal portfolio", "price-to-value ratio", "galactic hq", "locker room culture",
           "longevity of compound", "x-amount", "santa fe institute", "games workshop", "nebraska furniture mart", "international speedway"]


def words(t):
    t = t.lower().replace("’", "'").replace("‘", "'")
    for a in ALLOWED: t = t.replace(a, " ")
    return re.findall(r"[a-z0-9']+", t)


def shared_runs(text, src, n=5):
    a, b = words(text), words(src)
    grams = {tuple(b[i:i + n]) for i in range(len(b) - n + 1)}
    return [" ".join(a[i:i + n]) for i in range(len(a) - n + 1) if tuple(a[i:i + n]) in grams]


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+(?=[A-Z‘“])", t.strip()) if len(s.split()) >= 4]


def items():
    wp_in = json.load(open(PRIVATE / "writer_paths.json")); wa_in = json.load(open(PRIVATE / "writer_ask.json"))
    wp = json.load(open(DATA / "writer_paths_out.json")); wa = json.load(open(DATA / "writer_ask_out.json"))
    out = []
    for cid, blk in wp_in["paths"].items():
        for p in blk["paragraphs"]:
            note = wp["paths"].get(p["ref"])
            out.append(dict(kind="path", ref=p["ref"], text=note, sources=[p["text"]]))
    for k, lst in wp_in["voice"].items():
        for p in lst:
            out.append(dict(kind="voice", ref=p["ref"], text=wp["voice"].get(p["ref"]), sources=[p["text"]]))
    for q in wa_in:
        w = wa.get(q["qid"], {}); ans = w.get("answer")
        if not ans: out.append(dict(kind="ask", ref=q["qid"], text=None, sources=[])); continue
        used = [p for p in q["passages"] if p["n"] in set(w.get("used") or [])] or q["passages"]
        for k, s in enumerate(sentences(ans)):
            out.append(dict(kind="ask", ref=f"{q['qid']}#{k+1}", text=s, sources=[p["text"] for p in used], full=ans))
    return out


def jobs(its):
    return [dict(kind="verify", ref=it["ref"], state={"claim": it["text"], "passages": it["sources"]}, questions={"relation": jp.CLAIM_Q["relation"]})
            for it in its if it["text"]]


def main():
    its = items()
    missing = [it["ref"] for it in its if not it["text"]]
    print(f"items {len(its)}; missing/null {len(missing)}: {missing}")
    copy = []
    for it in its:
        if not it["text"]: continue
        runs = [r for src in it["sources"] for r in shared_runs(it["text"], src)]
        if runs: copy.append((it["ref"], sorted(set(runs))[:3]))
    print(f"copy check: {len(copy)} items share 5+ word runs with the source")
    for ref, r in copy: print("  ", ref, r)
    js = jobs(its)
    if "--live" in sys.argv:
        asyncio.run(jp.run_live(js))
    cache = jp.load_cache(); flags = []
    for j, it in zip(js, [i for i in its if i["text"]]):
        v = cache.get(jp.key_for(j["state"], j["questions"]))
        if not v: continue
        a = v["answers"]["relation"]
        if a["choice"] != "supports" or a["confidence"] < 0.6:
            flags.append((it["ref"], a["choice"], round(a["confidence"], 2), it["text"]))
    done = sum(1 for j in js if jp.key_for(j["state"], j["questions"]) in cache)
    print(f"grounding: {done}/{len(js)} judged; flagged {len(flags)}")
    for f in flags: print(f"  [{f[1]} {f[2]}] {f[0]}: {f[3]}")
    json.dump(dict(copy=copy, flags=flags), open(PRIVATE / "verify_writers.json", "w"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
