"""
Basic usage examples for the Clinical Trials API client.
"""

from pyctrials import ClinicalTrialsAPI
import pandas as pd
import matplotlib.pyplot as plt

def basic_search():
    """Basic search for clinical trials."""
    client = ClinicalTrialsAPI()
    
    # Fetch trials for a specific condition
    trials = client.fetch_trials("Pompe Disease")
    
    # Display basic statistics
    print(f"Total trials found: {len(trials)}")
    print("\nTrials by phase:")
    print(trials['phase'].value_counts())
    
    return trials

def analyze_trials(trials):
    """Analyze trial data and create visualizations."""
    # Create phase distribution plot
    phase_dist = trials['phase'].value_counts()
    plt.figure(figsize=(10, 6))
    phase_dist.plot(kind='bar')
    plt.title('Distribution of Clinical Trials by Phase')
    plt.xlabel('Phase')
    plt.ylabel('Number of Trials')
    plt.tight_layout()
    plt.savefig('phase_distribution.png')
    
    # Analyze enrollment numbers
    print("\nEnrollment Statistics:")
    print(trials['enrollment_count'].describe())
    
    # Look at trial locations
    print("\nTop 10 countries with most trials:")
    countries = trials['locations'].str.split(',').explode()
    print(countries.value_counts().head(10))

def compare_conditions():
    """Compare trials for different conditions."""
    client = ClinicalTrialsAPI()
    conditions = ["Pompe Disease", "Fabry Disease", "Gaucher Disease"]
    
    results = {}
    for condition in conditions:
        trials = client.fetch_trials(condition)
        results[condition] = len(trials)
    
    # Create comparison plot
    plt.figure(figsize=(10, 6))
    plt.bar(results.keys(), results.values())
    plt.title('Number of Clinical Trials by Condition')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('condition_comparison.png')

if __name__ == "__main__":
    # Run basic search example
    trials = basic_search()
    
    # Analyze the results
    analyze_trials(trials)
    
    # Compare different conditions
    compare_conditions()