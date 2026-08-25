import requests
from pathlib import Path
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


        
        

    