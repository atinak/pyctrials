"""
Advanced usage examples for the Clinical Trials API client.
"""

from pyctrials import ClinicalTrialsAPI
import pandas as pd
from datetime import datetime, timedelta

def analyze_trial_timeline():
    """Analyze trial timelines and duration."""
    client = ClinicalTrialsAPI()
    
    # Fetch trials
    trials = client.fetch_trials("Parkinson Disease")
    
    # Convert dates and calculate duration
    trials['duration'] = (
        pd.to_datetime(trials['completion_date']) - 
        pd.to_datetime(trials['start_date'])
    )
    
    # Analyze duration statistics
    print("Trial Duration Statistics (in days):")
    duration_stats = trials['duration'].dt.days.describe()
    print(duration_stats)
    
    return trials

def sponsor_analysis(trials):
    """Analyze trial sponsors and their patterns."""
    # Group by sponsor
    sponsor_stats = trials.groupby('sponsor').agg({
        'nct_id': 'count',
        'enrollment_count': 'mean',
        'phase': lambda x: x.value_counts().index[0] if len(x) > 0 else None
    }).rename(columns={
        'nct_id': 'trial_count',
        'enrollment_count': 'avg_enrollment',
        'phase': 'most_common_phase'
    })
    
    print("\nTop Sponsors by Trial Count:")
    print(sponsor_stats.sort_values('trial_count', ascending=False).head())
    
    return sponsor_stats

def keyword_analysis(trials):
    """Analyze common keywords and their relationships."""
    # Split keywords into individual terms
    keywords = trials['keywords'].str.split(',').explode()
    
    # Clean and count keywords
    keywords = keywords.str.strip()
    keyword_counts = keywords.value_counts()
    
    print("\nMost Common Keywords:")
    print(keyword_counts.head(10))
    
    return keyword_counts

if __name__ == "__main__":
    # Run timeline analysis
    trials = analyze_trial_timeline()
    
    # Analyze sponsors
    sponsor_stats = sponsor_analysis(trials)
    
    # Analyze keywords
    keyword_stats = keyword_analysis(trials)