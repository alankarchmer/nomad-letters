# The Nomad Letters

An interactive, single-page guide to the letters Nick Sleep and Qais Zakaria wrote to partners in the Nomad Investment Partnership between 2001 and 2014. It includes:

- a growth-of-$1 route map with one marker per letter
- summaries of all 24 letters
- a grid of 16 recurring ideas against the letters
- a timeline of the companies the letters discuss
- a company scorecard you can re-weight yourself
- an influence map of the thinkers they cite
- a view of the letters' tone over time
- 36 reader questions answered from the source
- a word-frequency explorer

The page never reproduces the letters' text, apart from one sentence. Every summary, note and answer is a paraphrase, and every reference points to a page in the authors' approved PDF on the [IGY Foundation website](https://igyfoundation.org.uk/nomad-partnership-letters/).

Most of the judgments behind the page come from [TypeSafe](https://docs.typesafe.ai)'s **Jev** model. Jev answers typed questions about text (yes/no, multiple choice or ratings) with calibrated probabilities. All Jev work runs once, at build time, and the page ships only the results.

This is an unofficial project, not affiliated with the authors or the IGY Foundation, and nothing here is investment advice.

## Layout

```
site/index.html        the built page (self-contained HTML, no server needed)
main.py                tiny static server for site/ on $PORT (used by Railway)
railway.json           Railway start command: python main.py
src/
  paths.py             where everything lives
  extract_text.py      1. PDF -> private/nomad.txt
  word_index.py        2. word counts per letter  -> data/wordindex.txt, data/totals.json
  entities.py          2. company/person mention counts -> data/ents.json
  distinctive_words.py    helper: tf-idf candidates for "words that set this letter apart"
  jev_pipeline.py      3. Jev: 16 idea questions per paragraph + fact-check of the summaries -> data/jev_results.json
  jev_extras.py        4. Jev: reading paths, company scorecard, influences, voice, Ask the letters
  extras_report.py        aggregates jev_extras answers -> data/extras_results.json (+ writer inputs in private/)
  verify_writers.py    5. checks drafted notes/answers: copy check + Jev grounding check
  build.py             6. page content (letter summaries, ideas, holdings) + data -> site/index.html
  template.html           the page's HTML, CSS and JavaScript
data/                  derived data that is safe to publish (counts, Jev judgments, paraphrased notes and answers)
private/               not committed: the letters' text, the Jev cache, writer inputs, redaction lists
```

## Rebuild the page from the committed data

No PDF or API key is needed for this:

```bash
python3 src/build.py      # writes site/index.html (a complete UTF-8 HTML document)
```

`--fragment out.html` also writes the page without its `<html>`/`<head>` wrapper, for hosts that add their own (such as claude.ai Artifacts).

## Deploy

`site/index.html` is a single self-contained file, so any static host works (GitHub Pages, Netlify and so on). For Railway, `railway.json` sets the start command to `python main.py`, which serves `site/` on the port Railway provides. It uses only the standard library, so the packages in `requirements.txt` aren't needed at run time. To run it locally:

```bash
python3 main.py      # http://localhost:8000
```

## Rebuild everything from scratch

1. Install the requirements (Python 3.12): `pip install -r requirements.txt`
2. Download the approved PDF from the IGY Foundation and extract its text:
   `python3 src/extract_text.py path/to/the.pdf`
   The letter boundaries (`STARTS` in `jev_pipeline.py` and `word_index.py`) are line numbers in this extracted text. They were produced with pypdf 6.19 from the 218-page "Full Collection" PDF, so check them if your extraction differs.
3. Optionally, create `private/redact_patterns.txt` and `private/redact_words.txt`. These hold the names of people mentioned in the letters' housekeeping notes, so they're removed before any text is sent to Jev and kept out of the word index. See `private/README.md`.
4. Count words and mentions:
   `python3 src/word_index.py && python3 src/entities.py`
5. Run Jev. You need a TypeSafe API key, and the whole run cost about $0.20 in September 2026:
   ```bash
   export TYPESAFE_API_KEY=...          # never commit this
   python3 src/jev_pipeline.py          # dry run: request count and cost estimate
   python3 src/jev_pipeline.py --live
   python3 src/jev_extras.py --live
   python3 src/jev_extras.py --report
   ```
   Every response is cached in `private/jev_cache.json`, keyed by a hash of the request, so re-runs only pay for new or changed requests. The model is pinned to `jev-1.13.0`.
6. The short notes and answers (`data/writer_*_out.json`) were drafted from the passages Jev ranked highest, using the inputs `extras_report.py` writes to `private/`. Check any changes with `python3 src/verify_writers.py --live`.
7. `python3 src/build.py`

## How Jev is used

| Feature | Jev question type | What code does with the answers |
| --- | --- | --- |
| Fact-check of the summaries | Choice: do the passages support, contradict or say nothing about this sentence? | Flags weak sentences for review by hand; ten were rewritten |
| Ideas grid | 16 yes/no questions per paragraph (726 paragraphs) | Share of each letter's text that discusses each idea |
| Reading paths | Rating: how central is this paragraph to the idea? | Top pages per idea, linked into the PDF |
| Scorecard | Six multiple-choice questions per company mention, each with a "doesn't say" option | Traits per company; the browser re-ranks with your weights |
| Influences | Choice: how is this thinker used, and which idea does the reference support? | Weighted person-to-idea network |
| Voice | Ratings per paragraph: humour, candour, industry criticism | Per-letter tone series and the strongest pages |
| Ask the letters | Rating per passage: does it answer the question? Plus a yes/no on whether any passage does | Ranked sources; answers drafted from them and checked with Jev |

## Notes

- Page numbers are positions in the 218-page approved PDF. The number printed at the foot of each page is one higher.
- Performance figures are as reported in the letters: before performance fees, against the MSCI World index (net, US$).
- The letters are the work of Nick Sleep and Qais Zakaria. Please read and cite the approved version at the IGY Foundation.
