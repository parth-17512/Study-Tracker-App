import csv
import logging
from app.ml.features import FeatureExtractor

logger = logging.getLogger(__name__)

class DatasetGenerator:
    """Pipeline for iterating over all data and generating an ML-ready dataset."""
    
    @staticmethod
    def generate_dataset(sessions):
        """
        Takes a list of StudySession objects, sorts them chronologically,
        and generates a dataset by applying feature extraction to each.
        """
        dataset = []
        
        # Sort chronologically to simulate time
        valid_sessions = [s for s in sessions if s.start_time and s.status == "COMPLETED"]
        valid_sessions.sort(key=lambda s: s.start_time)
        
        for i, session in enumerate(valid_sessions):
            past_sessions = valid_sessions[:i] # Everything strictly before current
            row = FeatureExtractor.build_feature_row(session, past_sessions)
            dataset.append(row)
            
        return dataset
        
    @staticmethod
    def export_to_csv(sessions, filepath):
        """Generates dataset and writes it out as a CSV file."""
        dataset = DatasetGenerator.generate_dataset(sessions)
        
        if not dataset:
            logger.warning("No completed sessions available to generate ML dataset.")
            return False
            
        try:
            keys = dataset[0].keys()
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(dataset)
            return True
        except Exception as e:
            logger.error(f"Failed to export ML dataset to CSV: {e}")
            return False
