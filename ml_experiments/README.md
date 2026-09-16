# ML Experiments

This directory is reserved for Jupyter Notebooks and Data Science scripts for predicting study behavior.

## Overview

The `StudyTrack` application generates an ML-ready dataset directly from your SQLite database. You can export this dataset by going to **Settings -> Export ML Dataset**.

## Feature Definitions

The `ml_dataset.csv` file contains the following columns:

- `session_id`: Unique database identifier.
- `topic`: The topic you studied.
- `target_duration_mins`: The **target variable**. The actual duration of the session in minutes.
- `hour_of_day`: The local hour (0-23) the session started.
- `day_of_week`: 0 (Monday) to 6 (Sunday).
- `is_weekend`: 1 if Saturday/Sunday, else 0.
- `recent_study_time_7d_mins`: The total minutes studied in the trailing 7-day period strictly prior to this session.
- `recent_session_count_7d`: The count of sessions in the trailing 7-day period strictly prior to this session.
- `current_streak_at_time`: Your continuous daily streak right before this session started.

## Getting Started

1. Ensure you have accumulated real data.
2. Export `ml_dataset.csv` from the app.
3. Install pandas/scikit-learn (`pip install pandas scikit-learn`).
4. Build models predicting `target_duration_mins` using the historical rolling features!
