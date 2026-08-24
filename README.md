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
