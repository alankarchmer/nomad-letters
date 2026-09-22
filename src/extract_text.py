"""Step 1: extract the text of the letters from the PDF.

    python3 src/extract_text.py path/to/Nomad_Partnership_Letters.pdf

Writes private/nomad.txt with a "=====PAGE n=====" marker before each PDF page. The other
scripts rely on the line numbers of this file (see STARTS in jev_pipeline.py), which were
taken from the 218-page "Full Collection" PDF.
"""
import sys
import pypdf
from paths import PRIVATE, TEXT

if len(sys.argv) != 2:
    sys.exit(__doc__)
reader = pypdf.PdfReader(sys.argv[1])
parts = [f"\n=====PAGE {i + 1}=====\n" + (page.extract_text() or "") for i, page in enumerate(reader.pages)]
PRIVATE.mkdir(exist_ok=True)
TEXT.write_text("".join(parts))
print(f"{len(reader.pages)} pages -> {TEXT}")
