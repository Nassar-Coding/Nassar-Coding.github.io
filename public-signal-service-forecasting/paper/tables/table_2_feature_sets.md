# Table 2: Feature Sets

Source: `src/config.py` (FEATURE_SETS) and `docs/model_card.md`.

| Feature set | Features |
|-------------|----------|
| internal_historical | borough, complaint_group, request_lag_1, request_lag_7, rolling_mean_7, rolling_mean_14, rolling_std_7, rolling_std_14 |
| calendar_augmented | internal_historical + is_weekend, is_holiday, day_of_week, month, quarter, year, day_of_year, week_of_year, is_month_start, is_month_end |
| weather_augmented | internal_historical + precipitation_mm, temp_max_c, temp_min_c, temp_avg_c, snowfall_mm, snow_depth_mm, wind_speed_ms |
| calendar_weather_augmented | internal_historical + calendar features + weather features |

Notes:
- `borough` and `complaint_group` are one-hot encoded; numeric features pass
  through.
- Lag and rolling features use only past observations; rolling statistics are
  shifted by one day to avoid same-day or future leakage.
- Calendar features are deterministic functions of the date. Weather features
  are the real NOAA daily series joined by date (a single-station city-level
  proxy).
