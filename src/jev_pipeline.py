"""Build-time Jev judgments for the Nomad Letters page.

Two jobs, both over the letter text:
  ideas   One request per paragraph: 16 Noul questions, one per idea in the page's Ideas grid.
          Code aggregates the probabilities into per-letter intensities and compares them with
          the hand-coded grid.
  claims  One request per factual sentence in the page's summaries, stories and holding notes:
          a Choice (supports / contradicts / says_nothing) over the best-matching paragraphs,
          plus a Noul asking whether the sentence adds a specific fact the passages lack.

Usage:
  python3 jev_pipeline.py            dry run: counts, token and cost estimate, sample requests
  python3 jev_pipeline.py --live     call Jev (needs TYPESAFE_API_KEY); responses are cached
  python3 jev_pipeline.py --report   analyse cached results without calling the API
"""
import asyncio, hashlib, json, math, os, re, sys, collections
from pathlib import Path

S = Path(__file__).resolve().parent
sys.path.insert(0, str(S))
from paths import TEXT, CACHE as CACHE_PATH, DATA, REDACT_PATTERNS, lines as cfg_lines  # noqa: E402
import build  # noqa: E402  (page content: letters, concepts, holdings)

MODEL = "jev-1.13.0"          # pinned so thresholds stay comparable across runs
PRICE_PER_MTOK = 0.042
CONCURRENCY = 8
CACHE = CACHE_PATH
OUT = DATA / "jev_results.json"

# ---------------------------------------------------------------- paragraphs
STARTS = [61,214,576,889,1245,1610,2012,2572,3239,4158,4583,5318,5762,6336,6969,7442,7939,8267,8622,8931,9309,9656,9986,10320,10665]
IDS = [l["id"] for l in build.L]
TRIG = re.compile(r"^\s*(Our [Ff]ootnotes|Legal [Ff]ootnotes|This document is issued by|\*+ ?Sleep, Zakaria and Company|Counsel writes|Marathon Counsel|In this (letter|article),? we use the t ?erm|Some [Nn]otes on [Hh]ousekeeping|Performance numbers are produced|In our letters we refer)")
RESUME = re.compile(r"^\s*(Appendix|Speech given|Dear \.)")
SKIP = re.compile(r"^\s*(=====PAGE|\d{1,3}\s*$|Sleep, Zakaria and Company, Ltd\.\s*$|\d+[a-z]?, [A-Z][a-z]+ Street|London\s*$|England\s*$|[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}\s*$|[TF]: \+\d)")
_NAMES = cfg_lines(REDACT_PATTERNS)  # regexes for people named in the letters' housekeeping notes (kept out of git)
PRIVATE = re.compile(r"\+\d{2,3}[\d ()]{6,}\d|\S+@\S+" + (r"|\b(?:" + "|".join(_NAMES) + r")\b" if _NAMES else ""))  # contacts and staff names never leave this machine


PAGE_RE = re.compile(r"^=====PAGE (\d+)=====")


def page_at(lines, idx):
    """PDF page (1-based index in the 218-page collection) containing line idx."""
    for k in range(idx, -1, -1):
        m = PAGE_RE.match(lines[k])
        if m: return int(m.group(1))
    return 1


def paragraphs():
    lines = TEXT.read_text().split("\n")
    out = []
    for li, lid in enumerate(IDS):
        seg = lines[STARTS[li] - 1:STARTS[li + 1] - 1]
        blocks, pages, cur, skip = [], [], [], False
        page = page_at(lines, STARTS[li] - 1); cur_page = page
        for ln in seg:
            mp = PAGE_RE.match(ln)
            if mp: page = int(mp.group(1))
            if TRIG.search(ln): skip = True
            if skip and RESUME.search(ln): skip = False
            if skip or SKIP.search(ln): continue
            if not ln.strip():
                if cur: blocks.append(" ".join(cur)); pages.append(cur_page); cur = []
                continue
            if not cur: cur_page = page
            cur.append(ln.strip())
        if cur: blocks.append(" ".join(cur)); pages.append(cur_page)
        blocks = [re.sub(r"\s+", " ", PRIVATE.sub("[redacted]", b)).strip() for b in blocks]
        merged, mpages, carry, carry_page = [], [], "", None
        for b, pg in zip(blocks, pages):  # fold headings and short fragments into the paragraph that follows
            if carry: b = (carry + " " + b).strip(); pg = carry_page
            if len(b.split()) < 30: carry = b; carry_page = pg; continue
            merged.append(b); mpages.append(pg); carry = ""
        if carry:
            if merged: merged[-1] += " " + carry
            else: merged.append(carry); mpages.append(carry_page)
        for pi, text in enumerate(merged):
            out.append(dict(letter=li, id=lid, n=pi + 1, text=text, words=len(text.split()), page=mpages[pi]))
    return out


# ---------------------------------------------------------------- idea questions
IDEA_Q = {
 "c1": ("Does `paragraph` discuss buying shares at a large discount to the business's estimated real value, or the portfolio's ratio of price to estimated value (for example, paying 50 cents for a dollar of value)?",
        "It discusses purchase prices relative to estimated intrinsic value, the size of the discount, or the price-to-value ratio",
        "It does not; it may mention share prices or returns without comparing price to estimated value"),
 "c2": ("Does `paragraph` discuss a company passing the savings from its growing size or efficiency back to customers as lower prices, so that customers buy more and the company grows further?",
        "It describes, names or applies this mechanism (called scale economics or scale efficiencies shared in the letters)",
        "It does not; low prices or growth may be mentioned without linking scale savings to lower prices"),
 "c3": ("Does `paragraph` explicitly reason about where a particular business is likely to end up many years from now (for example how large or dominant it could become), or explicitly argue that the final destination of investment returns matters more than their order or smoothness along the way?",
        "It analyses a specific business's long-term destination, or argues that the end result matters more than the path of returns",
        'It does not; general statements about being long-term or patient do not count'),
 "c4": ("Does `paragraph` discuss investment time horizons, such as the value of patience, long holding periods, or how briefly other investors hold their shares?",
        "Time horizon or patience is a subject of the paragraph",
        "Time horizon and patience are not discussed"),
 "c5": ("Does `paragraph` discuss portfolio concentration versus diversification, meaning how many holdings to own or how large each position should be?",
        "It discusses the number of holdings, position sizes, concentration, or diversification",
        "It does not discuss portfolio construction in these terms"),
 "c6": ("Does `paragraph` discuss how the fund managers are paid (management fees, performance fees or hurdle rates) or conflicts of interest between fund managers and their clients?",
        "Fees, pay or manager–client conflicts of interest are discussed",
        "Neither fees nor manager–client conflicts are discussed"),
 "c7": ("Does `paragraph` name or explain a specific psychological bias or error of judgement, such as social proof, anchoring, availability, denial, commitment bias, or poor probabilistic reasoning, and how it affects decisions?",
        'A specific bias or judgement error is named, or its mechanism is explained',
        "It does not; criticising other investors' behaviour or motives in general terms does not count"),
 "c8": ("Does `paragraph` discuss investment mistakes, including the authors' own errors, errors of omission such as selling a great company too early, or how to learn from mistakes?",
        "Mistakes or learning from them are a subject of the paragraph",
        "Mistakes are not discussed"),
 "c9": ("Does `paragraph` discuss buying companies for less than it would cost to replace or rebuild their assets (replacement cost), or companies priced below the value of their physical assets?",
        "Replacement cost or pricing below asset value is discussed",
        "It does not discuss replacement cost or asset value"),
 "c10": ("Does `paragraph` discuss the character, integrity or capital-allocation behaviour of the people running companies, or companies run by their founders or owner-managers?",
        "It assesses company managers' character, behaviour or capital allocation, or founder or owner management",
        "It does not assess the people running companies"),
 "c11": ("Does `paragraph` discuss the size of the Nomad fund itself: accepting or turning away new money, opening or closing to subscriptions, or returning capital to investors?",
        "It discusses Nomad's own size, subscriptions, opening, closing, or returning capital",
        "It does not discuss Nomad's size or subscriptions"),
 "c12": ("Does `paragraph` discuss rules, investment mandates or regulation constraining how people or investment managers think and act, or argue that removing rules can lead to better judgement?",
        "Rules, mandates or regulation and their effect on judgement are discussed",
        "It does not discuss rules, mandates or regulation"),
 "c13": ("Does `paragraph` discuss shareholders acting to protect their interests, such as voting against a takeover, blocking a low-priced buyout, or owning a stake large enough to influence a company?",
        "Shareholder action, takeover resistance, or holding an influential stake is discussed",
        "It does not discuss shareholder action of this kind"),
 "c14": ("Does `paragraph` argue for the value of doing less, such as keeping spare capacity or cash in reserve (slack), taking unhurried time to think, or deliberately trading rarely?",
        'It makes an argument for slack, thinking time, or deliberate inactivity',
        'It does not; describing reporting frequency or low turnover as a fact, or criticising short-term investors, does not count'),
 "c15": ("Does `paragraph` discuss the distinction between growth investing and value investing, or argue that valuation ratios such as price-to-earnings or price-to-book are poor measures of what a business is worth?",
        "It discusses the growth-versus-value distinction or criticises valuation ratios as measures of value",
        "It does not discuss either"),
 "c16": ("Does `paragraph` draw on ideas from fields outside finance and psychology, such as biology, physics, complexity science (for example the Santa Fe Institute), anthropology or geography, to explain investing or business?",
        "It borrows an idea from another field to explain investing or business",
        "It does not borrow from another field"),
}


def idea_questions():
    return {cid: {"type": "noul", "instructions": q, "criteria": {"true": t, "false": f}} for cid, (q, t, f) in IDEA_Q.items()}


def idea_state(p):
    return {"source": f"A paragraph from the Nomad Investment Partnership letter for the period ending {p['id']}", "paragraph": p["text"]}


# ---------------------------------------------------------------- claims
def sentences(text):
    text = re.sub(r"<[^>]+>", "", text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z‘“(0-9$£])", text.strip())
    return [s for s in parts if len(s.split()) >= 6]


def claims():
    out = []
    for li, l in enumerate(build.L):
        for k, s in enumerate(sentences(l["summary"])):
            out.append(dict(kind="summary", letter=li, id=f"{l['id']}#s{k+1}", text=s))
        for k, s in enumerate(sentences(l["story"])):
            out.append(dict(kind="story", letter=li, id=f"{l['id']}#story{k+1}", text=s))
    for r in build.Hrows:
        cnt = build.ENTS_ALL[r["key"]] if hasattr(build, "ENTS_ALL") else build.ents[r["key"]]
        letters = [i for i, n in enumerate(cnt) if n]
        for k, s in enumerate(sentences(r["note"])):
            out.append(dict(kind="holding", letters=letters, id=f"{r['key']}#n{k+1}", text=s, name=r["name"]))
    return out


TOK = re.compile(r"[a-z0-9£$%]+")
STOP = set("the a an and or of to in on for with at by from as is was were be been it its this that these those his her their they he she we our not but also into than then over about which who what when".split())


def toks(t):
    return [w for w in TOK.findall(t.lower().replace("’", "'")) if w not in STOP]


class BM25:
    def __init__(self, docs, k1=1.4, b=0.75):
        self.docs = [toks(d) for d in docs]; self.k1, self.b = k1, b
        self.avg = sum(map(len, self.docs)) / max(1, len(self.docs))
        df = collections.Counter(w for d in self.docs for w in set(d)); N = len(self.docs)
        self.idf = {w: math.log(1 + (N - n + .5) / (n + .5)) for w, n in df.items()}
        self.tf = [collections.Counter(d) for d in self.docs]

    def top(self, query, k):
        q = toks(query); sc = []
        for i, (tf, d) in enumerate(zip(self.tf, self.docs)):
            s = sum(self.idf.get(w, 0) * tf[w] * (self.k1 + 1) / (tf[w] + self.k1 * (1 - self.b + self.b * len(d) / self.avg)) for w in q if w in tf)
            sc.append((s, i))
        return [i for s, i in sorted(sc, reverse=True)[:k] if s > 0]


CLAIM_Q = {
 "relation": {"type": "choice", "instructions": "How do `passages` relate to `claim`? The claim is a paraphrase written for a summary, so judge its meaning, not its wording.",
   "criteria": {"supports": "Together the passages state the claim or directly imply that it is true",
                "contradicts": "The passages state the opposite of the claim or imply that it is false",
                "says_nothing": "The passages do not address what the claim asserts, either way"}},
 "adds_fact": {"type": "noul", "instructions": "Does `claim` state a specific fact, such as a name, number, date, price or event, that does not appear in `passages`?",
   "criteria": {"true": "At least one specific fact in the claim is missing from the passages", "false": "Every specific fact in the claim appears in the passages, or the claim contains no specific facts"}},
}


def claim_requests(paras):
    by_letter = collections.defaultdict(list)
    for i, p in enumerate(paras): by_letter[p["letter"]].append(i)
    idx_all = BM25([p["text"] for p in paras])
    idx_letter = {li: (ids, BM25([paras[i]["text"] for i in ids])) for li, ids in by_letter.items()}
    reqs = []
    for c in claims():
        if c["kind"] == "holding":
            pool = [i for i in range(len(paras)) if paras[i]["letter"] in set(c["letters"])]
            sub = BM25([paras[i]["text"] for i in pool])
            hits = [pool[j] for j in sub.top(c["name"] + " " + c["text"], 4)]
        else:
            ids, idx = idx_letter[c["letter"]]
            hits = [ids[j] for j in idx.top(c["text"], 4)]
        state = {"claim": c["text"], "passages": [paras[i]["text"] for i in hits]}
        reqs.append(dict(claim=c, paras=hits, state=state))
    return reqs


# ---------------------------------------------------------------- API plumbing
def key_for(state, questions):
    return hashlib.sha256(json.dumps([MODEL, state, questions], sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def load_cache():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def est_tokens(state, questions):
    return int(len(json.dumps([state, questions], ensure_ascii=False)) / 3.6)


async def run_live(jobs):
    from typesafe_sdk import AsyncTypeSafeClient
    cache = load_cache(); todo = [j for j in jobs if key_for(j["state"], j["questions"]) not in cache]
    print(f"{len(jobs) - len(todo)} cached, {len(todo)} to request with {MODEL}")
    sem = asyncio.Semaphore(CONCURRENCY); done = 0; used = 0
    async with AsyncTypeSafeClient(model=MODEL, timeout=60.0) as client:
        async def one(j):
            nonlocal done, used
            async with sem:
                r = await client.system_one(state=j["state"], questions=j["questions"])
            ans = {}
            for qid, a in r.answers.items():
                d = a.model_dump() if hasattr(a, "model_dump") else dict(a)
                ans[qid] = d
            cache[key_for(j["state"], j["questions"])] = {"model": r.model, "answers": ans, "input_tokens": r.usage.input_tokens}
            used += r.usage.input_tokens or 0; done += 1
            if done % 50 == 0:
                CACHE.write_text(json.dumps(cache)); print(f"  {done}/{len(todo)}  ({used:,} input tokens)")
        await asyncio.gather(*(one(j) for j in todo))
    CACHE.write_text(json.dumps(cache))
    print(f"done: {used:,} input tokens this run, about ${used / 1e6 * PRICE_PER_MTOK:.3f}")


def jobs_for(paras, creqs):
    iq = idea_questions()
    jobs = [dict(kind="idea", ref=i, state=idea_state(p), questions=iq) for i, p in enumerate(paras)]
    jobs += [dict(kind="claim", ref=k, state=r["state"], questions=CLAIM_Q) for k, r in enumerate(creqs)]
    return jobs


# ---------------------------------------------------------------- analysis
def report(paras, creqs, jobs):
    cache = load_cache()
    got = {j["kind"] + str(j["ref"]): cache.get(key_for(j["state"], j["questions"])) for j in jobs}
    missing = sum(1 for v in got.values() if v is None)
    if missing: print(f"note: {missing} of {len(jobs)} requests are not cached yet")
    models = collections.Counter(v["model"] for v in got.values() if v)
    print("models:", dict(models))

    # ideas: per letter x concept aggregates
    grid = {}
    for cid in IDEA_Q:
        grid[cid] = []
        for li in range(24):
            ps = [(i, p) for i, p in enumerate(paras) if p["letter"] == li]
            vals = []
            for i, p in ps:
                v = got.get("idea" + str(i))
                if v: vals.append((v["answers"][cid]["noul"], p["words"], p["n"]))
            if not vals: grid[cid].append(None); continue
            wsum = sum(w for _, w, _ in vals)
            share = sum(pr * w for pr, w, _ in vals) / wsum
            expected = sum(pr for pr, _, _ in vals)
            strong = sorted([n for pr, _, n in vals if pr >= 0.7])
            k50 = sum(1 for pr, _, _ in vals if pr >= 0.5)
            grid[cid].append(dict(share=round(share, 3), expected=round(expected, 2), max=round(max(pr for pr, _, _ in vals), 3), paras=strong, k=k50, n=len(vals)))
    # compare with the hand-coded grid
    rows = []
    for c in build.C:
        for li, h in enumerate(c["hits"]):
            g = grid[c["id"]][li]
            if g: rows.append((int(h), g["share"], g["max"], len(g["paras"]), c["name"], build.L[li]["id"]))
    if rows:
        for lvl in (0, 1, 2):
            sh = [r[1] for r in rows if r[0] == lvl]
            if sh: print(f"hand-coded {lvl}: {len(sh)} cells, mean Jev share {sum(sh)/len(sh):.3f}")
        print("\npossible misses (hand-coded absent, Jev finds 2+ strong paragraphs):")
        for r in sorted([r for r in rows if r[0] == 0 and r[3] >= 2], key=lambda r: -r[1])[:25]:
            print(f"  {r[5]}  {r[4]:<38} share {r[1]:.2f}  strong ¶ {r[3]}")
        print("\npossible overstatements (hand-coded main theme, no paragraph above 0.5):")
        for r in [r for r in rows if r[0] == 2 and r[2] < 0.5]:
            print(f"  {r[5]}  {r[4]:<38} max {r[2]:.2f}")

    # claims
    verdicts = []
    for k, r in enumerate(creqs):
        v = got.get("claim" + str(k))
        if not v: continue
        rel = v["answers"]["relation"]; add = v["answers"]["adds_fact"]["noul"]
        verdicts.append(dict(id=r["claim"]["id"], kind=r["claim"]["kind"], text=r["claim"]["text"], relation=rel["choice"],
                             confidence=round(rel["confidence"], 3), probs=rel["probabilities"], adds_fact=round(add, 3),
                             paras=[f"{paras[i]['id']} ¶{paras[i]['n']}" for i in r["paras"]]))
    if verdicts:
        c = collections.Counter(v["relation"] for v in verdicts)
        print(f"\nclaims checked: {len(verdicts)}  {dict(c)}")
        flag = [v for v in verdicts if v["relation"] != "supports" or v["confidence"] < 0.8 or v["adds_fact"] >= 0.5]
        print(f"flagged for review: {len(flag)}")
        for v in sorted(flag, key=lambda v: (v["relation"] == "supports", v["confidence"])):
            print(f"  [{v['relation']} {v['confidence']:.2f} | adds_fact {v['adds_fact']:.2f}] {v['id']}: {v['text'][:150]}")
    OUT.write_text(json.dumps(dict(model=dict(models), grid=grid, claims=verdicts), ensure_ascii=False, indent=1))
    print(f"\nwrote {OUT.name}")


def main():
    paras = paragraphs(); creqs = claim_requests(paras); jobs = jobs_for(paras, creqs)
    if "--live" in sys.argv:
        if not os.environ.get("TYPESAFE_API_KEY"):
            sys.exit("TYPESAFE_API_KEY is not set")
        asyncio.run(run_live(jobs)); report(paras, creqs, jobs); return
    if "--report" in sys.argv:
        report(paras, creqs, jobs); return
    # dry run
    per_letter = collections.Counter(p["id"] for p in paras)
    wl = sorted(p["words"] for p in paras)
    print(f"paragraphs: {len(paras)}  (median {wl[len(wl)//2]} words, max {wl[-1]})")
    print("per letter:", " ".join(f"{k}:{v}" for k, v in per_letter.items()))
    ck = collections.Counter(r["claim"]["kind"] for r in creqs)
    print(f"claims: {len(creqs)}  {dict(ck)}")
    it = sum(est_tokens(j["state"], j["questions"]) for j in jobs if j["kind"] == "idea")
    ct = sum(est_tokens(j["state"], j["questions"]) for j in jobs if j["kind"] == "claim")
    print(f"requests: {len(jobs)}  est. input tokens: ideas {it:,}, claims {ct:,}  -> about ${(it+ct)/1e6*PRICE_PER_MTOK:.3f}")
    biggest = max(jobs, key=lambda j: est_tokens(j["state"], j["questions"]))
    print(f"largest request ~{est_tokens(biggest['state'], biggest['questions']):,} tokens (limit 32k state + longest question)")
    print("\nsample idea request state:", json.dumps(jobs[40]["state"], ensure_ascii=False)[:400], "...")
    r = creqs[3]
    print("\nsample claim:", r["claim"]["id"], "|", r["claim"]["text"])
    for i in r["paras"]: print("   candidate", paras[i]["id"], f"¶{paras[i]['n']}:", paras[i]["text"][:110], "...")
    print(f"\ncache: {len(load_cache())} responses stored")


if __name__ == "__main__":
    main()
