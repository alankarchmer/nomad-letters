"""Five more Jev jobs over the Nomad letters, all run at build time.

  paths      Score: how central is each paragraph to each idea it discusses -> reading paths into the PDF
  scorecard  Choice/Score per company mention: role, price vs value, scale sharing, owner-run,
             capital allocation, management character, the authors' view
  influence  Choice per mention of a thinker: how the letter uses them, and which idea they support
  voice      Score per paragraph: humour, candour about own mistakes, criticism of the industry; Noul: tells a story
  ask        Score per (question, passage): does this passage answer a reader's question?

Usage:
  python3 jev_extras.py            dry run (counts and cost)
  python3 jev_extras.py --live     call Jev (needs TYPESAFE_API_KEY); cached in jev_cache.json
  python3 jev_extras.py --report   aggregate cached answers into extras_results.json and writer inputs
"""
import asyncio, collections, json, os, re, sys
from pathlib import Path

S = Path(__file__).resolve().parent
sys.path.insert(0, str(S))
import build                      # noqa: E402
import jev_pipeline as jp         # noqa: E402

PARAS = jp.paragraphs()
IQ = jp.idea_questions()
CACHE = jp.load_cache()


def ans(state, questions):
    v = CACHE.get(jp.key_for(state, questions))
    return v["answers"] if v else None


def idea_p(i, cid):
    a = ans(jp.idea_state(PARAS[i]), IQ)
    return a[cid]["noul"] if a else 0.0


def first_sentence(t):
    return re.split(r"(?<=[.!?])\s", re.sub(r"<[^>]+>", "", t), maxsplit=1)[0]


IDEA_DESC = {c["id"]: dict(name=c["name"], description=first_sentence(c["def"])) for c in build.C}

# ------------------------------------------------------------------ 1. reading paths
PATH_LEVELS = [
    "The idea is only mentioned in passing or implied",
    "The paragraph applies the idea to a specific company, event or decision",
    "The paragraph explains the reasoning behind the idea or argues for it",
    "The paragraph introduces, names or sets out the idea in general terms as its main subject",
]


def path_jobs():
    jobs = []
    for i, p in enumerate(PARAS):
        cands = [cid for cid in IDEA_DESC if idea_p(i, cid) >= 0.5]
        if not cands: continue
        state = {"paragraph": p["text"], "ideas": {cid: IDEA_DESC[cid] for cid in cands}}
        qs = {cid: {"type": "score", "instructions": f"How central is the idea `ideas.{cid}` to `paragraph`?", "criteria": PATH_LEVELS} for cid in cands}
        jobs.append(dict(kind="paths", ref=i, state=state, questions=qs))
    return jobs


# ------------------------------------------------------------------ 2. scorecard
CO_PAT = {
 "speedway": r"International Speedway|\bISCA\b|Nascar", "matichon": r"Matichon", "xerox": r"Xerox", "monsanto": r"Monsanto",
 "estee": r"Est[ée]e ?Lauder", "conseco": r"Conseco", "stagecoach": r"Stagecoach", "costco": r"Costco|Price Club|Fed-Mart",
 "kersaf": r"Kersaf", "weetabix": r"Weetabix", "lucent": r"Lucent", "erie": r"\bErie\b", "jardine": r"Jardine",
 "unioncement": r"Union Cement|Holcim Philippines", "telewest": r"Telewest|Virgin Media", "newworld": r"New World Development",
 "dell": r"\bDell\b", "ebay": r"eBay", "walmart": r"Wal-?Mart|Sam Walton", "berkshire": r"Berkshire|GEICO|Geico|Nebraska Furniture|National Indemnity",
 "zimbabwe": r"Zimbabwe|Zimcem|Harare", "siam": r"Siam (City )?Cement", "northwest": r"Northwest Airlines", "amazon": r"Amazon|Ama zon",
 "liberty": r"Liberty (Media|Global)", "games": r"Games Workshop|Warhammer", "whiteheadmann": r"Whitehead Mann", "mdc": r"\bMDC\b",
 "airasia": r"Air ?Asia", "mbia": r"\bMBIA\b", "carpetright": r"Carpetright", "gm": r"General Motors|\bGM\b",
 "michaelpage": r"Michael Page", "asos": r"\bAsos\b|\bASOS\b", "welsh": r"Welsh insurance|Welsh motor", "blackarrow": r"Black Arrow",
}
CO_NAME = {r["key"]: r["name"] for r in build.Hrows}
NA = "`paragraph` does not say anything about this for `company`"
CO_Q = {
 "role": {"type": "choice", "instructions": "What role does `company` play in `paragraph`?", "criteria": {
     "holding_positive": "A Nomad investment, described favourably or as doing well",
     "holding_troubled": "A Nomad investment, described as troubled, disappointing or cheap because of its problems",
     "sold": "Describes Nomad selling, or having sold, its shares",
     "mistake": "Described as one of Nomad's own mistakes",
     "example": "Used as an example, comparison or case study, not discussed as a Nomad investment",
     "passing": "Mentioned only in passing"}},
 "price": {"type": "choice", "instructions": "What does `paragraph` say about how the share price of `company` compares with the value of the business?", "criteria": {
     "not_addressed": NA,
     "expensive": "Priced at or above what the business is worth",
     "fair": "Priced roughly at fair value",
     "discount": "Priced somewhat below what the business is worth",
     "deep_discount": "Priced far below value, such as half its worth or less, or well below replacement cost"}},
 "sharing": {"type": "choice", "instructions": "What does `paragraph` say about whether `company` passes the savings from its scale or efficiency on to customers as lower prices?", "criteria": {
     "not_addressed": NA,
     "keeps": "It keeps the savings, raises prices, or charges customers as much as it can",
     "shares": "It passes savings from its scale or efficiency on to customers as lower prices"}},
 "owner": {"type": "choice", "instructions": "What does `paragraph` say about who runs `company`?", "criteria": {
     "not_addressed": NA,
     "hired": "Run by hired professional managers",
     "owner": "Run by its founder, a founding family, or a manager who owns a large stake"}},
 "capital": {"type": "choice", "instructions": "How does `paragraph` judge the way `company` allocates capital (for example acquisitions, reinvestment, share buybacks, debt, share issuance)?", "criteria": {
     "not_addressed": NA,
     "poor": "Poorly: for example overpaying for acquisitions, diluting shareholders, or piling on debt",
     "mixed": "Mixed, or improving after past mistakes",
     "good": "Well: for example reinvesting at high returns, buying back shares cheaply, or declining to grow for its own sake"}},
 "character": {"type": "choice", "instructions": "How does `paragraph` describe the character of the people running `company`?", "criteria": {
     "not_addressed": NA,
     "poor": "Self-serving, promotional, short-term or evasive",
     "good": "Candid, rational, long-term minded or focused on customers"}},
 "view": {"type": "score", "instructions": "How positive is the authors' view of `company` as a business in `paragraph`?", "criteria": [
     "Negative: criticised, called a mistake, or a business to avoid",
     "Neutral or mixed",
     "Positive",
     "Enthusiastic: held up as an exemplary business"]},
}


def mention_pairs(patterns):
    out = []
    for i, p in enumerate(PARAS):
        for key, pat in patterns.items():
            if re.search(pat, p["text"]): out.append((i, key))
    return out


def scorecard_jobs():
    return [dict(kind="co", ref=(i, key), state={"company": CO_NAME[key], "paragraph": PARAS[i]["text"]}, questions=CO_Q)
            for i, key in mention_pairs(CO_PAT)]


# ------------------------------------------------------------------ 3. influence map
PEOPLE = {
 "buffett": ("Warren Buffett", r"Buffett"), "munger": ("Charlie Munger", r"Munger"), "keynes": ("John Maynard Keynes", r"Keynes"),
 "darwin": ("Charles Darwin", r"Darwin"), "zeckhauser": ("Richard Zeckhauser", r"Zeckhauser"), "miller": ("Bill Miller", r"Bill Miller"),
 "taleb": ("Nassim Taleb", r"Taleb"), "bogle": ("Jack Bogle", r"Bogle"), "bezos": ("Jeff Bezos", r"Bezos"), "sinegal": ("Jim Sinegal", r"Sinegal"),
 "santafe": ("Santa Fe Institute", r"Santa ?Fe|\bSFI\b|Gell-Mann|Brian Arthur|Geoff(?:rey)? West|Ole Peters"),
 "rand": ("Ayn Rand", r"Ayn Rand|John Galt"), "mauboussin": ("Michael Mauboussin", r"Mauboussin"), "ariely": ("Dan Ariely", r"Ariely"),
 "cialdini": ("Robert Cialdini", r"Cialdini"), "graham": ("Benjamin Graham", r"Benjamin Graham|Graham wrote|Security Analysis"),
 "schloss": ("Walter Schloss", r"Schloss"), "walton": ("Sam Walton", r"Sam Walton"), "schwed": ("Fred Schwed", r"Schwed"),
 "ruane": ("Bill Ruane", r"Ruane"), "attenborough": ("David Attenborough", r"Attenborough"), "schwartz": ("Barry Schwartz", r"Barry Schwartz|Schwartz observed"),
 "hirt": ("H.O. Hirt (Erie founder)", r"H\.\s?O\.\s?Hirt|Hirt posted"), "lynch": ("Peter Lynch", r"Peter Lynch"),
}
USE_Q = {"type": "choice", "instructions": "How does `paragraph` use `person`?", "criteria": {
    "endorses": "Adopts or endorses their idea, advice or example",
    "evidence": "Quotes or cites them as evidence or authority for a point",
    "anecdote": "Tells a story about them to illustrate a point",
    "disagrees": "Disagrees with or criticises them",
    "passing": "Mentions them only in passing"}}


def influence_questions():
    crit = {cid: f"{d['name']}: {d['description']}" for cid, d in IDEA_DESC.items()}
    crit["none"] = "None of these ideas; the reference serves some other purpose"
    return {"use": USE_Q, "idea": {"type": "choice", "instructions": "Which of these ideas does `paragraph` use `person` to support or illustrate?", "criteria": crit}}


def influence_jobs():
    pats = {k: v[1] for k, v in PEOPLE.items()}
    q = influence_questions()
    return [dict(kind="inf", ref=(i, key), state={"person": PEOPLE[key][0], "paragraph": PARAS[i]["text"]}, questions=q)
            for i, key in mention_pairs(pats)]


# ------------------------------------------------------------------ 4. voice
VOICE_Q = {
 "humour": {"type": "score", "instructions": "How humorous is `paragraph`?", "criteria": [
     "No humour: plainly informative or argumentative",
     "A wry aside, pun or playful turn of phrase",
     "A joke, a comic story, or a sustained comic passage"]},
 "candour": {"type": "score", "instructions": "How much does `paragraph` admit mistakes or limitations of the authors themselves (the managers of Nomad)?", "criteria": [
     "No admission of the authors' own mistakes or limitations",
     "Acknowledges a limitation, uncertainty or small error of their own",
     "Admits a specific mistake of their own, or dwells on its cost"]},
 "critique": {"type": "score", "instructions": "How critical is `paragraph` of the investment or fund-management industry, its practices, or financial regulation?", "criteria": [
     "Not critical of the industry or regulation",
     "Mild or passing criticism",
     "Sharp or sustained criticism"]},
 "story": {"type": "noul", "instructions": "Does `paragraph` tell an anecdote: a specific event involving particular people or places?",
     "criteria": {"true": "It narrates a specific event or encounter", "false": "It argues, explains or reports figures without narrating a specific event"}},
}


def voice_jobs():
    return [dict(kind="voice", ref=i, state={"paragraph": p["text"]}, questions=VOICE_Q) for i, p in enumerate(PARAS)]


# ------------------------------------------------------------------ 5. ask the letters
ASK = [
 ("closing", "Why did Sleep and Zakaria close Nomad and return the money?"),
 ("ses", "What does 'scale economics shared' mean?"),
 ("costco", "Why did Nomad invest in Costco?"),
 ("amazon", "Why did Nomad own so much Amazon?"),
 ("robust", "What is the robustness ratio?"),
 ("destination", "What is destination analysis?"),
 ("biggest_mistake", "What did they consider their biggest mistake?"),
 ("stagecoach", "Why did they sell Stagecoach, and why did they regret it?"),
 ("conseco", "What went wrong with the investment in Conseco?"),
 ("fees", "How did Nomad's performance fee work?"),
 ("mgmt_fee", "Why should a management fee only cover costs and not make a profit?"),
 ("close2004", "Why did Nomad close to new money in 2004?"),
 ("reopen", "When and why did Nomad reopen to new investors?"),
 ("concentration", "How many stocks should a fund own, and why not diversify more?"),
 ("yield_curve", "What is the equity yield curve?"),
 ("zimbabwe", "Why did Nomad invest in Zimbabwe, and how did it end?"),
 ("weetabix", "What happened with the Weetabix investment?"),
 ("mbia", "Why did they sell MBIA so quickly?"),
 ("dilution", "What is dilution risk?"),
 ("crash2008", "How did they respond to the market crash of 2008?"),
 ("slack", "Why do they argue for slack?"),
 ("santafe", "What is the Santa Fe Institute, and which of its ideas do the letters describe?"),
 ("bridge", "How does Zeckhauser play bridge, and why does it matter for investing?"),
 ("biases", "Which psychological mistakes do investors make most often?"),
 ("marathon", "How did Nomad move from Marathon to Sleep, Zakaria and Company, and what changed?"),
 ("pv", "What is the price-to-value ratio and why did they watch it?"),
 ("returns_model", "What return did they expect from a typical investment?"),
 ("reporting", "Why did they dislike frequent reporting to clients?"),
 ("growth_value", "What did they think of the growth versus value debate?"),
 ("founders", "Why did they end up owning founder-run companies?"),
 ("thinkers", "What did Nomad mean by its office list of super high-quality thinkers, and why did it keep one?"),
 ("learning", "How should investors respond to their own mistakes?"),
 ("regulation", "What did they think about financial regulation?"),
 ("airasia", "What did they like about AirAsia?"),
 ("partners", "Why did they value the patience of their partners so much?"),
 ("x_amount", "What should successful investors do with their wealth?"),
]
ASK_K = 20
ASK_LEVELS = ["Unrelated to the question", "Related background, but does not answer the question",
              "Partly answers the question", "Directly answers the question"]


def extra_docs():
    """Preamble and postamble (2021), not part of the letters, used only for Ask."""
    lines = __import__("paths").TEXT.read_text().split("\n")
    def grab(a, b, did, page):
        txt = re.sub(r"\s+", " ", " ".join(l for l in lines[a:b] if not l.startswith("=====PAGE") and not re.match(r"^\s*\d{1,3}\s*$", l))).strip()
        chunks = re.split(r"(?<=\.)\s(?=[A-Z])", txt)
        out, cur = [], ""
        for c in chunks:
            cur = (cur + " " + c).strip()
            if len(cur.split()) > 120: out.append(cur); cur = ""
        if cur: out.append(cur)
        return [dict(letter=None, id=did, n=k + 1, text=t, words=len(t.split()), page=page) for k, t in enumerate(out)]
    return grab(9, 44, "preamble", 2) + grab(10665, len(lines), "postamble", 218)


def ask_pool():
    return PARAS + extra_docs()


ASK_HINT = {"closing": ["postamble"], "x_amount": ["preamble", "postamble"], "marathon": ["2006-06", "2006-12"]}
QSTOP = set("why did what how does do when which who whom is are was were should much so many and it they them their there would could can".split())


def ask_query(q):
    seen, out = set(), []
    for w in jp.toks(q):
        if w in QSTOP or w in seen: continue
        seen.add(w); out.append(w)
    return " ".join(out)


def ask_candidates():
    """Keyword shortlist, plus the best paragraphs that name the question's subject or year."""
    pool = ask_pool()
    bm = jp.BM25([p["text"] for p in pool])
    out = {}
    for qid, q in ASK:
        qq = ask_query(q)
        ids = bm.top(qq, 14)
        ents = [w for w in re.findall(r"(?<!^)(?<![.?!] )\b([A-Z][A-Za-z\-]+)", q) if w.lower() not in QSTOP and w not in ("Nomad", "Sleep", "Zakaria")]
        years = re.findall(r"\b(19|20)(\d\d)\b", q)
        extra = []
        if ents:
            sub = [i for i, p in enumerate(pool) if any(e in p["text"] for e in ents)]
            if sub:
                sb = jp.BM25([pool[i]["text"] for i in sub]); extra += [sub[j] for j in sb.top(qq, 10)]
        for c, yy in years:
            sub = [i for i, p in enumerate(pool) if p["id"].startswith(c + yy)]
            if sub:
                sb = jp.BM25([pool[i]["text"] for i in sub]); extra += [sub[j] for j in sb.top(qq, 8)]
        for doc in ASK_HINT.get(qid, []):
            sub = [i for i, p in enumerate(pool) if p["id"] == doc]
            if sub:
                sb = jp.BM25([pool[i]["text"] for i in sub]); extra += [sub[j] for j in sb.top(qq, 6)] or sub[:6]
        merged = []
        for i in extra + ids:
            if i not in merged: merged.append(i)
        out[qid] = merged[:ASK_K + 4]
    return pool, out


def ask_jobs():
    pool, cands = ask_candidates()
    jobs = []
    for qid, q in ASK:
        ids = cands[qid]
        state = {"question": q, "passages": [pool[i]["text"] for i in ids]}
        qs = {f"p{k}": {"type": "score", "instructions": f"How well does `passages[{k}]` answer `question`?", "criteria": ASK_LEVELS} for k in range(len(ids))}
        qs["answered"] = {"type": "noul", "instructions": "Do `passages`, taken together, answer `question`?",
                          "criteria": {"true": "At least one passage gives a direct answer", "false": "None of the passages directly answers the question"}}
        jobs.append(dict(kind="ask", ref=qid, state=state, questions=qs))
    return jobs


def all_jobs():
    return dict(paths=path_jobs(), scorecard=scorecard_jobs(), influence=influence_jobs(), voice=voice_jobs(), ask=ask_jobs())


def main():
    groups = all_jobs()
    if "--live" in sys.argv:
        if not os.environ.get("TYPESAFE_API_KEY"): sys.exit("TYPESAFE_API_KEY is not set")
        jobs = [j for g in groups.values() for j in g]
        asyncio.run(jp.run_live(jobs)); return
    if "--report" in sys.argv:
        import extras_report; extras_report.main(groups); return
    tot = 0
    for name, g in groups.items():
        t = sum(jp.est_tokens(j["state"], j["questions"]) for j in g); tot += t
        big = max((jp.est_tokens(j["state"], j["questions"]) for j in g), default=0)
        cached = sum(1 for j in g if jp.key_for(j["state"], j["questions"]) in CACHE)
        print(f"{name:<10} {len(g):>5} requests  ~{t:>9,} tokens  largest ~{big:,}  cached {cached}")
    print(f"total ~{tot:,} tokens, about ${tot / 1e6 * jp.PRICE_PER_MTOK:.3f}")
    pc = collections.Counter(k for _, k in mention_pairs(CO_PAT)); print("company mentions:", dict(pc.most_common(8)), "...")
    pp = collections.Counter(k for _, k in mention_pairs({k: v[1] for k, v in PEOPLE.items()})); print("people mentions:", dict(pp))


if __name__ == "__main__":
    main()
