"""
ClinicalTrials.gov API Client

A Python client for interacting with the ClinicalTrials.gov API v2.
"""

from .client import ClinicalTrialsAPI, ClinicalTrialParser

__version__ = "0.1.6"
__all__ = ["ClinicalTrialsAPI", "ClinicalTrialParser"]