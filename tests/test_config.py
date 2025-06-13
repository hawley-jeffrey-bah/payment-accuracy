"""
This is a simple set of tests to make sure constants are properly defined
"""

import pytest
import re

# Import the module
from data_processing import config

class TestConstants:
    """Tests for our config module"""
    def test_fiscal_year_defined(self):
        """
        Check that the fiscal year is defined.
        """
        assert hasattr(config, 'FISCAL_YEAR')
        assert isinstance(config.FISCAL_YEAR, int)
        assert 2000 <= config.FISCAL_YEAR <= 2100
    def test_government_wide_range_defined(self):
        """
        Check that the count of government wide years displayed is defined.
        """
        assert hasattr(config, 'COUNT_GOVERNMENT_WIDE_YEARS_DISPLAYED')
        assert isinstance(config.COUNT_GOVERNMENT_WIDE_YEARS_DISPLAYED, int)
        assert 0 <= config.COUNT_GOVERNMENT_WIDE_YEARS_DISPLAYED <= 10
    def test_agency_specific_range_defined(self):
        """
        Check that the count of agency-specific years displayed is defined.
        """
        assert hasattr(config, 'COUNT_AGENCY_SPECIFIC_YEARS_DISPLAYED')
        assert isinstance(config.COUNT_AGENCY_SPECIFIC_YEARS_DISPLAYED, int)
        assert 0 <= config.COUNT_AGENCY_SPECIFIC_YEARS_DISPLAYED <= 10
    def test_last_quarter_defined(self):
        """
        Check that the count of government wide years displayed is defined.
        """
        assert hasattr(config, 'LAST_QUARTERLY_SURVEY')
        assert isinstance(config.LAST_QUARTERLY_SURVEY, str)
        match = re.search(r"^Q[1-4] [0-9]{4}$", config.LAST_QUARTERLY_SURVEY)
        assert bool(match)