"""Step 2b: how often each company and person is mentioned in each letter (regex counts).

    python3 src/entities.py

Reads private/nomad.txt, writes data/ents.json ({key: [count per letter]}). Used for the
holdings trail on the page.
"""
import json, re
from paths import DATA, TEXT

lines = TEXT.read_text().split("\n")
starts = [61,214,576,889,1245,1610,2012,2572,3239,4158,4583,5318,5762,6336,6969,7442,7939,8267,8622,8931,9309,9656,9986,10320,10665]
texts = [re.sub(r"\s+", " ", " ".join(lines[starts[i] - 1:starts[i + 1] - 1])) for i in range(24)]
ENTS = {
 "costco": r"Costco|Price Club|Fed-Mart", "amazon": r"Amazon", "berkshire": r"Berkshire|Geico|GEICO|Nebraska Furniture|National Indemnity",
 "stagecoach": r"Stagecoach", "weetabix": r"Weetabix", "xerox": r"Xerox", "conseco": r"Conseco", "lucent": r"Lucent", "matichon": r"Matichon",
 "speedway": r"International Speedway|ISCA|Nascar", "monsanto": r"Monsanto", "airasia": r"Air ?Asia", "games": r"Games Workshop|Warhammer",
 "mbia": r"MBIA", "carpetright": r"Carpetright", "asos": r"Asos|ASOS", "michaelpage": r"Michael Page", "zimbabwe": r"Zimbabwe|Zimcem|Harare",
 "jardine": r"Jardine", "kersaf": r"Kersaf", "unioncement": r"Union Cement|Holcim Philippines", "siam": r"Siam (City )?Cement", "hollinger": r"Hollinger",
 "telewest": r"Telewest|Virgin Media", "newworld": r"New World Development", "liberty": r"Liberty (Media|Global)", "whiteheadmann": r"Whitehead Mann",
 "walmart": r"Wal-?Mart|Sam's Club|Walton", "dell": r"\bDell\b", "ebay": r"eBay", "erie": r"Erie", "hershey": r"Hershey Creamery", "northwest": r"Northwest Airlines",
 "blackarrow": r"Black Arrow", "welsh": r"Welsh insurance", "georgica": r"Georgica", "readers": r"Readers Digest", "estee": r"Est[ée]e Lauder", "phelps": r"Phelps Dodge",
 "mdc": r"\bMDC\b", "gm": r"General Motors|\bGM\b",
 "buffett": r"Buffett", "munger": r"Munger", "keynes": r"Keynes", "darwin": r"Darwin", "zeckhauser": r"Zeckhauser", "miller": r"Bill Miller", "taleb": r"Taleb",
 "bogle": r"Bogle", "bezos": r"Bezos", "sinegal": r"Sinegal", "santafe": r"Santa ?Fe|SFI", "rand": r"Ayn Rand", "mauboussin": r"Mauboussin", "ariely": r"Ariely", "zak": r"\bZak\b",
 "resorts": r"Resorts World", "midland": r"Midland Realty", "fleetwood": r"Fleetwood", "primedia": r"Primedia", "schibsted": r"Schibsted", "nextmedia": r"Next Media",
 "sony": r"\bSony\b", "ford": r"\bFord\b", "apple": r"\bApple\b", "calpine": r"Calpine", "usg": r"\bUSG\b", "jarvis": r"Jarvis", "thorntons": r"Thornton",
 "mbk": r"Mah Boon Krong", "saks": r"\bSaks\b", "hci": r"\bHCI\b|eTV", "smartone": r"Smartone", "tvb": r"Television Broadcast", "colgate": r"Colgate",
 "readers2": r"Reader'?s Digest", "potash": r"Potash", "brierley": r"Brierley", "siamcity": r"Siam City", "ppc": r"Pretoria Portland", "oldmutual": r"Old Mutual", "geico": r"GEICO|Geico",
}
out = {k: [len(re.findall(p, t)) for t in texts] for k, p in ENTS.items()}
out["readers"] = out.pop("readers2")
DATA.mkdir(exist_ok=True)
json.dump(out, open(DATA / "ents.json", "w"))
print(len(out), "entities")
