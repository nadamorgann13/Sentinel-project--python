import requests
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
             print(all_neos)
    else:
        print("error")
        break





        
        

    