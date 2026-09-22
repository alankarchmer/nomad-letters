"""Where everything lives.

data/     derived data that is safe to publish (counts, Jev judgments, paraphrased notes)
private/  the letters' text, the Jev response cache and writer inputs: copyrighted text, never committed
site/     the built page
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
DATA = ROOT / "data"
PRIVATE = ROOT / "private"
SITE = ROOT / "site"

TEXT = PRIVATE / "nomad.txt"            # output of extract_text.py
CACHE = PRIVATE / "jev_cache.json"      # every Jev request/response, keyed by a hash of the request
REDACT_PATTERNS = PRIVATE / "redact_patterns.txt"   # regexes (one per line) for names removed before text is sent to Jev
REDACT_WORDS = PRIVATE / "redact_words.txt"         # lowercase words kept out of the public word index


def lines(path):
    """Non-empty, non-comment lines of an optional file."""
    if not path.exists():
        return []
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.lstrip().startswith("#")]
