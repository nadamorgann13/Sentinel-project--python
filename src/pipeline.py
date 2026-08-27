import csv
from pathlib import Path
import requests


def safe_float(value, default=None):
    try:
        return float(value)
    except (ValueError, TypeError):
        return default
def filter_cohort(records):
    return [ record for record in records if record.get("close_approach_data")]  
def calculate_median(values):
    sorted_values = sorted(values)
    return sorted_values[len(sorted_values) // 2]
def clean_records(records):
    magnitude_values = []

    for record in records:
        value = record.get("absolute_magnitude_h")

        if value is not None:
            magnitude_values.append(safe_float(value))

    median_magnitude = calculate_median(magnitude_values)

    cleaned_records = []

    for record in records:
        approaches = record.get("close_approach_data", [])

        approach = approaches[0]

        distance_km = safe_float(approach.get("miss_distance", {}).get("kilometers"))

        distance_lunar = safe_float(approach.get("miss_distance", {}).get("lunar"))

        velocity = safe_float(approach.get("relative_velocity", {}).get("kilometers_per_hour"))

        diameter_max = safe_float(record.get("estimated_diameter", {}).get("kilometers", {}).get("estimated_diameter_max"))

        absolute_magnitude = safe_float(record.get("absolute_magnitude_h"))

        if absolute_magnitude is None:
            absolute_magnitude = median_magnitude

        cleaned_record = {
            "neo_id": record.get("neo_reference_id"),
            "absolute_magnitude_h": absolute_magnitude,
            "estimated_diameter_max_km": diameter_max,
            "miss_distance_km": distance_km,
            "miss_distance_lunar": distance_lunar,
            "relative_velocity_kph": velocity,
            "num_close_approaches": len(approaches),
            "is_potentially_hazardous_asteroid":
                record.get("is_potentially_hazardous_asteroid")
        }

        cleaned_records.append(cleaned_record)

    return cleaned_records
def get_approach_category(distance_lunar):
    if distance_lunar is None:
        return None
    if distance_lunar <= 5:
        return "very_close"
    elif distance_lunar <= 20:
        return "close"
    elif distance_lunar <= 60:
        return "moderate"
    else:
        return "distant"
def engineer_features(records):
    featured_records = []

    for record in records:
        diameter = record["estimated_diameter_max_km"]
        distance_lunar = record["miss_distance_lunar"]

        if diameter is not None and distance_lunar not in (None, 0):
            size_to_distance_ratio = diameter / distance_lunar
        else:
            size_to_distance_ratio = None

        approach_category = get_approach_category(distance_lunar)

        if diameter is not None and distance_lunar is not None:
            priority_watch = ( diameter >= 0.14 and distance_lunar <= 10)
        else:
            priority_watch = False

        featured_record = record.copy()

        featured_record["size_to_distance_ratio"] = size_to_distance_ratio
        featured_record["approach_category"] = approach_category
        featured_record["priority_watch"] = priority_watch

        featured_records.append(featured_record)

    return featured_records
def load_ground_station_log(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        return { row["neo_id"]: row for row in reader}
def join_ground_station(records, ground_station_data, total_known_neos):
    joined_records = []

    for record in records:
        neo_id = str(record["neo_id"])

        log_data = ground_station_data.get(neo_id, {})

        joined_record = record.copy()

        joined_record["observatory_code"] = log_data.get("observatory_code")
        joined_record["confidence_score"] = safe_float(log_data.get("confidence_score"))
        joined_record["total_known_neos"] = total_known_neos

        joined_records.append(joined_record)

    return joined_records
def scale_ratio(records):
    ratios = [record["size_to_distance_ratio"] for record in records if record["size_to_distance_ratio"] is not None]

    min_x = ratios[0]
    max_x = ratios[0]

    for value in ratios:
        if value < min_x:
            min_x = value

        if value > max_x:
            max_x = value

    for record in records:
        x = record["size_to_distance_ratio"]

        if x is not None:
            if max_x == min_x:
                record["scaled_size_to_distance_ratio"] = 0
            else:
                record["scaled_size_to_distance_ratio"] = ((x - min_x) / (max_x - min_x))
        else:
            record["scaled_size_to_distance_ratio"] = None

    return records 
def validate_priority_watch(records):
    crosstab = {
        (True, True): 0,
        (True, False): 0,
        (False, True): 0,
        (False, False): 0
    }

    for record in records:
        priority = record["priority_watch"]
        nasa_hazardous = record["is_potentially_hazardous_asteroid"]

        crosstab[(priority, nasa_hazardous)] += 1

    return crosstab  
def fetch_nasa_data(dates, api_key):
    all_neos = []

    for start_date, end_date in dates:
        url=f"https://api.nasa.gov/neo/rest/v1/feed?start_date={start_date}&end_date={end_date}&api_key=GehboWogq2EOuimvY5oOLjyd5yX44db2kkuFhd1c"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"NASA API request failed: {e}")   

        payload = response.json()
        for objects in payload["near_earth_objects"].values():
            all_neos.extend(objects)

    return all_neos
def write_clean_data(records, output_path):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not records:
        return

    fieldnames = records[0].keys()

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(records)
def run_pipeline(dates, api_key, ground_station_path, total_known_neos):
    all_neos = fetch_nasa_data(dates, api_key)
    filtered_records = filter_cohort(all_neos)
    cleaned_records = clean_records(filtered_records)
    featured_records = engineer_features(cleaned_records)
    ground_station_data = load_ground_station_log(ground_station_path)
    joined_records = join_ground_station(featured_records,ground_station_data,total_known_neos)
    scaled_records = scale_ratio(joined_records)
    validation = validate_priority_watch(scaled_records)
    print("Validation:", validation)
    write_clean_data(scaled_records,"data/processed/clean_data.csv")

    return scaled_records
if __name__ == "__main__":
    dates = [
        ("2026-07-17", "2026-07-18"),
        ("2026-07-19", "2026-07-20")
    ]

    API_KEY = "GehboWogq2EOuimvY5oOLjyd5yX44db2kkuFhd1c"

    run_pipeline(dates,API_KEY,"data/raw/ground_station_log.csv",total_known_neos=19)