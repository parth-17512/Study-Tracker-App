import math
from datetime import datetime, timedelta, timezone

class FeatureExtractor:
    """Extracts machine learning features from raw study sessions."""
    
    @staticmethod
    def extract_time_features(session):
        """Extracts hour, day of week, and weekend flags."""
        if not session.start_time:
            return {}
            
        dt = session.start_time
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
            
        local_dt = dt.astimezone()
        
        # 0 = Monday, 6 = Sunday
        dow = local_dt.weekday()
        
        return {
            "hour_of_day": local_dt.hour,
            "day_of_week": dow,
            "is_weekend": 1 if dow >= 5 else 0
        }
        
    @staticmethod
    def extract_rolling_context(session, past_sessions):
        """
        Calculates historical context exactly *before* this session started.
        `past_sessions` must be a list of sessions strictly prior to `session`.
        """
        if not session.start_time:
            return {}
            
        cutoff = session.start_time
        
        recent_7d_duration = 0
        recent_7d_count = 0
        
        # Calculate 7-day rolling window
        seven_days_ago = cutoff - timedelta(days=7)
        
        for p in past_sessions:
            if not p.start_time:
                continue
            if p.start_time >= seven_days_ago:
                recent_7d_count += 1
                recent_7d_duration += (p.duration_seconds or 0)
                
        # Approximate current streak before this session
        streak = 0
        if past_sessions:
            # Sort past sessions descending by time
            sorted_past = sorted([p for p in past_sessions if p.start_time], key=lambda x: x.start_time, reverse=True)
            if sorted_past:
                last_dt = sorted_past[0].start_time
                # If the last session was yesterday or today (before this one), count the streak
                diff_days = (cutoff.date() - last_dt.date()).days
                if diff_days <= 1:
                    streak = 1
                    current_check_date = last_dt.date()
                    for p in sorted_past[1:]:
                        d = (current_check_date - p.start_time.date()).days
                        if d == 0:
                            continue # Same day, skip
                        elif d == 1:
                            streak += 1
                            current_check_date = p.start_time.date()
                        else:
                            break # Streak broken
                            
        return {
            "recent_study_time_7d_mins": recent_7d_duration // 60,
            "recent_session_count_7d": recent_7d_count,
            "current_streak_at_time": streak
        }

    @staticmethod
    def build_feature_row(session, past_sessions):
        """Returns a flat dictionary of all features for a single session."""
        row = {
            "session_id": session.id,
            "topic": session.topic,
            "target_duration_mins": (session.duration_seconds or 0) // 60
        }
        
        time_feats = FeatureExtractor.extract_time_features(session)
        row.update(time_feats)
        
        ctx_feats = FeatureExtractor.extract_rolling_context(session, past_sessions)
        row.update(ctx_feats)
        
        return row
