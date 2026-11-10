import csv
from pathlib import Path
root = Path(__file__).resolve().parents[1] / 'data'
for filename, required in {
    'resorts.csv': ['resort_id','name','prefecture','municipality','latitude','longitude','source_url','verified_at'],
    'seasons.csv': ['resort_id','season','scheduled_open','scheduled_close','actual_operating_days','source_url','verified_at'],
    'land_prices.csv': ['point_id','year','latitude','longitude','price_jpy_m2','land_use','source_url'],
}.items():
    with (root / filename).open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == required, f'Invalid columns in {filename}'
        rows = list(reader)
        print(f'{filename}: {len(rows)} data rows')
        for row in rows:
            assert row.get('source_url'), f'Missing source in {filename}'
