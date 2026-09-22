# private/

Everything else in this folder is excluded from git (see `.gitignore`). It holds:

- `nomad.txt`: text extracted from the PDF by `src/extract_text.py`. This is the letters' copyrighted text.
- `jev_cache.json`: every Jev request and response. Requests contain paragraph text.
- `writer_paths.json`, `writer_ask.json`: passages handed to the note and answer drafters.
- `redact_patterns.txt`: one regex per line. Matching names are replaced with `[redacted]` before any text is sent to Jev. The order matters, so list longer patterns first. Lines starting with `#` are ignored.
- `redact_words.txt`: one lowercase word per line, kept out of the public word index.

Phone numbers and email addresses are always redacted, whether or not these files exist.
