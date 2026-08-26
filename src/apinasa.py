import requests
from pathlib import Path
def inspect_types(value, path="root"):
    if isinstance(value, dict):
        for key, item in value.items():
            inspect_types(item, f"{path}.{key}")

    elif isinstance(value, list):
        if value:
            inspect_types(value[0], f"{path}[0]")

    else:
        print(f"{path}: {type(value).__name__}")

all_neos=[]
dates=[("2026-07-17","2026-07-18"),("2026-07-19","2026-07-20")]
for start_date,end_date in dates:
    url=f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key=GehboWogq2EOuimvY5oOLjyd5yX44db2kkuFhd1c"
    response=requests.get(url)
    if response.status_code==200:
        payload=response.json()
        for date,objects in payload["near_earth_objects"].items():
            #for obj in objects:
             all_neos.extend(objects)
            # print(all_neos)
    else:
        print("error")
        break
  

neo_ids=[str(obj["neo_reference_id"])for obj in all_neos]
neo_ids=list(dict.fromkeys(neo_ids))
Path("data/raw").mkdir(parents=True, exist_ok=True)

Path("data/raw/extracted_ids.txt").write_text( "\n".join(neo_ids),encoding="utf-8")

print(f"Extracted {len(neo_ids)} unique NEO ids.")

print(all_neos[0]["close_approach_data"])

records=[]
for obj in all_neos:
    approaches=obj.get("close_approach_data",[])
    num_close_approaches=len(approaches)
    if approaches:
        approach=approaches[0]
        try:
          distance_km=float(approach["miss_distance"]["kilometers"])
          distance_lunar=float(approach["miss_distance"]["lunar"])
          velocity=float(approach["relative_velocity"]["kilometers_per_hour"])
        except (ValueError ,TypeError) as e:
          distance_km=None
          distance_lunar=None
          velocity=None
    else:
        distance_km=None
        distance_lunar=None
        velocity=None
    try:
        diameter_max=float(obj["estimated_diameter"]["kilometers"]["estimated_diameter_max"])
    except (ValueError, TypeError, KeyError) as e:
        diameter_max=None
    record={"neo_id":obj.get("neo_reference_id"),"num_close_approaches":num_close_approaches,"miss_distance_km":distance_km,"miss_distance_lunar":distance_lunar,"relative_velocity_kph":velocity,"estimated_diameter_max_km":diameter_max}
    records.append(record)
print(len(records))
print(records[0])
for i, obj in enumerate(all_neos[:5]):
    print(f"\n--- Record {i + 1} ---")
    inspect_types(obj)