"""
ClinicalTrials.gov API Client

A Python client for interacting with the ClinicalTrials.gov API v2.
Provides functionality to fetch, parse, and analyze clinical trial data.

Author: [Your Name]
License: MIT
"""

import json
import time
from typing import List, Dict, Tuple, Optional, Union
import pandas as pd
import requests
from requests.exceptions import RequestException

class ClinicalTrialParser:
    """Parser for clinical trial data from ClinicalTrials.gov API responses."""
    
    @staticmethod
    def flatten_trial(trial: Dict) -> Dict:
        """
        Flatten a single clinical trial entry from the nested JSON structure.
        
        Args:
            trial (Dict): Raw trial data from the API
            
        Returns:
            Dict: Flattened trial data with simplified structure
        """
        flattened = {}
        
        # Extract protocol section for cleaner access
        protocol = trial['protocolSection']
        
        # Extract basic identification info
        identification = protocol['identificationModule']
        flattened['nct_id'] = identification.get('nctId')
        flattened['org_study_id'] = identification.get('orgStudyIdInfo', {}).get('id')
        flattened['brief_title'] = identification.get('briefTitle')
        
        # Extract status info
        status = protocol['statusModule']
        flattened['overall_status'] = status.get('overallStatus')
        flattened['last_known_status'] = status.get('lastKnownStatus')
        flattened['start_date'] = status.get('startDateStruct', {}).get('date')
        flattened['completion_date'] = status.get('completionDateStruct', {}).get('date')
        
        # Extract sponsor info
        sponsor = protocol['sponsorCollaboratorsModule']
        flattened['sponsor'] = sponsor.get('leadSponsor', {}).get('name')
        
        # Extract study info
        description = protocol.get('descriptionModule', {})
        flattened['brief_summary'] = description.get('briefSummary')
        
        # Extract conditions and keywords
        conditions = protocol.get('conditionsModule', {})
        flattened['conditions'] = ', '.join(conditions.get('conditions', []))
        flattened['keywords'] = ', '.join(conditions.get('keywords', []))
        
        # Extract enrollment and study design info
        design = protocol.get('designModule', {})
        enrollment_info = design.get('enrollmentInfo', {})
        flattened['enrollment_count'] = enrollment_info.get('count')
        flattened['study_type'] = design.get('studyType')
        flattened['phase'] = ', '.join(design.get('phases', []))
        
        # Extract location info
        locations = protocol.get('contactsLocationsModule', {}).get('locations', [])
        if locations:
            flattened['locations'] = ', '.join([
                f"{loc.get('facility', '')} ({loc.get('city', '')}, {loc.get('country', '')})"
                for loc in locations
            ])
        
        return flattened

class ClinicalTrialsAPI:
    """Client for interacting with the ClinicalTrials.gov API."""
    
    BASE_URL = 'https://clinicaltrials.gov/api/v2/studies'
    VERSION_URL = 'https://clinicaltrials.gov/api/v2/version'
    
    def __init__(self, max_retries: int = 5, retry_delay: int = 5):
        """
        Initialize the API client.
        
        Args:
            max_retries (int): Maximum number of retry attempts for failed requests
            retry_delay (int): Delay between retry attempts in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.parser = ClinicalTrialParser()
    
    def get_version(self) -> Dict:
        """
        Get the API version information.
        
        Returns:
            Dict: API version details
        """
        response = requests.get(self.VERSION_URL)
        response.raise_for_status()
        return response.json()
    
    def fetch_trials(self, 
                    condition: str,
                    status: str = 'RECRUITING',
                    page_size: int = 10) -> pd.DataFrame:
        """
        Fetch clinical trials for a specific condition.
        
        Args:
            condition (str): Medical condition to search for
            status (str): Trial status filter (e.g., 'RECRUITING')
            page_size (int): Number of results per page
            
        Returns:
            pd.DataFrame: DataFrame containing all fetched trials
        """
        params = {
            'query.cond': condition,
            'pageSize': page_size,
            'format': 'json',
            'filter.overallStatus': status,
            'pageToken': None
        }
        
        all_trials = pd.DataFrame()
        page = 0
        
        while True:
            for attempt in range(self.max_retries):
                try:
                    response = requests.get(
                        self.BASE_URL,
                        params=params,
                        timeout=10
                    )
                    response.raise_for_status()
                    
                    # Process the current page
                    current_trials = self._process_response(response.text)
                    
                    # Merge with existing results
                    if page == 0:
                        all_trials = current_trials
                    else:
                        all_trials = self._merge_trials(all_trials, current_trials)
                    
                    # Check for next page
                    next_page_token = response.json().get('nextPageToken')
                    if not next_page_token:
                        return all_trials
                    
                    params['pageToken'] = next_page_token
                    page += 1
                    break
                    
                except RequestException as e:
                    print(f"Attempt {attempt + 1} failed: {e}")
                    if attempt == self.max_retries - 1:
                        raise
                    time.sleep(self.retry_delay)
    
    def _process_response(self, response_text: str) -> pd.DataFrame:
        """
        Process API response text into a DataFrame.
        
        Args:
            response_text (str): Raw JSON response from the API
            
        Returns:
            pd.DataFrame: Processed trial data
        """
        data = json.loads(response_text)
        studies = data.get('studies', [])
        flattened_studies = [
            self.parser.flatten_trial(study) for study in studies
        ]
        df = pd.DataFrame(flattened_studies)
        
        # Convert date columns
        date_columns = ['start_date', 'completion_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        return df
    
    @staticmethod
    def _merge_trials(df1: pd.DataFrame,
                     df2: pd.DataFrame,
                     merge_type: str = 'outer') -> pd.DataFrame:
        """
        Merge two DataFrames of clinical trials.
        
        Args:
            df1 (pd.DataFrame): First DataFrame
            df2 (pd.DataFrame): Second DataFrame
            merge_type (str): Type of merge operation
            
        Returns:
            pd.DataFrame: Merged DataFrame
        """
        # Add source indicators
        df1['source'] = 'dataset1'
        df2['source'] = 'dataset2'
        
        # Perform merge
        merged = pd.merge(
            df1, df2,
            on='nct_id',
            how=merge_type,
            suffixes=('_1', '_2')
        )
        
        # Clean up duplicate columns
        cols_to_combine = [
            col.replace('_1', '')
            for col in merged.columns
            if col.endswith('_1')
        ]
        
        for col in cols_to_combine:
            if f'{col}_1' in merged.columns and f'{col}_2' in merged.columns:
                merged[col] = merged[f'{col}_1'].combine_first(merged[f'{col}_2'])
                merged = merged.drop([f'{col}_1', f'{col}_2'], axis=1)
        
        return merged

# Example usage
if __name__ == "__main__":
    # Initialize the client
    client = ClinicalTrialsAPI(max_retries=5, retry_delay=5)
    
    try:
        # Get API version
        version = client.get_version()
        print(f"API Version: {version}")
        
        # Fetch trials for a specific condition
        condition = "Pompe Disease"
        trials_df = client.fetch_trials(condition)
        
        # Display results
        print(f"\nFound {len(trials_df)} trials for {condition}")
        print("\nFirst few trials:")
        print(trials_df[['nct_id', 'brief_title', 'overall_status']].head())
        
    except Exception as e:
        print(f"An error occurred: {e}")