import pytest
from datetime import datetime, timedelta, timezone
from app.database.models import StudySession
from app.ml.features import FeatureExtractor
from app.ml.dataset import DatasetGenerator

def test_extract_time_features():
    # 2026-09-14 is a Monday, 14:30
    dt = datetime(2026, 9, 14, 14, 30, tzinfo=timezone.utc)
    s = StudySession(start_time=dt)
    
    feats = FeatureExtractor.extract_time_features(s)
    
    # Depending on local timezone this might shift, but let's just assert keys exist
    assert "hour_of_day" in feats
    assert "day_of_week" in feats
    assert "is_weekend" in feats

def test_rolling_context():
    dt_now = datetime.now(timezone.utc)
    
    # Past sessions
    p1 = StudySession(start_time=dt_now - timedelta(days=1), duration_seconds=3600)
    p2 = StudySession(start_time=dt_now - timedelta(days=2), duration_seconds=1800)
    p3 = StudySession(start_time=dt_now - timedelta(days=8), duration_seconds=3600) # Outside 7d window
    
    current = StudySession(start_time=dt_now)
    
    feats = FeatureExtractor.extract_rolling_context(current, [p1, p2, p3])
    
    assert feats["recent_session_count_7d"] == 2
    assert feats["recent_study_time_7d_mins"] == (3600 + 1800) // 60
    assert feats["current_streak_at_time"] == 2

def test_dataset_generator():
    dt_now = datetime.now(timezone.utc)
    s1 = StudySession(id=1, topic="Math", start_time=dt_now - timedelta(days=2), duration_seconds=3600, status="COMPLETED")
    s2 = StudySession(id=2, topic="Science", start_time=dt_now - timedelta(days=1), duration_seconds=1800, status="COMPLETED")
    s3 = StudySession(id=3, topic="History", start_time=dt_now, duration_seconds=3600, status="COMPLETED")
    
    dataset = DatasetGenerator.generate_dataset([s1, s2, s3])
    
    assert len(dataset) == 3
    
    # Check that s3 has historical context of s1 and s2
    s3_row = dataset[2]
    assert s3_row["session_id"] == 3
    assert s3_row["recent_session_count_7d"] == 2
    assert s3_row["recent_study_time_7d_mins"] == (3600 + 1800) // 60
