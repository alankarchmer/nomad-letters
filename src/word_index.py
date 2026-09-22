"""Step 2a: per-letter word counts for the "Trace a word" chart.

    python3 src/word_index.py

Reads private/nomad.txt and writes data/wordindex.txt (word -> counts per letter, for words used
3+ times) and data/totals.json (words per letter). Disclaimers and housekeeping notes are skipped;
stopwords and the words in private/redact_words.txt are left out. The index holds counts only,
not text.
"""
import collections, json, re
from paths import DATA, TEXT, REDACT_WORDS, lines as cfg_lines

lines = TEXT.read_text().split("\n")
starts = [61,214,576,889,1245,1610,2012,2572,3239,4158,4583,5318,5762,6336,6969,7442,7939,8267,8622,8931,9309,9656,9986,10320,10665]
ids = ["2001-12","2002-06","2002-12","2003-06","2003-12","2004-06","2004-12","2005-06","2005-12","2006-06","2006-12","2007-06","2007-12","2008-06","2008-12","2009-06","2009-12","2010-06","2011-06","2011-12","2012-06","2012-12","2013-06","2013-12"]
trig = re.compile(r"^\s*(Our [Ff]ootnotes|Legal [Ff]ootnotes|This document is issued by|\*+ ?Sleep, Zakaria and Company|Counsel writes|Marathon Counsel|In this (letter|article),? we use the t ?erm|Some [Nn]otes on [Hh]ousekeeping|Performance numbers are produced|In our letters we refer)")
resume = re.compile(r"^\s*(Appendix|Speech given|Dear \.)")
skipline = re.compile(r"^\s*(=====PAGE|\d{1,3}\s*$|Sleep, Zakaria and Company, Ltd\.\s*$|\d+[a-z]?, [A-Z][a-z]+ Street|London\s*$|England\s*$|[A-Z]{1,2}\d[A-Z\d]? \d[A-Z]{2}\s*$|[TF]: \+\d)")

texts = []
for i, lid in enumerate(ids):
    seg = lines[starts[i] - 1:starts[i + 1] - 1]
    out = []; skip = False
    for ln in seg:
        if trig.search(ln): skip = True
        if skip and resume.search(ln): skip = False
        if skip or skipline.search(ln): continue
        out.append(ln)
    texts.append(" ".join(out))

priv = set(cfg_lines(REDACT_WORDS))
stop = set("""the and that this with from have for are was were been has had not but his her its our their they them then than there these those which who whom what when where why how all any can could would should will may might must shall into onto upon over under about above after before again also just only very such some more most much many few other each own same both either neither nor too out off one two three four five six seven eight nine ten per its it's i'm we're you're don't didn't isn't aren't wasn't won't doesn't can't that's there's let's what's who's he's she's being does did doing done yes yet via etc let get got use used using say said says see seen well even ever every still here now way ways make made makes you your yours him she he it we us me my mine ours theirs itself themselves ourselves yourself myself hers himself because while though although whilst unless until since therefore thus hence however whether also""".split())
tok = re.compile(r"[a-z][a-z'\-]*[a-z]|[a-z]")
counts, totals = [], []
for t in texts:
    t2 = t.lower().replace("’", "'").replace("- ", "")
    ws = [w.strip("'-") for w in tok.findall(t2)]
    ws = [re.sub(r"'s$", "", w) for w in ws if w]
    totals.append(len(ws))
    counts.append(collections.Counter(w for w in ws if len(w) >= 3 and w not in stop and w not in priv))
agg = collections.Counter()
for c in counts: agg.update(c)
vocab = [w for w, n in agg.items() if n >= 3]
vocab.sort(key=lambda w: -agg[w])
blob = "|".join(w + ":" + ",".join(f"{i}.{n}" for i, n in enumerate(counts[i][w] for i in range(len(ids))) if n) for w in vocab)
DATA.mkdir(exist_ok=True)
(DATA / "wordindex.txt").write_text(blob)
json.dump({"ids": ids, "totals": totals}, open(DATA / "totals.json", "w"))
print("vocab", len(vocab), "words", sum(totals))
