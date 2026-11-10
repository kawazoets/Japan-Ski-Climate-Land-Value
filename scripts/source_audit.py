"""Audit known primary and secondary source endpoints without inventing data."""
from datetime import datetime, timezone
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import csv
from pathlib import Path

SOURCES = [
    ("resort_count_report", "https://news.jp/i/1380113804442730560"),
    ("mlit_2026_land_price_release", "https://www.mlit.go.jp/report/press/tochi_fudousan_kensetsugyo17_hh_000001_00078.html"),
    ("mlit_2026_land_price_catalog", "https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-L01-2026.html"),
    ("mlit_2026_prefectural_land_survey", "https://www.mlit.go.jp/report/press/tochi_fudousan_kensetsugyo17_hh_000001_00089.html"),
]
dest = Path(__file__).resolve().parents[1] / "data" / "source_audit.csv"
rows = []
for name, url in SOURCES:
    status, detail = "error", ""
    try:
        req = Request(url, headers={"User-Agent": "Japan-Ski-Climate-Land-Value/0.1 (source availability audit)"})
        with urlopen(req, timeout=20) as resp:
            status = str(resp.status)
            detail = resp.headers.get("Content-Type", "")
    except (URLError, HTTPError, TimeoutError, OSError) as exc:
        detail = str(exc)[:300]
    rows.append([datetime.now(timezone.utc).isoformat(), name, url, status, detail])
with dest.open("w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["checked_at_utc", "source", "url", "http_status", "detail"])
    writer.writerows(rows)
print(f"Audited {len(rows)} sources. This is NOT a data acquisition run.")
