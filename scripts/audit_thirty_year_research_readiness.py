"""30-year research gate: never mislabel 2016–2026 observations as 1996–2026."""
import csv,json,datetime,collections
from pathlib import Path
P=Path(__file__).resolve().parents[1];D=P/"data";R=P/"reports";R.mkdir(exist_ok=True)
def read(path):
 with path.open(encoding="utf-8-sig",newline="") as f:return list(csv.DictReader(f))
config=json.loads((P/"config/research_period.json").read_text(encoding="utf-8"))
land=read(D/"ski_resort_mlit_buffer_summary_2016_2026.csv")
snow=read(D/"jma_national_combined_winter_metrics_2016_2025.csv")
cohort={r["candidate_id"] for r in land}
station={r["station_id"] for r in snow}
snowyears=sorted({int(r["winter_start_year"]) for r in snow})
radius=collections.Counter(int(r["radius_km"]) for r in land)
required_start=config["primary_real_estate_period"]["start_year"]
required_end=config["primary_real_estate_period"]["end_year"]
climate_start=config["climate_reference_period"]["start_year"]
# Explicitly report unavailable longitudinal data instead of pretending coverage.
result={"run_date_utc":datetime.datetime.now(datetime.timezone.utc).date().isoformat(),"research_question":config["research_question"],"required_land_price_period":[required_start,required_end],"available_comparable_land_price_endpoints":[2016,2026],"required_climate_start_year":climate_start,"available_winter_snow_start_years":snowyears,"unique_resorts_with_land_buffer_records":len(cohort),"unique_jma_stations_in_winter_metrics":len(station),"land_buffer_row_counts_by_radius":dict(sorted(radius.items())),"status":"THIRTY_YEAR_DATA_NOT_YET_AVAILABLE","must_not_claim":"A 30-year climate-real-estate effect has been established"}
(R/"thirty_year_research_data_gate.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
(R/"thirty_year_research_data_gate.md").write_text("# Thirty-year climate × real estate research: evidence gate\n\n"+f"**Status: {result['status']}**\n\n"+f"- Research land-price window: {required_start}–{required_end}\n- Existing land-price endpoints: 2016 and 2026 only\n- Climate baseline requested: from {climate_start}\n- Existing winter snow series: {min(snowyears)}–{max(snowyears)}\n- Resort IDs with existing land buffer rows: {len(cohort)}\n- JMA stations in existing snow series: {len(station)}\n\n## Immediate conclusion\n\nExisting national data support **a preliminary 2016–2026 descriptive comparison**, not a 30-year climate impact conclusion. Do not label these as 1996–2026 findings. Existing snow–land correlations are unadjusted and not causal.\n\n## Work remaining\n\n1. Acquire and harmonize historical land-price observations back to 1996, preserving consistent observation-point identity and sample changes.\n2. Acquire JMA long-term air temperature and snow observations back to the chosen climate baseline, checking station relocations, altitude and observation definitions.\n3. Run climate × land-price panel analysis with regional controls, urban proximity, tourism development and geographic clustering.\n4. Produce final report distinguishing evidence, uncertainty and unavailable data.\n",encoding="utf-8")
print(json.dumps(result,ensure_ascii=False))
