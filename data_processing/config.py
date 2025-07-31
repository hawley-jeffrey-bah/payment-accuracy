from enum import Enum

"""
Store various constants used across the data processing process.
"""

FISCAL_YEAR = 2024

# expected format:  Q<1-4> YYYY
LAST_QUARTERLY_SURVEY = "Q1 2025"
COUNT_GOVERNMENT_WIDE_YEARS_DISPLAYED = 5
COUNT_AGENCY_SPECIFIC_YEARS_DISPLAYED = 4
COUNT_AGENCY_SPECIFIC_YEARS_DISPLAYED_FOR_RECOVERY = 5
COUNT_PROGRAM_SPECIFIC_YEARS_DISPLAYED = 4
COUNT_CONGRESSIONAL_REPORTS_YEARS_DISPLAYED = 2

CONGRESSIONAL_REPORTS = [
    {
        "Id": 1,
        "Name": "Agency Risk Assessments Report"
    },
    {
        "Id": 2,
        "Name": "Agency High-Priority Program Report"
    },
    {
        "Id": 3,
        "Name": "Improper Payment and Unknown Payment Estimation Report"
    },
    {
        "Id": 4,
        "Name": "Agency Actions to Reduce Improper Payments Report"
    },
    {
        "Id": 5,
        "Name": "Agency Actions to Recover Improper Payments Report"
    },
    {
        "Id": 6,
        "Name": "OMB Government Wide Improper Payment Report"
    },
    {
        "Id": 7,
        "Name": "Agency Compliance Plan"
    },
    {
        "Id": 8,
        "Name": "Agency Compliance Plan"
    },
    {
        "Id": 9,
        "Name": "OMB Do Not Pay Initiative Report"
    },
    {
        "Id": 10,
        "Name": "Agency Quarterly High-Priorty Program Report"
    }
]

CONGRESSIONAL_REPORTS_YEAR_TO_VIEW_MAPPING = [
    {
        "Year": 2023,
        "AgencyReports": {
            "1": "congressional_report_1_2024",
            "2": "congressional_report_2_2024"
        },
        "ProgramReports": {
            "3": "congressional_report_3_2024"
        }
    },
    {
        "Year": 2024,
        "AgencyReports": {
            "1": "congressional_report_1_2024",
            "2": "congressional_report_2_2024"
        },
        "ProgramReports": {
            "3": "congressional_report_3_2024"
        }
    },
    {
        "Year": 2025,
        "AgencyReports": {
            "1": "congressional_report_1_2025",
            "2": "congressional_report_2_2025"
        },
        "ProgramReports": {
            "3": "congressional_report_3_2024"
        }
    }
]

class CONGRESSIONAL_REPORTS_FIELD_TYPES(Enum):
    TEXT = 1
    MILLIONS_OF_DOLLARS = 2
    PERCENTAGE = 3
    MULTISELECT_TEXT = 4

CONGRESSIONAL_REPORTS_FIELD_TO_TYPE_MAPPING = {
    "2023": {
        "raa6_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa6_2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MULTISELECT_TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa7_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa7_2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MULTISELECT_TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa8": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "ara2_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        }
    },
    "2024": {
        "raa6_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa6_2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MULTISELECT_TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa7_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa7_2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MULTISELECT_TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa8": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "ara2_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        }
    },
    "2025": {
        "raa6_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa6_2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MULTISELECT_TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa7_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa7_2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MULTISELECT_TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa8": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "raa8_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        },
        "arp17_1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "heading": "",
            "subheading": ""
        }
    }
}

CONGRESSIONAL_REPORTS_FIELD_TO_TYPE_MAPPING_PROGRAMS = {
    "2023": {
        "rac3": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "subheading": "",
            "heading": ""
        },
        "cyp1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Annual Outlay Amount"
        },
        "cyp27": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Improper Payment Estimate"
        },
        "cyp28": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Improper Payment Estimate"
        },
        "cyp21": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp22": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Overpayments Within the Agency Control",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp3": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Overpayments Outside the Agency Control",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp26": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Non-Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp5": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Underpayments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp23": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Underpayments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp6": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Technically Improper Payments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp25": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Technically Improper Payments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp7": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Unknown Payment Estimate"
        },
        "cyp24": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Unknown Payment Estimate"
        },
        "cyp30": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Improper Payment and Unknown Payment Estimate"
        },
        "cyp29": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Improper Payment and Unknown Payment Estimate"
        }
    },
    "2024": {
        "rac3": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "subheading": "",
            "heading": ""
        },
        "cyp1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Annual Outlay Amount"
        },
        "cyp27": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Improper Payment Estimate"
        },
        "cyp28": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Improper Payment Estimate"
        },
        "cyp21": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp22": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Overpayments Within the Agency Control",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp3": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Overpayments Outside the Agency Control",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp26": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Non-Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp5": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Underpayments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp23": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Underpayments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp6": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Technically Improper Payments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp25": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Technically Improper Payments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp7": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Unknown Payment Estimate"
        },
        "cyp24": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Unknown Payment Estimate"
        },
        "cyp30": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Improper Payment and Unknown Payment Estimate"
        },
        "cyp29": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Improper Payment and Unknown Payment Estimate"
        }
    },
    "2025": {
        "rac3": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.TEXT,
            "subheading": "",
            "heading": ""
        },
        "cyp1": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Annual Outlay Amount"
        },
        "cyp27": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Improper Payment Estimate"
        },
        "cyp28": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Improper Payment Estimate"
        },
        "cyp21": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp22": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp2": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Overpayments Within the Agency Control",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp3": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Overpayments Outside the Agency Control",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp26": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Non-Monetary Loss",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp5": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Underpayments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp23": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Underpayments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp6": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "Technically Improper Payments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp25": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "Technically Improper Payments",
            "heading": "Makeup of Improper Payment Estimate"
        },
        "cyp7": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Unknown Payment Estimate"
        },
        "cyp24": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Unknown Payment Estimate"
        },
        "cyp30": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.MILLIONS_OF_DOLLARS,
            "subheading": "",
            "heading": "Improper Payment and Unknown Payment Estimate"
        },
        "cyp29": {
            "type": CONGRESSIONAL_REPORTS_FIELD_TYPES.PERCENTAGE,
            "subheading": "",
            "heading": "Improper Payment and Unknown Payment Estimate"
        }
    }
}