Business objectives:
reduce analyst's review time for  space objects by 20% by identifying objects with meaningful size and close pass to the earth
not the full list at the begining of the new year


Target variable:
priority_watch = 1 if (max_estimated_diameter_km >= 0.14) AND(miss_distance_lunar <= 10)
priority_watch = 0 otherwise


Brainstorm Features (minimum 6)
1. estimated_diameter_max_km
2. miss_distance_km
3. miss_distance_lunar
4. relative_velocity_kph
5. num_close_approaches_in_window
6. confidence_score (from the ground-station log)

ROI:
pct_workload_reduction = (1 - (n_flagged / n_total)) * 100
n_total = 19
n_flagged = priority_watch = True
n_flagged = 0
workload reduction = (1 - 0/19) × 100 = 100%



The validation results show complete agreement between our `priority_watch` flag and NASA’s `is_potentially_hazardous_asteroid` flag in this dataset: all 19 records were classified as `(False, False)`, with zero disagreements. However, this agreement should not be interpreted as meaning that the two rules are equivalent. `priority_watch` is our project-specific triage rule based on asteroid size and close-approach distance, while NASA’s hazardous-asteroid flag follows NASA’s own potentially hazardous asteroid classification criteria. Therefore, disagreement is expected in a larger or different dataset because the two flags measure different concepts and are designed for different purposes.

