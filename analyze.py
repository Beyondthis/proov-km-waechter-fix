# analyze.py
# Breakdown-risk analysis for Vossberg Mobility fleet.
#
# KEY FINDINGS (from fleet_history.csv, 120 cars):
#   The two strongest predictors of breakdown are km_since_service (how close a car is to its
#   next service) and load_factor (how hard the car is driven relative to its capacity).
#   Total odometer mileage and age do NOT reliably separate cars that broke down from those that
#   did not — high-mileage, old cars frequently appear in the no-breakdown group.
#
# METHODOLOGY:
#   For each numeric feature, the mean is compared between the broke_down=1 and broke_down=0
#   groups. Features with the largest mean difference (relative to the overall spread) are
#   used to build a transparent, additive risk score from 0 to 100.  No machine-learning model
#   is used.  The score is a heuristic ranking tool, not a validated breakdown probability.

import pandas as pd


# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
df = pd.read_csv("fleet_history.csv")

FEATURE_COLS = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]

# ---------------------------------------------------------------------------
# 2. Compare feature distributions between the two groups
# ---------------------------------------------------------------------------
broke = df[df["broke_down"] == 1]
fine  = df[df["broke_down"] == 0]

print("=" * 65)
print("Feature means: broke_down=1  vs  broke_down=0")
print(f"{'Feature':<22} {'Broke (mean)':>14} {'Fine (mean)':>12} {'Diff':>8}")
print("-" * 65)

separations: dict[str, float] = {}
for col in FEATURE_COLS:
    m_broke = broke[col].mean()
    m_fine  = fine[col].mean()
    overall_std = df[col].std()
    # Normalised separation: how many standard deviations apart are the two means?
    sep = abs(m_broke - m_fine) / overall_std if overall_std > 0 else 0.0
    separations[col] = sep
    print(f"  {col:<20} {m_broke:>14.2f} {m_fine:>12.2f} {sep:>7.3f} SD")

print("=" * 65)
print()
print("Columns ranked by separation power (higher = better predictor):")
for col, sep in sorted(separations.items(), key=lambda x: x[1], reverse=True):
    print(f"  {col:<22}  separation = {sep:.3f} SD")
print()

# ---------------------------------------------------------------------------
# 3. Build a transparent risk score (0–100) from the top predictors
#
#    We use the two features with the largest separation: km_since_service
#    and load_factor.  Both are normalised to [0, 1] across the fleet, then
#    combined with weights proportional to their separation power, and scaled
#    to 0–100.  This is an additive heuristic — not a probability estimate.
# ---------------------------------------------------------------------------

# Select features whose separation exceeds a minimum threshold (0.2 SD)
THRESHOLD = 0.2
selected = {col: sep for col, sep in separations.items() if sep >= THRESHOLD}

if not selected:
    # Fallback: use top two features regardless
    selected = dict(sorted(separations.items(), key=lambda x: x[1], reverse=True)[:2])

total_sep = sum(selected.values())
weights = {col: sep / total_sep for col, sep in selected.items()}

print(f"Risk score built from {len(selected)} feature(s):")
for col, w in sorted(weights.items(), key=lambda x: x[1], reverse=True):
    print(f"  {col:<22}  weight = {w:.3f}")
print()

# Normalise each selected feature to [0, 1] using min-max scaling
score_df = df[["car_id"]].copy()
score_df["risk_score_raw"] = 0.0

for col, weight in weights.items():
    col_min = df[col].min()
    col_max = df[col].max()
    col_range = col_max - col_min
    if col_range == 0:
        normalised = pd.Series(0.0, index=df.index)
    else:
        normalised = (df[col] - col_min) / col_range
    score_df["risk_score_raw"] += normalised * weight

# Scale to 0–100 and round to one decimal place
raw_min = score_df["risk_score_raw"].min()
raw_max = score_df["risk_score_raw"].max()
raw_range = raw_max - raw_min
if raw_range > 0:
    score_df["risk_score"] = ((score_df["risk_score_raw"] - raw_min) / raw_range * 100).round(1)
else:
    score_df["risk_score"] = 50.0

# Attach original columns for context in the output
output = df[["car_id", "km_since_service", "load_factor", "avg_daily_km",
             "odometer_km", "age_years", "broke_down"]].copy()
output["risk_score"] = score_df["risk_score"]
output = output.sort_values("risk_score", ascending=False).reset_index(drop=True)

# ---------------------------------------------------------------------------
# 4. Print ranked list
# ---------------------------------------------------------------------------
print("=" * 85)
print(f"{'Rank':<5} {'Car ID':<12} {'Risk':>6} {'km_since_svc':>14} {'load':>7} "
      f"{'daily_km':>10} {'odometer':>10} {'age':>5} {'broke':>6}")
print("-" * 85)
for i, row in output.iterrows():
    rank = i + 1
    flag = " <-- BROKE DOWN" if row["broke_down"] == 1 else ""
    print(
        f"{rank:<5} {row['car_id']:<12} {row['risk_score']:>6.1f} "
        f"{row['km_since_service']:>14.0f} {row['load_factor']:>7.2f} "
        f"{row['avg_daily_km']:>10.0f} {row['odometer_km']:>10.0f} "
        f"{row['age_years']:>5.0f} {int(row['broke_down']):>6}{flag}"
    )

print("=" * 85)
print()

# ---------------------------------------------------------------------------
# 5. Validation: how well does the score separate the two groups?
# ---------------------------------------------------------------------------
avg_risk_broke = output.loc[output["broke_down"] == 1, "risk_score"].mean()
avg_risk_fine  = output.loc[output["broke_down"] == 0, "risk_score"].mean()
print("Score sanity check:")
print(f"  Mean risk score for cars that broke down : {avg_risk_broke:.1f}")
print(f"  Mean risk score for cars that did NOT    : {avg_risk_fine:.1f}")
print()
print("NOTE: This score is a heuristic ranking tool based on historical averages.")
print("It is NOT a validated breakdown probability and should be used alongside")
print("engineer judgement, not as a replacement for it.")
