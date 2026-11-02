# What I checked, and what the agent got wrong

## What the agent got wrong

The original code used the wrong formula to convert kilometres into miles. It multiplied by 1.609 instead of dividing. The correct formula divides by 1.60934.

For example, 100 km should be approximately 62.1 miles. This helped me identify the conversion problem.

The original code also did not handle missing `last_service_km` readings safely. A vehicle without this value should not automatically be treated as overdue for service.

I also checked that `fleet_report.py` no longer depends on the removed `get_setting()` function from `config_loader.py`.

## What I checked before I accepted the work

The agent reported that the following checks passed:

1. `pytest` — all four tests passed (three existing tests and one new missing-reading test).
2. `python verify.py` — all 11 verification checks passed.
3. `python analyze.py` — ran without errors and produced the feature-separation analysis.

The verification checks covered:

- Wear calculations use true division instead of floor division.
- A vehicle at 14,900 km since its last service is correctly flagged.
- A vehicle with no `last_service_km` is not flagged.
- The 15,000 km service interval remains unchanged.
- The 80% warning threshold remains unchanged.
- The values in `settings.cfg` remain unchanged.
- The kilometres-to-miles conversion is correct.
- The fleet report handles missing readings without crashing.
- Average wear is calculated correctly.
- A test for missing service readings has been added.
- The breakdown-risk analysis is completed.

I also checked that the protected service interval and warning threshold were not changed.

## What the data actually said

After running `python analyze.py`, the feature-separation analysis produced these results:

| Feature | Broke mean | Fine mean | Separation |
|---|---:|---:|---:|
| `km_since_service` | 11,678 km | 7,261 km | 0.977 SD |
| `avg_daily_km` | 159.7 | 131.4 | 0.610 SD |
| `load_factor` | 0.60 | 0.51 | 0.520 SD |
| `odometer_km` | 53,448 | 53,302 | 0.005 SD |
| `age_years` | 5.88 yrs | 5.89 yrs | 0.003 SD |

- **`km_since_service`** was the strongest feature, with 0.977 SD separation. Vehicles that broke down had travelled more kilometres since their last service.

- **`avg_daily_km`** and **`load_factor`** were moderate features. Vehicles with higher daily usage and heavier loads showed a stronger relationship with breakdowns.

- **`odometer_km`** had almost no separation. Both groups had nearly the same average total mileage. This means total mileage alone was not useful for distinguishing the two groups in this dataset.

- **`age_years`** also had almost no separation. Vehicle age alone did not show a meaningful difference between the groups.

The risk score used the three features with separation above 0.2 SD. Their weights were:

- `km_since_service`: 46%
- `avg_daily_km`: 29%
- `load_factor`: 25%

The average risk score was 67.7 for vehicles that broke down and 41.9 for vehicles that did not.

This suggests that the score can help prioritize vehicle inspections. However, it is not a guaranteed prediction of future breakdowns.

## My conclusion

I learned that it is important to review AI-generated code instead of accepting it without checking.

I also learned the importance of correct calculations, safe handling of missing data, testing, and checking that important configuration values remain unchanged.

The analysis showed that maintenance history and vehicle usage can provide useful information for prioritizing fleet inspections. The risk score should be used as a support tool for maintenance decisions, not as a guarantee that a vehicle will break down.
