"""
Creates markdown files for static site generation.
"""

import config
from itertools import groupby
from operator import itemgetter
import os
import shutil
import sqlite3
import re
import hashlib
import yaml

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITE_DIR = os.path.join(BASE_DIR, "..", "website")

DB_FILE_PATH = os.path.join("transformed", "transformed_data.db")
HOME_MARKUP_FILE_PATH = os.path.join(WEBSITE_DIR, "pages", "home.md")
AGENY_WIDE_FILE_PATH = os.path.join(WEBSITE_DIR, "pages", "agenciesPrograms.md")
AGENCY_SPECIFIC_DIR = os.path.join(WEBSITE_DIR, "pages", "agencies")
PROGRAM_SPECIFIC_DIR = os.path.join(WEBSITE_DIR, "pages", "programs")
AGENCY_DATA_POINTS_FILE_PATH = os.path.join(WEBSITE_DIR, "data", "agency_data_points.json")
DB_FULL_PATH = os.path.join(BASE_DIR, DB_FILE_PATH)

GOVERNMENT_WIDE_FISCAL_YEARS = list(range(config.FISCAL_YEAR - config.COUNT_GOVERNMENT_WIDE_YEARS_DISPLAYED + 1, config.FISCAL_YEAR + 1))
AGENCY_SPECIFIC_FISCAL_YEARS = list(range(config.FISCAL_YEAR - config.COUNT_AGENCY_SPECIFIC_YEARS_DISPLAYED + 1, config.FISCAL_YEAR + 1))

compliance_survey_to_criterion_mapping = {
    'pcp01_1': 'Overall',
    'pcp2_2': '1A',
    'pcp3_2': '1B',
    'pcp4_2': '2A',
    'pcp5_2': '2B',
    'pcp6_2': '3',
    'pcp7_2': '4',
    'pcp8_2': '5A',
    'pcp9_2': '5B',
    'pcp10_2': '5C',
    'pcp11_2': '6'
}

compliance_survey_to_criterion_mapping_2022 = {
    'pcp01': 'Overall',
    'pcp2': '1A',
    'pcp3': '1B',
    'pcp4': '2A',
    'pcp5': '2B',
    'pcp6': '3',
    'pcp7': '4',
    'pcp8': '5A',
    'pcp9': '5B',
    'pcp10': '5C',
    'pcp11': '6'
}

SLUGIFIED_PROGRAM_NAME_MAPPINGS = {}

def slugify(name, max_length=60):
    slug = re.sub(r'[^a-zA-Z0-9]+', '-', name.lower()).strip('-')
    if len(slug) > max_length:
        # Truncate and add hash to preserve uniqueness
        slug = slug[:max_length] + '-' + hashlib.md5(name.encode()).hexdigest()[:8]
    return slug

def slugifyProgramNames(cursor: sqlite3.Cursor):
    query = f"""
        SELECT DISTINCT
            Agency,
            [Program_Name]
        FROM [all_programs_data_aggregation]
    """

    cursor.execute(query)
    programs = cursor.fetchall()
    for program in programs:
        SLUGIFIED_PROGRAM_NAME_MAPPINGS[program["Program_Name"]] = slugify(program["Program_Name"])
    print("Successfully slugified program names")

def generate_home_page(cursor: sqlite3.Cursor):
    """
    Generate the home page using transformed all_programs_min_max_rates database.
    """

    placeholders = ','.join(['?'] * len(GOVERNMENT_WIDE_FISCAL_YEARS))

    query = f"""
        SELECT
            ROUND(MIN(Payment_Accuracy_Rate), 1) AS [Payment_Accuracy_Rate_Min],
            ROUND(MAX(Payment_Accuracy_Rate), 1) AS [Payment_Accuracy_Rate_Max],
            ROUND(MIN(Improper_Payments_Rate), 1) AS [Improper_Payments_Rate_Min],
            ROUND(MAX(Improper_Payments_Rate), 1) AS [Improper_Payments_Rate_Max],
            ROUND(MIN(Unknown_Payments_Rate), 1) AS [Unknown_Payments_Rate_Min],
            ROUND(MAX(Unknown_Payments_Rate), 1) AS [Unknown_Payments_Rate_Max]
        FROM government_wide_data_aggregation
        WHERE Fiscal_Year IN ({placeholders})
    """

    cursor.execute(query, GOVERNMENT_WIDE_FISCAL_YEARS)

    result = cursor.fetchone()

    Payment_Accuracy_Rate_Min = result[0]
    Payment_Accuracy_Rate_Max = result[1]
    Improper_Payments_Rate_Min = result[2]
    Improper_Payments_Rate_Max = result[3]
    Unknown_Payments_Rate_Min = result[4]
    Unknown_Payments_Rate_Max = result[5]

    query = f"""
        SELECT
            Agency,
            Agency_Name,
            High_Priority_Programs AS High_Priority_Programs,
            ROUND(Improper_Payments_Rate, 1) AS Improper_Payments_Rate
        FROM all_agencies_data_aggregation
        WHERE Fiscal_Year = ?
        ORDER BY Improper_Payments_Rate ASC
        LIMIT 3
    """

    cursor.execute(query, (config.FISCAL_YEAR,))

    columns = [desc[0] for desc in cursor.description]
    highest_performing_agencies = [dict(zip(columns, row)) for row in cursor.fetchall()]

    query = f"""
        SELECT
            Agency,
            Agency_Name,
            High_Priority_Programs AS High_Priority_Programs,
            ROUND(Improper_Payments_Rate, 1) AS Improper_Payments_Rate
        FROM all_agencies_data_aggregation
        WHERE Fiscal_Year = ?
        ORDER BY Improper_Payments_Rate DESC
        LIMIT 3
    """

    cursor.execute(query, (config.FISCAL_YEAR,))

    columns = [desc[0] for desc in cursor.description]
    lowest_performing_agencies = [dict(zip(columns, row)) for row in cursor.fetchall()]

    dataPointQuery = f"""
            SELECT
                [Payment_Accuracy_Rate],
                [Improper_Payments_Rate],
                [Unknown_Payments_Rate],
                [Fiscal_Year]
            FROM government_wide_data_aggregation
            WHERE [Fiscal_Year] IN ({placeholders})
            ORDER BY [Fiscal_Year]
        """

    cursor.execute(dataPointQuery, GOVERNMENT_WIDE_FISCAL_YEARS)

    dataPointsDetails = cursor.fetchall()
    accuracyRates = []
    improperRates = []
    unknownRates = []
    fiscalYears = []

    for dataPoint in dataPointsDetails:
        accuracyRates.append(dataPoint["Payment_Accuracy_Rate"])
        improperRates.append(dataPoint["Improper_Payments_Rate"])
        unknownRates.append(dataPoint["Unknown_Payments_Rate"])
        fiscalYears.append(dataPoint["Fiscal_Year"])

    page = {
        'title': 'Home',
        'layout': 'index',
        'permalink': '/',
        'payment_accuracy_rate_min': Payment_Accuracy_Rate_Min,
        'payment_accuracy_rate_max': Payment_Accuracy_Rate_Max,
        'improper_payments_rate_min': Improper_Payments_Rate_Min,
        'improper_payments_rate_max': Improper_Payments_Rate_Max,
        'unknown_payments_rate_min': Unknown_Payments_Rate_Min,
        'unknown_payments_rate_max': Unknown_Payments_Rate_Max,
        'highest_performing_agencies': highest_performing_agencies,
        'lowest_performing_agencies': lowest_performing_agencies,
        'fiscal_year': config.FISCAL_YEAR,
        'payment_accuracy_rates': str(accuracyRates),
        'improper_payments_rates': str(improperRates),
        'unknown_payments_rates': str(unknownRates),
        'improper_payments_years': str(fiscalYears)
    }

    os.makedirs(os.path.dirname(HOME_MARKUP_FILE_PATH), exist_ok=True)
    with open(HOME_MARKUP_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write('---\n')
        yaml.dump(page, file, allow_unicode=True)
        file.write('---\n')
    print("Successfully generated homepage markup file")

def generate_agency_programs_page(cursor: sqlite3.Cursor):
    query = f"""
        SELECT
            all_agencies_years.Agency,
            a.Program_Name,
            COALESCE(ROUND(a.Outlays, 2),0) AS [Total_Spent_Federal_Funding],
            COALESCE(a.High_Priority_Program,0),
            COALESCE(ROUND(a.IP_Rate, 2),0),
            CASE
                WHEN b.IP_Rate IS NULL THEN NULL
                ELSE ROUND(b.IP_Rate - a.IP_Rate, 2)
            END AS [Relative_Change]
        FROM all_agencies_years
            LEFT JOIN all_programs_data_aggregation a
            ON all_agencies_years.[Agency] = a.[Agency] AND all_agencies_years.[Fiscal_Year] = a.[Fiscal_Year]
            LEFT JOIN (
                SELECT
                    Agency,
                    Program_Name,
                    IP_Rate
                FROM all_programs_data_aggregation
                WHERE Fiscal_Year = ?
            ) b
            ON a.Agency = b.Agency
            AND a.Program_Name = b.Program_Name
        WHERE all_agencies_years.Fiscal_Year = ?
    """

    cursor.execute(query, (config.FISCAL_YEAR-1,config.FISCAL_YEAR))

    program_rows = cursor.fetchall()

    query = f"""
        SELECT
            all_agencies_years.Agency,
            all_agencies_years.Agency_Name,
            COALESCE(ROUND(a.Outlays, 2),0) AS [Total_Spent_Federal_Funding],
            COALESCE(c.Num_Programs,0),
            COALESCE(a.Susceptible_Programs,0),
            COALESCE(a.High_Priority_Programs,0),
            COALESCE(ROUND(a.Improper_Payments_Rate, 2),0),
            CASE
                WHEN b.Improper_Payments_Rate IS NULL THEN NULL
                ELSE ROUND(b.Improper_Payments_Rate - a.Improper_Payments_Rate, 2)
            END AS [Relative_Change]
        FROM all_agencies_years
            LEFT JOIN all_agencies_data_aggregation a
            ON all_agencies_years.[Agency] = a.[Agency] AND all_agencies_years.[Fiscal_Year] = a.[Fiscal_Year]
            LEFT JOIN (
                SELECT
                    Agency,
                    Improper_Payments_Rate
                FROM all_agencies_data_aggregation
                WHERE Fiscal_Year = ?
            ) b
            ON a.Agency = b.Agency
            LEFT JOIN (
                SELECT
                    [Agency],
                    [Fiscal_Year],
                    COUNT(*) AS [Num_Programs]
                FROM [program_compliance]
                GROUP BY [Agency], [Fiscal_Year]
            ) c ON all_agencies_years.Agency = c.Agency AND all_agencies_years.Fiscal_Year = c.Fiscal_Year
        WHERE all_agencies_years.Fiscal_Year = ?
        ORDER BY COALESCE(ROUND(a.Outlays, 2),0) DESC
    """

    cursor.execute(query, (config.FISCAL_YEAR-1,config.FISCAL_YEAR))

    agency_rows = cursor.fetchall()

    programs_by_agency = {}

    for row in program_rows:
        agency = row[0]
        program_name = row[1]
        program = {
            "program_name": program_name,
            "total_spent_federal_funding": row[2],
            "high_priority_program": bool(row[3]),
            "ip_rate": row[4],
            "relative_change": row[5],
        }
        if program_name in SLUGIFIED_PROGRAM_NAME_MAPPINGS:
            program["slug"] = SLUGIFIED_PROGRAM_NAME_MAPPINGS[program_name]
        programs_by_agency.setdefault(agency, []).append(program)

    agencies_data = []

    for row in agency_rows:
        agency_code = row[0]
        agency_data = {
            "agency": agency_code,
            "agency_name": row[1],
            "total_spent_federal_funding": row[2],
            "num_programs": row[3],
            "susceptible_programs": row[4],
            "high_priority_programs": row[5],
            "improper_payments_rate": row[6],
            "relative_change": row[7],
            "programs": programs_by_agency.get(agency_code, []),
        }
        agencies_data.append(agency_data)
    
    page = {
        'title': 'Agencies & Programs',
        'layout': 'agency-wide',
        'permalink': '/agencies-and-programs',
        'agencies': agencies_data
    }

    os.makedirs(os.path.dirname(AGENY_WIDE_FILE_PATH), exist_ok=True)
    with open(AGENY_WIDE_FILE_PATH, 'w', encoding='utf-8') as file:
        file.write('---\n')
        yaml.dump(page, file, allow_unicode=True)
        file.write('---\n')
    print("Successfully generated agency-wide markup file")

def map_program_compliance(program):
    mappedProgram = { 'Name': program['Program_Name'] }
    for key, value in compliance_survey_to_criterion_mapping.items():
        mappedProgram['Compliant_' + value] = str(program[key]).upper() == 'YES'

    return mappedProgram

def map_program_compliance_2022(program):
    mappedProgram = { 'Name': program['Program_Name'] }
    for key, value in compliance_survey_to_criterion_mapping_2022.items():
        mappedProgram['Compliant_' + value] = str(program[key]).upper() != 'NON-COMPLIANT'

    return mappedProgram

def group_and_map_risks(risks):
    groupedRiskDetails = {key: list(group) for key, group in groupby(risks, key=itemgetter("Program_Name"))}
    return list(map(lambda x: {
        "Program_Name": x[0],
        "Assessments": list(map(lambda y: { "Susceptible": y["Susceptible"], "Fiscal_Year": y["Fiscal_Year"] }, x[1]))
    }, groupedRiskDetails.items()))

def extract_column_from_results(fieldName, results):
    return list(map(lambda x: x[fieldName], results))

def generate_agency_specific_pages_for_year(cursor: sqlite3.Cursor, year):
    query = f"""
        SELECT
            a.[Agency],
            a.[Agency_Name],
            a.[Fiscal_Year],
            b.[Confirmed_Fraud]
        FROM [all_agencies_years] a
        LEFT JOIN [all_agencies_data_aggregation] b
        ON a.[Agency] = b.[Agency] AND a.[Fiscal_Year] = b.[Fiscal_Year]
        WHERE a.[Fiscal_Year] = ?
    """

    cursor.execute(query, (year,))

    agencies = cursor.fetchall()

    yearsCriteria = ','.join(['?'] * len(AGENCY_SPECIFIC_FISCAL_YEARS))

    os.makedirs(AGENCY_SPECIFIC_DIR, exist_ok=True)
    for agency in agencies:

        yearsAvailableQuery = f"""
            SELECT
                [Fiscal_Year]
            FROM [all_agencies_years]
            WHERE [Agency] = ? AND [Fiscal_Year] IN ({yearsCriteria})
            ORDER BY [Fiscal_Year] DESC
        """

        cursor.execute(yearsAvailableQuery, [agency["Agency"]] + AGENCY_SPECIFIC_FISCAL_YEARS)
        yearsAvailable = cursor.fetchall()

        # this object is used to merge agency data and raw detail data
        agencyObj = {
            "Agency": agency["Agency"],
            "Agency_Name": agency["Agency_Name"],
            "Fiscal_Year": agency["Fiscal_Year"],
            "Confirmed_Fraud": agency["Confirmed_Fraud"],
            "layout": "agency-specific",
            "Years_Available": list(map(lambda x: x["Fiscal_Year"], yearsAvailable)),
            "Is_Placeholder": False
        }

        agencyQuery = f"""
            SELECT
                [agency],
                [Key],
                [Title],
                [value],
                [Fiscal_Year]
            FROM [agency_data_raw]
            WHERE [Fiscal_Year] = ? AND [Agency] = ?
        """
        cursor.execute(agencyQuery, (year, agency["Agency"]))

        details = cursor.fetchall()

        # this relies on the assumption that there is one record per year-agency-key 
        # if multiselect values are ever needed, use a separate extract file and table
        for detail in details:
            key = "detail_" + detail["Key"]
            agencyObj[key] = detail["value"]

        # prior to 2021, no null record was created for summarization
        paymentRecoveryDetailsQuery = f"""
            SELECT
                [Agency],
                [Fiscal_Year],
                [key],
                SUM([value]) AS [value]
            FROM [payment_recovery_details]
            WHERE [Fiscal_Year] = ? AND [Agency] = ? AND [Program_Name] IS NOT NULL
            GROUP BY [Agency], [Fiscal_Year], [key]
        """

        if year > 2021:
            paymentRecoveryDetailsQuery = f"""
                SELECT
                    [Agency],
                    [Fiscal_Year],
                    [key],
                    [value]
                FROM [payment_recovery_details]
                WHERE [Fiscal_Year] = ? AND [Agency] = ? AND [Program_Name] IS NULL
            """

        cursor.execute(paymentRecoveryDetailsQuery, (year, agency["Agency"]))

        recoveryDetails = cursor.fetchall()

        for recoveryDetail in recoveryDetails:
            key = "recovery_" + str(recoveryDetail["key"]).replace(" ","_")
            agencyObj[key] = recoveryDetail["value"]

        recoveryYears = list(range(year - config.COUNT_AGENCY_SPECIFIC_YEARS_DISPLAYED_FOR_RECOVERY + 1, year + 1))
        recoveryYearsCriteria = ','.join(['?'] * len(recoveryYears))

        paymentRecoveryAmountsQuery = f"""
            SELECT
                [Fiscal_Year],
                [Overpayment_Amount_Identified_For_Recapture_($M)],
                [Overpayment_Amount_Recovered_($M)]
            FROM [recovery_amounts]
            WHERE [Agency] = ? AND [Fiscal_Year] IN ({recoveryYearsCriteria})
            ORDER BY [Fiscal_Year]
        """
        cursor.execute(paymentRecoveryAmountsQuery, [agency["Agency"]] + recoveryYears)
        recoveryAmountDetails = cursor.fetchall()
        agencyObj["Overpayment_Amounts_Identified"] = str(extract_column_from_results("Overpayment_Amount_Identified_For_Recapture_($M)", recoveryAmountDetails))
        agencyObj["Overpayment_Amounts_Recovered"] = str(extract_column_from_results("Overpayment_Amount_Recovered_($M)", recoveryAmountDetails))
        agencyObj["Overpayment_Years"] = str(extract_column_from_results("Fiscal_Year", recoveryAmountDetails))

        dataPointQuery = f"""
            SELECT
                [Payment_Accuracy_Rate],
                [Improper_Payments_Rate],
                [Unknown_Payments_Rate],
                COALESCE([Outlays],0)
                    - COALESCE([CY_Overpayment_Amount],0)
                    - COALESCE([CY_Underpayment_Amount],0)
                    - COALESCE([CY_Technically_Improper_Amount],0)
                    - COALESCE([CY_Unknown_Payments],0)
                    AS [Payment_Accuracy_Amount],
                COALESCE([CY_Overpayment_Amount],0) AS [Overpayment_Amount],
                COALESCE([CY_Underpayment_Amount],0) AS [Underpayment_Amount],
                COALESCE([CY_Technically_Improper_Amount],0) AS [Technically_Improper_Amount],
                COALESCE([CY_Unknown_Payments],0) AS [Unknown_Amount],
                [Fiscal_Year]
            FROM all_agencies_data_aggregation
            WHERE [Agency] = ? AND [Fiscal_Year] IN ({yearsCriteria})
            ORDER BY [Fiscal_Year]
        """

        cursor.execute(dataPointQuery, [agency["Agency"]] + AGENCY_SPECIFIC_FISCAL_YEARS)

        dataPointsDetails = cursor.fetchall()

        accuracyRates = extract_column_from_results("Payment_Accuracy_Rate", dataPointsDetails)
        improperRates = extract_column_from_results("Improper_Payments_Rate", dataPointsDetails)
        unknownRates = extract_column_from_results("Unknown_Payments_Rate", dataPointsDetails)
        agencyObj["Payment_Accuracy_Rates"] = str(accuracyRates)
        agencyObj["Improper_Payments_Rates"] = str(improperRates)
        agencyObj["Unknown_Payments_Rates"] = str(unknownRates)
        agencyObj["Payment_Accuracy_Amounts"] = str(extract_column_from_results("Payment_Accuracy_Amount", dataPointsDetails))
        agencyObj["Overpayment_Amounts"] = str(extract_column_from_results("Overpayment_Amount", dataPointsDetails))
        agencyObj["Underpayment_Amounts"] = str(extract_column_from_results("Underpayment_Amount", dataPointsDetails))
        agencyObj["Technically_Improper_Amounts"] = str(extract_column_from_results("Technically_Improper_Amount", dataPointsDetails))
        agencyObj["Unknown_Amounts"] = str(extract_column_from_results("Unknown_Amount", dataPointsDetails))
        agencyObj["Payment_Accuracy_Rate_Min"] = round(min(accuracyRates, default=0),1)
        agencyObj["Payment_Accuracy_Rate_Max"] = round(max(accuracyRates, default=0),1)
        agencyObj["Improper_Payments_Rate_Min"] = round(min(improperRates, default=0),1)
        agencyObj["Improper_Payments_Rate_Max"] = round(max(improperRates, default=0),1)
        agencyObj["Unknown_Payments_Rate_Min"] = round(min(unknownRates, default=0),1)
        agencyObj["Unknown_Payments_Rate_Max"] = round(max(unknownRates, default=0),1)
        agencyObj["Improper_Payments_Data_Years"] = str(extract_column_from_results("Fiscal_Year", dataPointsDetails))

        if (year > 2022):
            piiaNonCompliantProgramsQuery = f"""
                SELECT
                    [Program_Name],
                    [pcp01_1],
                    [pcp2_2],
                    [pcp3_2],
                    [pcp4_2],
                    [pcp5_2],
                    [pcp6_2],
                    [pcp7_2],
                    [pcp8_2],
                    [pcp9_2],
                    [pcp10_2],
                    [pcp11_2]
                FROM program_compliance
                WHERE [Agency] = ? AND [Fiscal_Year] = ?
                ORDER BY [Program_Name]
            """

            cursor.execute(piiaNonCompliantProgramsQuery, (agency["Agency"], year))

            piiaProgramDetails = cursor.fetchall()

            nonCompliantProgramDetails = list(filter(lambda x: str(x['pcp01_1']).upper() == 'NO', piiaProgramDetails))
            compliantProgramDetails = list(filter(lambda x: str(x['pcp01_1']).upper() != 'NO', piiaProgramDetails))

            agencyObj["PIIA2019_NonCompliant_Programs"] = list(map(map_program_compliance, nonCompliantProgramDetails))
            agencyObj["PIIA2019_Compliant_Programs"] = list(map(map_program_compliance, compliantProgramDetails))
        else:
            piiaNonCompliantProgramsQuery = f"""
                SELECT
                    [Program Name] AS [Program_Name],
                    min([value]) filter (where [seq] = 1) as [pcp01],
                    min([value]) filter (where [seq] = 4) as [pcp2],
                    min([value]) filter (where [seq] = 5) as [pcp3],
                    min([value]) filter (where [seq] = 6) as [pcp4],
                    min([value]) filter (where [seq] = 7) as [pcp5],
                    min([value]) filter (where [seq] = 8) as [pcp6],
                    min([value]) filter (where [seq] = 9) as [pcp7],
                    min([value]) filter (where [seq] = 10) as [pcp8],
                    min([value]) filter (where [seq] = 11) as [pcp9],
                    min([value]) filter (where [seq] = 2) as [pcp10],
                    min([value]) filter (where [seq] = 3) as [pcp11]
                FROM (select [Program Name],[value],
                    row_number() over (partition by [Program Name] order by [key]) as seq
                    from [program_data_raw]
                    where [key] IN (
                        'pcp01'
                        ,'pcp2'
                        ,'pcp3'
                        ,'pcp4'
                        ,'pcp5'
                        ,'pcp6'
                        ,'pcp7'
                        ,'pcp8'
                        ,'pcp9'
                        ,'pcp10'
                        ,'pcp11'
                    ) AND [Agency] = ? AND [Fiscal_Year] = ?
                ) t
                GROUP BY [Program Name]
            """

            cursor.execute(piiaNonCompliantProgramsQuery, (agency["Agency"], year))

            piiaProgramDetails = cursor.fetchall()

            nonCompliantProgramDetails = list(filter(lambda x: str(x['pcp01']).upper() == 'NON-COMPLIANT', piiaProgramDetails))
            compliantProgramDetails = list(filter(lambda x: str(x['pcp01']).upper() != 'NON-COMPLIANT', piiaProgramDetails))

            agencyObj["PIIA2019_NonCompliant_Programs"] = list(map(map_program_compliance_2022, nonCompliantProgramDetails))
            agencyObj["PIIA2019_Compliant_Programs"] = list(map(map_program_compliance_2022, compliantProgramDetails))

        # This is a union of the letest 'YES' and 'NO' for each program
        risksQuery = f"""
            SELECT * FROM (SELECT
                a.[Agency],
                a.[Fiscal_Year],
                a.[Program_Name],
                'Yes' AS [Susceptible]
            FROM [risks] a
            JOIN (
                SELECT
                    [Agency],
                    MAX([Fiscal_Year]) AS [LastRiskAssessment],
                    [Program_Name]
                FROM [risks]
                WHERE (upper([raa7_2]) = 'YES' OR upper([Was_the_Program_or_Activity_Susceptible_to_Significant_Improper_]) = 'YES') AND [Agency] = ? AND [Fiscal_Year] <= ?
                GROUP BY [Agency], [Program_Name]
            ) b ON a.[Agency] = b.[Agency] AND UPPER(a.[Program_Name]) = UPPER(b.[Program_Name]) AND a.[Fiscal_Year] = b.[LastRiskAssessment]
            UNION
            SELECT
                c.[Agency],
                c.[Fiscal_Year],
                c.[Program_Name],
                'No' AS [Susceptible]
            FROM [risks] c
            JOIN (
                SELECT
                    [Agency],
                    MAX([Fiscal_Year]) AS [LastRiskAssessment],
                    [Program_Name]
                FROM [risks]
                WHERE (upper([raa6_2]) = 'YES' OR [Was_the_Program_or_Activity_Susceptible_to_Significant_Improper_] IS NOT NULL)
                    AND (upper([Was_the_Program_or_Activity_Susceptible_to_Significant_Improper_]) = 'NO' OR upper([raa7_2]) = 'NO')
                    AND ([Agency] = ? AND [Fiscal_Year] <= ?)
                GROUP BY [Agency], [Program_Name]
            ) d ON c.[Agency] = d.[Agency] AND UPPER(c.[Program_Name]) = UPPER(d.[Program_Name]) AND c.[Fiscal_Year] = d.[LastRiskAssessment]) e
            ORDER BY e.[Program_Name], e.[Fiscal_Year]
        """
        cursor.execute(risksQuery, (str(agency["Agency"]), year, str(agency["Agency"]), year))
        riskDetails = cursor.fetchall()
        agencyObj["Risks"] = group_and_map_risks(riskDetails)

        eligiblityThemesQuery = f"""
            SELECT
                b.[Program Name],
                a.[theme],
                b.[value] AS [Barriers],
                c.[value] AS [Info]
            FROM eligibility_themes a
            LEFT JOIN (SELECT * FROM program_data_raw) b ON concat(a.key,'_2') = b.key
            LEFT JOIN (SELECT * FROM program_data_raw) c ON concat(a.key,'_3') = c.key
            WHERE
                b.[agency] = c.[agency]
                AND b.[Program Name] = c.[Program Name]
                AND b.[Fiscal_Year] = c.[Fiscal_Year]
                AND b.[Agency] = ?
                AND b.[Fiscal_Year] = ?
                AND b.[value] IS NOT NULL
                AND c.[value] IS NOT NULL
            ORDER BY b.[Program Name], a.[theme]
        """
        cursor.execute(eligiblityThemesQuery, (agency["Agency"], year))
        eligibilityThemeDetails = cursor.fetchall()

        # group themes for easier use in jekyll
        agencyObj["Eligibility_Themes"] = []
        lastProgram = None
        for eligibilityThemeDetail in eligibilityThemeDetails:
            if lastProgram == None or lastProgram['Program_Name'] != eligibilityThemeDetail["Program Name"]:
                lastProgram = {
                    'Program_Name': eligibilityThemeDetail["Program Name"],
                    'Themes': []
                }
                agencyObj["Eligibility_Themes"].append(lastProgram)
            lastProgram['Themes'].append({
                "Theme": eligibilityThemeDetail["theme"],
                "Barriers": eligibilityThemeDetail["Barriers"],
                "Info": eligibilityThemeDetail["Info"]
            })

        hide_agency_specific_sections(agencyObj)

        write_agency_md_files(agency["Agency"], agencyObj, year)

    print("Successfully generated agency-specific markup files for FY " + str(year))

def hide_agency_specific_sections(agencyObj):
    hasRecoveryKey = False
    for key in agencyObj.keys():
        if key.startswith("recovery_"):
            hasRecoveryKey = True
            break

    agencyObj["Hide_Integrity_Results"] = "Improper_Payments_Data_Years" not in agencyObj or \
            agencyObj["Improper_Payments_Data_Years"] is None or \
            agencyObj["Improper_Payments_Data_Years"] == '[]'
    # Sparklines with one datapoint are not useful
    agencyObj["Hide_Sparklines"] = agencyObj["Hide_Integrity_Results"] or \
        "," not in agencyObj["Improper_Payments_Data_Years"]

    agencyObj["Hide_Recovery_Details"] = not hasRecoveryKey and \
        ("detail_arp18" not in agencyObj or agencyObj["detail_arp18"] is None or agencyObj["detail_arp18"] == '')
    agencyObj["Hide_Recovery_Audits"] = \
        ("detail_arp17" not in agencyObj or agencyObj["detail_arp17"] is None or agencyObj["detail_arp17"] == '') and \
        ("detail_ara2_1" not in agencyObj or agencyObj["detail_ara2_1"] is None or agencyObj["detail_ara2_1"] == '')
    agencyObj["Hide_Recovery_Info"] = agencyObj["Hide_Recovery_Details"] and \
        ("detail_ara2_1" not in agencyObj or agencyObj["detail_ara2_1"] is None or agencyObj["detail_ara2_1"] == '') and \
        ("Overpayment_Years" not in agencyObj or agencyObj["Overpayment_Years"] is None or agencyObj["Overpayment_Years"] == '[]')

    agencyObj["Hide_Disposition_of_Funds"] = ("recovery_Disposition_of_Funds_through_recovery_audit_Administer_Auditor" not in agencyObj or agencyObj["recovery_Disposition_of_Funds_through_recovery_audit_Administer_Auditor"] is None) and \
        ("recovery_Disposition_of_Funds_through_FM_Improvement_Activities" not in agencyObj or agencyObj["recovery_Disposition_of_Funds_through_FM_Improvement_Activities"] is None) and \
        ("recovery_Disposition_of_Funds_Through_Original_Purpose" not in agencyObj or agencyObj["recovery_Disposition_of_Funds_Through_Original_Purpose"] is None) and \
        ("recovery_Disposition_of_Funds_Through_Office_of_Inspector_General" not in agencyObj or agencyObj["recovery_Disposition_of_Funds_Through_Office_of_Inspector_General"] is None) and \
        ("recovery_Disposition_of_Funds_Through_Returned_to_Treasury" not in agencyObj or agencyObj["recovery_Disposition_of_Funds_Through_Returned_to_Treasury"] is None) and \
        ("recovery_Returned_to_Original_Account" not in agencyObj or agencyObj["recovery_Returned_to_Original_Account"] is None) and \
        ("recovery_Aging_of_Outstanding_OP_Identified_Remaining_Unrecovered" not in agencyObj or agencyObj["recovery_Aging_of_Outstanding_OP_Identified_Remaining_Unrecovered"] is None) and \
        ("recovery_Aging_of_Outstanding_OP_Identified_Amt_0_-_6_months" not in agencyObj or agencyObj["recovery_Aging_of_Outstanding_OP_Identified_Amt_0_-_6_months"] is None) and \
        ("recovery_Aging_of_Outstanding_OP_Identified_Amt_6_months_to_1_year" not in agencyObj or agencyObj["recovery_Aging_of_Outstanding_OP_Identified_Amt_6_months_to_1_year"] is None) and \
        ("recovery_Aging_of_Outstanding_OP_Identified_Amt_over_1_year" not in agencyObj or agencyObj["recovery_Aging_of_Outstanding_OP_Identified_Amt_over_1_year"] is None) and \
        ("recovery_Aging_of_Outstanding_OP_Identified_determined_not_collectable" not in agencyObj or agencyObj["recovery_Aging_of_Outstanding_OP_Identified_determined_not_collectable"] is None) and \
        ("recovery_Recovery_Audit_Amount_Identified_In_Prior_Reporting_Periods_Determined_Not_Collectable_During_This_Reporting_Period" not in agencyObj or agencyObj["recovery_Recovery_Audit_Amount_Identified_In_Prior_Reporting_Periods_Determined_Not_Collectable_During_This_Reporting_Period"] is None) and \
        ("detail_ara2_2" not in agencyObj or agencyObj["detail_ara2_2"] is None)
    agencyObj["Hide_Do_Not_Pay"] = ("detail_dpa5" not in agencyObj or agencyObj["detail_dpa5"] is None or agencyObj["detail_dpa5"] == '') and \
        ("detail_dpa2" not in agencyObj or agencyObj["detail_dpa2"] is None or agencyObj["detail_dpa2"] == '') and \
        ("detail_dpa3" not in agencyObj or agencyObj["detail_dpa3"] is None or agencyObj["detail_dpa3"] == '')
    agencyObj["Hide_PIIA2019"] = ("detail_com1" not in agencyObj or agencyObj["detail_com1"] is None) and \
        ("PIIA2019_Compliant_Programs" not in agencyObj or agencyObj["PIIA2019_Compliant_Programs"] is None or len(agencyObj["PIIA2019_Compliant_Programs"]) == 0) and \
        ("PIIA2019_NonCompliant_Programs" not in agencyObj or agencyObj["PIIA2019_NonCompliant_Programs"] is None or len(agencyObj["PIIA2019_NonCompliant_Programs"]) == 0) and \
        ("detail_pcp14" not in agencyObj or agencyObj["detail_pcp14"] is None) and \
        ("detail_CAP5" not in agencyObj or agencyObj["detail_CAP5"] is None) and \
        ("detail_cap3" not in agencyObj or agencyObj["detail_cap3"] is None) and \
        ("detail_cap4" not in agencyObj or agencyObj["detail_cap4"] is None)
    agencyObj["Hide_Risk_Assessment_Results"] = \
        ("detail_raa9" not in agencyObj or agencyObj["detail_raa9"] is None or agencyObj["detail_raa9"] == '') and \
        ("detail_raa8" not in agencyObj or agencyObj["detail_raa8"] is None or agencyObj["detail_raa8"] == '') and \
        ("Risks" not in agencyObj or agencyObj["Risks"] is None or len(agencyObj["Risks"]) == 0)
    agencyObj["Hide_Eligibility_Criteria"] = \
        ("Eligibility_Themes" not in agencyObj or agencyObj["Eligibility_Themes"] is None or len(agencyObj["Eligibility_Themes"]) == 0)
    agencyObj["Hide_Supplemental_Payment_Integrity"] = \
        ("detail_agy1" not in agencyObj or agencyObj["detail_agy1"] is None or agencyObj["detail_agy1"] == '')
    agencyObj["Hide_Supplemental_Info"] = agencyObj["Hide_Do_Not_Pay"] and \
        agencyObj["Hide_Disposition_of_Funds"] and agencyObj["Hide_PIIA2019"] and \
        agencyObj["Hide_Risk_Assessment_Results"] and agencyObj["Hide_Eligibility_Criteria"] and \
        agencyObj["Hide_Supplemental_Payment_Integrity"]

def write_agency_md_files(agencyCode, agencyObj, year):
    longpath = os.path.join(AGENCY_SPECIFIC_DIR, agencyCode)
    os.makedirs(longpath, exist_ok=True)
    with open(os.path.join(longpath, str(year) + ".md"), 'w', encoding='utf-8') as file:
        agencyObj["permalink"] = "agency/" + agencyCode + "/" + str(year) + ".html"
        file.write('---\n')
        yaml.dump(agencyObj, file, allow_unicode=True)
        file.write('---\n')

    # Provide current year as default
    if year == config.FISCAL_YEAR:
        with open(os.path.join(AGENCY_SPECIFIC_DIR, agencyCode + ".md"), 'w', encoding='utf-8') as file:
            agencyObj["permalink"] = "agency/" + str(agencyCode) + ".html"
            file.write('---\n')
            yaml.dump(agencyObj, file, allow_unicode=True)
            file.write('---\n')

def generate_agency_specific_pages(cursor):
    if os.path.exists(AGENCY_SPECIFIC_DIR):
        shutil.rmtree(AGENCY_SPECIFIC_DIR)

    for year in AGENCY_SPECIFIC_FISCAL_YEARS:
        generate_agency_specific_pages_for_year(cursor, year)

# this ensures that every agency that has ever had data has a landing page
def generate_placeholder_agency_specific_pages(cursor):
    query = f"""
        SELECT DISTINCT
            [Agency],
            [Agency_Name]
        FROM [all_agencies_years]
    """

    cursor.execute(query)

    agencies = cursor.fetchall()

    for agency in agencies:
        if not os.path.isfile(os.path.join(AGENCY_SPECIFIC_DIR, agency["Agency"] + ".md")):
            with open(os.path.join(AGENCY_SPECIFIC_DIR, agency["Agency"] + ".md"), 'w', encoding='utf-8') as file:
                yearsCriteria = ','.join(['?'] * len(AGENCY_SPECIFIC_FISCAL_YEARS))

                yearsAvailableQuery = f"""
                    SELECT
                        [Fiscal_Year]
                    FROM [all_agencies_years]
                    WHERE [Agency] = ? AND [Fiscal_Year] IN ({yearsCriteria})
                    ORDER BY [Fiscal_Year] DESC
                """

                cursor.execute(yearsAvailableQuery, [agency["Agency"]] + AGENCY_SPECIFIC_FISCAL_YEARS)
                yearsAvailable = cursor.fetchall()

                agencyObj = {
                    "Agency": agency["Agency"],
                    "Agency_Name": agency["Agency_Name"],
                    "Fiscal_Year": config.FISCAL_YEAR,
                    "layout": "agency-specific",
                    "permalink": "agency/" + agency["Agency"] + ".html",
                    "Years_Available": list(map(lambda x: x["Fiscal_Year"], yearsAvailable)),
                    "Is_Placeholder": True
                }

                file.write('---\n')
                yaml.dump(agencyObj, file, allow_unicode=True)
                file.write('---\n')

    print("Successfully generated placeholder agency-specific markup files for FY " + str(config.FISCAL_YEAR))

def generate_program_specific_pages(cursor: sqlite3.Cursor):
    query = f"""
        SELECT DISTINCT
            a.Agency,
            b.Agency_Name,
            a.[Program_Name],
            a.[High_Priority_Program],
            a.[Phase_2_Program],
            a.[Outlays],
            a.[Payment_Accuracy_Rate],
            c.[Description]
        FROM [all_programs_data_aggregation] a
            LEFT JOIN ip_agency_pocs b
                ON a.[Agency] = b.[Agency_Acronym]
            LEFT JOIN (
                SELECT DISTINCT
                    Agency,
                    [Program Name],
                    [Please provide a brief 1-2 sentence high level description of yo] as [Description]
                FROM survey_root_cause
                WHERE [Quarter Year] = ?
                    AND RootCauseNumber = 'Please choose Root Cause 1.'
            ) c
            ON a.[Agency] = c.[Agency]
                AND a.[Program_Name] = c.[Program Name]
    """

    cursor.execute(query, (config.LAST_QUARTERLY_SURVEY,))
    programs = cursor.fetchall()

    if os.path.exists(PROGRAM_SPECIFIC_DIR):
        shutil.rmtree(PROGRAM_SPECIFIC_DIR)

    os.makedirs(PROGRAM_SPECIFIC_DIR, exist_ok=True)
    for program in programs:
        # this object is used to merge program data and raw detail data
        programObj = {
            "Agency": program["Agency"],
            "Agency_Name": program["Agency_Name"],
            "Program_Name": program["Program_Name"],
            "High_Priority_Program": program["High_Priority_Program"],
            "Phase_2_Program": program["Phase_2_Program"],
            "Outlays": program["Outlays"],
            "Payment_Accuracy_Rate": program["Payment_Accuracy_Rate"],
            "Description": program["Description"],
            "layout": "program-specific",
            "fpi_link": "https://fpi.omb.gov/",
            "permalink": "program/" + SLUGIFIED_PROGRAM_NAME_MAPPINGS[program["Program_Name"]] + ".html"
        }

        yearsCriteria = ','.join(['?'] * len(AGENCY_SPECIFIC_FISCAL_YEARS))

        dataPointQuery = f"""
            SELECT
                COALESCE([Outlays],0)
                    - COALESCE([CY_Overpayment_Amount],0)
                    - COALESCE([CY_Underpayment_Amount],0)
                    - COALESCE([CY_Technically_Improper_Amount],0)
                    - COALESCE([CY_Unknown_Payments],0)
                    AS [Payment_Accuracy_Amount],
                COALESCE([CY_Overpayment_Amount],0) AS [Overpayment_Amount],
                COALESCE([CY_Underpayment_Amount],0) AS [Underpayment_Amount],
                COALESCE([CY_Technically_Improper_Amount],0) AS [Technically_Improper_Amount],
                COALESCE([CY_Unknown_Payments],0) AS [Unknown_Amount]
            FROM all_programs_data_aggregation
            WHERE [Program_Name] = ? AND [Fiscal_Year] IN ({yearsCriteria})
            ORDER BY [Fiscal_Year]
        """

        cursor.execute(dataPointQuery, [program["Program_Name"]] + AGENCY_SPECIFIC_FISCAL_YEARS)

        dataPointsDetails = cursor.fetchall()

        programObj["Payment_Accuracy_Amounts"] = str(extract_column_from_results("Payment_Accuracy_Amount", dataPointsDetails))
        programObj["Overpayment_Amounts"] = str(extract_column_from_results("Overpayment_Amount", dataPointsDetails))
        programObj["Underpayment_Amounts"] = str(extract_column_from_results("Underpayment_Amount", dataPointsDetails))
        programObj["Technically_Improper_Amounts"] = str(extract_column_from_results("Technically_Improper_Amount", dataPointsDetails))
        programObj["Unknown_Amounts"] = str(extract_column_from_results("Unknown_Amount", dataPointsDetails))
        
        rates_by_year = {}

        improperPaymentEstimatesQuery = f"""
            SELECT
                [Fiscal_Year],
                [Payment_Accuracy_Rate],
                [IP_Rate],
                [Unknown_Payments_Rate],
                [Start_Date],
                [End_Date],
                [CY_Confidence_Level],
                [CY_Margin_of_Error]
            FROM all_programs_data_aggregation
            WHERE [Program_Name] = ? AND
                (
                    [Payment_Accuracy_Rate] IS NOT NULL OR
                    [IP_Rate] IS NOT NULL OR
                    [Unknown_Payments_Rate] IS NOT NULL
                )
            ORDER BY [Fiscal_Year]
        """

        cursor.execute(improperPaymentEstimatesQuery, (program["Program_Name"],))

        improperPaymentEstimates = cursor.fetchall()
        
        for row in improperPaymentEstimates:
            fiscal_year = row["Fiscal_Year"]
            accuracy_rate = row["Payment_Accuracy_Rate"]
            ip_rate = row["IP_Rate"]
            unknown_rate = row["Unknown_Payments_Rate"]
            start_date = row["Start_Date"]
            end_date = row["End_Date"]
            confidence_level = row["CY_Confidence_Level"]
            margin_of_error = row["CY_Margin_of_Error"]

            # Check if at least one of the rates is not None
            if any(rate is not None for rate in (accuracy_rate, ip_rate, unknown_rate)):
                rates_by_year[fiscal_year] = {
                    "Payment_Accuracy_Rate": accuracy_rate,
                    "Improper_Payments_Rate": ip_rate,
                    "Unknown_Payments_Rate": unknown_rate,
                    "Start_Date": start_date,
                    "End_Date": end_date,
                    "Confidence_Level": confidence_level,
                    "Margin_of_Error": margin_of_error
                }
        
        programObj["Rates_By_Year"] = rates_by_year

        actions_by_year = {}

        actionsQuery = f"""
            SELECT
                [Fiscal_Year],
                [Agency],
                [Program_Name],
                [Column_names] AS [Mitigation_Strategy],
                [Column_values] AS [Description_Action_Taken],
                CASE
                    WHEN Column_names LIKE 'app%\\_1' ESCAPE '\\' AND Column_values NOT LIKE 'The corrective action was not fully completed%' THEN 'Planned'
                    WHEN (Column_names LIKE 'atp%\\_1' ESCAPE '\\' OR Column_names LIKE 'app%\\_1' ESCAPE '\\') AND Column_values LIKE 'The corrective action was not fully completed%' THEN 'Not Completed'
                    ELSE 'Completed'
                END as [Action_Taken]
            FROM principal_table_columns
            WHERE Column_values <> ''
                AND (Column_names LIKE 'atp%\\_1' ESCAPE '\\' OR Column_names LIKE 'app%\\_1' ESCAPE '\\')
                AND Program_Name = ?
        """

        cursor.execute(actionsQuery, (program["Program_Name"],))

        actionsTaken = cursor.fetchall()

        for row in actionsTaken:
            fiscal_year = row["Fiscal_Year"]
            mitigation_strategy = row["Mitigation_Strategy"]
            description_action_taken = row["Description_Action_Taken"]
            action_taken = row["Action_Taken"]

            if fiscal_year not in actions_by_year:
                actions_by_year[fiscal_year] = []

            actions_by_year[fiscal_year].append({
                "Mitigation_Strategy": mitigation_strategy,
                "Description_Action_Taken": description_action_taken,
                "Action_Taken": action_taken
            })

        programObj["Actions_By_Year"] = actions_by_year

        overpayments_by_year = {}

        overpayments_query = f"""
            SELECT DISTINCT
                a.Fiscal_Year,
                a.[Program_Name],
                b.Column_values AS [cyp2_1],
                c.[Inability_to_Authenticate_Eligibility:_Data_Needed_Does_Not_Exis],
                c.[Inability_to_Authenticate_Eligibility:_Inability_to_Access_Data],
                c.[Failure_to_Access_Data],
                c.[Address_Location],
                c.[Contractor_or_Provider_Status],
                c.[Financial],
                d.Column_values AS [cyp2_atp1_8],
                e.Column_values AS [cyp2_app1_8]
            FROM principal_table_columns AS a
            LEFT JOIN (
                SELECT * FROM principal_table_columns
                WHERE Column_names = 'cyp2_1' AND Column_values <> ''
            ) AS b
                ON a.Agency = b.Agency
                AND a.Program_Name = b.Program_Name
                AND a.Fiscal_Year = b.Fiscal_Year
            LEFT JOIN ip_root_causes AS c
                ON a.Agency = c.Agency
                AND a.[Program_Name] = c.[Program_Name]
                AND a.Fiscal_Year = c.Fiscal_Year
                AND c.[Payment_Type] = 'Overpayments within agency control'
            LEFT JOIN principal_table_columns AS d
                ON a.Agency = d.Agency
                AND a.[Program_Name] = d.[Program_Name]
                AND a.Fiscal_Year = d.Fiscal_Year
                AND d.Column_names = 'cyp2_atp1_8'
                AND d.Column_values <> ''
            LEFT JOIN principal_table_columns AS e
                ON a.Agency = e.Agency
                AND a.[Program_Name] = e.[Program_Name]
                AND a.Fiscal_Year = e.Fiscal_Year
                AND e.Column_names = 'cyp2_app1_8'
                AND e.Column_values <> ''
            WHERE a.[Program_Name] = ?
        """

        cursor.execute(overpayments_query, (program["Program_Name"],))

        overpayments = cursor.fetchall()

        for row in overpayments:
            fiscal_year = row["Fiscal_Year"]
            cyp2_1 = row["cyp2_1"]
            data_needed_does_not_exist = row["Inability_to_Authenticate_Eligibility:_Data_Needed_Does_Not_Exis"]
            inability_to_access_data = row["Inability_to_Authenticate_Eligibility:_Inability_to_Access_Data"]
            failure_to_access_data = row["Failure_to_Access_Data"]
            address_location = row["Address_Location"]
            contractor_provider_status = row["Contractor_or_Provider_Status"]
            financial = row["Financial"]
            cyp2_atp1_8 = row["cyp2_atp1_8"]
            cyp2_app1_8 = row["cyp2_app1_8"]

            if fiscal_year not in overpayments_by_year:
                overpayments_by_year[fiscal_year] = {
                    "cyp2_1" : cyp2_1,
                    "Data_Needed_Does_Not_Exist" : data_needed_does_not_exist,
                    "Inability_to_Access_Data" : inability_to_access_data,
                    "Failure_to_Access_Data" : failure_to_access_data,
                    "Address_Location" : address_location,
                    "Contractor_Provider_Status" : contractor_provider_status,
                    "Financial" : financial,
                    "cyp2_atp1_8" : cyp2_atp1_8,
                    "cyp2_app1_8" : cyp2_app1_8
                }

        programObj["Overpayments_By_Year"] = overpayments_by_year

        underpayments_by_year = {}

        underpayments_query = f"""
            SELECT DISTINCT
                a.Fiscal_Year,
                a.[Program_Name],
                c.[Inability_to_Authenticate_Eligibility:_Data_Needed_Does_Not_Exis],
                c.[Inability_to_Authenticate_Eligibility:_Inability_to_Access_Data],
                c.[Failure_to_Access_Data],
                c.[Address_Location],
                c.[Contractor_or_Provider_Status],
                c.[Financial],
                d.Column_values AS [cyp5_atp1_8],
                e.Column_values AS [cyp5_app1_8]
            FROM principal_table_columns AS a
            LEFT JOIN ip_root_causes AS c
                ON a.Agency = c.Agency
                AND a.[Program_Name] = c.[Program_Name]
                AND a.Fiscal_Year = c.Fiscal_Year
                AND c.[Payment_Type] = 'Underpayments'
            LEFT JOIN principal_table_columns AS d
                ON a.Agency = d.Agency
                AND a.[Program_Name] = d.[Program_Name]
                AND a.Fiscal_Year = d.Fiscal_Year
                AND d.Column_names = 'cyp5_atp1_8'
                AND d.Column_values <> ''
            LEFT JOIN principal_table_columns AS e
                ON a.Agency = e.Agency
                AND a.[Program_Name] = e.[Program_Name]
                AND a.Fiscal_Year = e.Fiscal_Year
                AND e.Column_names = 'cyp5_app1_8'
                AND e.Column_values <> ''
            WHERE a.[Program_Name] = ?
        """

        cursor.execute(underpayments_query, (program["Program_Name"],))

        underpayments = cursor.fetchall()

        for row in underpayments:
            fiscal_year = row["Fiscal_Year"]
            data_needed_does_not_exist = row["Inability_to_Authenticate_Eligibility:_Data_Needed_Does_Not_Exis"]
            inability_to_access_data = row["Inability_to_Authenticate_Eligibility:_Inability_to_Access_Data"]
            failure_to_access_data = row["Failure_to_Access_Data"]
            address_location = row["Address_Location"]
            contractor_provider_status = row["Contractor_or_Provider_Status"]
            financial = row["Financial"]
            cyp5_atp1_8 = row["cyp5_atp1_8"]
            cyp5_app1_8 = row["cyp5_app1_8"]

            if fiscal_year not in underpayments_by_year:
                underpayments_by_year[fiscal_year] = {
                    "Data_Needed_Does_Not_Exist" : data_needed_does_not_exist,
                    "Inability_to_Access_Data" : inability_to_access_data,
                    "Failure_to_Access_Data" : failure_to_access_data,
                    "Address_Location" : address_location,
                    "Contractor_Provider_Status" : contractor_provider_status,
                    "Financial": financial,
                    "cyp5_atp1_8" : cyp5_atp1_8,
                    "cyp5_app1_8" : cyp5_app1_8
                }

        programObj["Underpayments_By_Year"] = underpayments_by_year

        technically_ip_by_year = {}

        technically_ip_query = f"""
            SELECT DISTINCT
                a.Fiscal_Year,
                a.[Program_Name],
                b.Column_values AS [cyp6_1],
                c.[Program_Design_or_Structural_Issue],
                d.Column_values AS [cyp7_atp1_8],
                e.Column_values AS [cyp7_app1_8]
            FROM principal_table_columns AS a
            LEFT JOIN (
                SELECT * FROM principal_table_columns
                WHERE Column_names = 'cyp6_1' AND Column_values <> ''
            ) AS b
                ON a.Agency = b.Agency
                AND a.Program_Name = b.Program_Name
                AND a.Fiscal_Year = b.Fiscal_Year
            LEFT JOIN ip_root_causes AS c
                ON a.Agency = c.Agency
                AND a.[Program_Name] = c.[Program_Name]
                AND a.Fiscal_Year = c.Fiscal_Year
                AND c.[Payment_Type] = 'Technically Improper'
            LEFT JOIN principal_table_columns AS d
                ON a.Agency = d.Agency
                AND a.[Program_Name] = d.[Program_Name]
                AND a.Fiscal_Year = d.Fiscal_Year
                AND d.Column_names = 'cyp7_atp1_8'
                AND d.Column_values <> ''
            LEFT JOIN principal_table_columns AS e
                ON a.Agency = e.Agency
                AND a.[Program_Name] = e.[Program_Name]
                AND a.Fiscal_Year = e.Fiscal_Year
                AND e.Column_names = 'cyp7_app1_8'
                AND e.Column_values <> ''
            WHERE a.[Program_Name] = ?
        """

        cursor.execute(technically_ip_query, (program["Program_Name"],))

        technically_ip = cursor.fetchall()

        for row in technically_ip:
            fiscal_year = row["Fiscal_Year"]
            cyp6_1 = row["cyp6_1"]
            program_design_or_structural_issue = row["Program_Design_or_Structural_Issue"]
            cyp7_atp1_8 = row["cyp7_atp1_8"]
            cyp7_app1_8 = row["cyp7_app1_8"]

            if fiscal_year not in technically_ip_by_year:
                technically_ip_by_year[fiscal_year] = {
                    "cyp6_1" : cyp6_1,
                    "Program_Design_or_Structural_Issue" : program_design_or_structural_issue,
                    "cyp7_atp1_8" : cyp7_atp1_8,
                    "cyp7_app1_8" : cyp7_app1_8
                }

        programObj["Technically_IP_By_Year"] = technically_ip_by_year

        unknown_payments_by_year = {}

        unknown_payments_query = f"""
            SELECT DISTINCT
                a.Fiscal_Year,
                a.[Program_Name],
                b.Column_values AS [cyp8],
                c.[Insufficient_Documentation_to_Determine],
                d.Column_values AS [cyp7_ucp4_1],
                e.Column_values AS [cyp7_atp1_8],
                f.Column_values AS [cyp7_app1_8]
            FROM principal_table_columns AS a
            LEFT JOIN (
                SELECT * FROM principal_table_columns
                WHERE Column_names = 'cyp8' AND Column_values <> ''
            ) AS b
                ON a.Agency = b.Agency
                AND a.Program_Name = b.Program_Name
                AND a.Fiscal_Year = b.Fiscal_Year
            LEFT JOIN ip_root_causes AS c
                ON a.Agency = c.Agency
                AND a.[Program_Name] = c.[Program_Name]
                AND a.Fiscal_Year = c.Fiscal_Year
                AND c.[Payment_Type] = 'Unknown'
            LEFT JOIN principal_table_columns AS d
                ON a.Agency = d.Agency
                AND a.[Program_Name] = d.[Program_Name]
                AND a.Fiscal_Year = d.Fiscal_Year
                AND d.Column_names = 'cyp7_ucp4_1'
                AND d.Column_values <> ''
            LEFT JOIN principal_table_columns AS e
                ON a.Agency = e.Agency
                AND a.[Program_Name] = e.[Program_Name]
                AND a.Fiscal_Year = e.Fiscal_Year
                AND e.Column_names = 'cyp7_atp1_8'
                AND e.Column_values <> ''
            LEFT JOIN principal_table_columns AS f
                ON a.Agency = f.Agency
                AND a.[Program_Name] = f.[Program_Name]
                AND a.Fiscal_Year = f.Fiscal_Year
                AND f.Column_names = 'cyp7_app1_8'
                AND f.Column_values <> ''
            WHERE a.[Program_Name] = ?
        """

        cursor.execute(unknown_payments_query, (program["Program_Name"],))

        unknown_payments = cursor.fetchall()

        for row in unknown_payments:
            fiscal_year = row["Fiscal_Year"]
            cyp8 = row["cyp8"]
            insufficient_documentation_to_determine = row["Insufficient_Documentation_to_Determine"]
            cyp7_ucp4_1 = row["cyp7_ucp4_1"]
            cyp7_atp1_8 = row["cyp7_atp1_8"]
            cyp7_app1_8 = row["cyp7_app1_8"]

            if fiscal_year not in unknown_payments_by_year:
                unknown_payments_by_year[fiscal_year] = {
                    "cyp8" : cyp8,
                    "Insufficient_Documentation_to_Determine" : insufficient_documentation_to_determine,
                    "cyp7_ucp4_1" : cyp7_ucp4_1,
                    "cyp7_atp1_8" : cyp7_atp1_8,
                    "cyp7_app1_8" : cyp7_app1_8
                }

        programObj["Unknown_Payments_By_Year"] = unknown_payments_by_year

        corrective_actions_by_year = {}

        corrective_actions_query = f"""
            SELECT DISTINCT
                a.Fiscal_Year,
                a.[Program_Name],
                b.Column_values AS [rnp3],
                d.Column_values AS [act17_2],
                e.Column_values AS [act17_1],
                f.Column_values AS [act17_3]
            FROM principal_table_columns AS a
            LEFT JOIN (
                SELECT * FROM principal_table_columns
                WHERE Column_names = 'rnp3' AND Column_values <> ''
            ) AS b
                ON a.Agency = b.Agency
                AND a.Program_Name = b.Program_Name
                AND a.Fiscal_Year = b.Fiscal_Year
            LEFT JOIN principal_table_columns AS d
                ON a.Agency = d.Agency
                AND a.[Program_Name] = d.[Program_Name]
                AND a.Fiscal_Year = d.Fiscal_Year
                AND d.Column_names = 'act17_2'
                AND d.Column_values <> ''
            LEFT JOIN principal_table_columns AS e
                ON a.Agency = e.Agency
                AND a.[Program_Name] = e.[Program_Name]
                AND a.Fiscal_Year = e.Fiscal_Year
                AND e.Column_names = 'act17_1'
                AND e.Column_values <> ''
            LEFT JOIN principal_table_columns AS f
                ON a.Agency = f.Agency
                AND a.[Program_Name] = f.[Program_Name]
                AND a.Fiscal_Year = f.Fiscal_Year
                AND f.Column_names = 'act17_3'
                AND f.Column_values <> ''
            WHERE a.[Program_Name] = ?
        """

        cursor.execute(corrective_actions_query, (program["Program_Name"],))

        corrective_actions = cursor.fetchall()

        for row in corrective_actions:
            fiscal_year = row["Fiscal_Year"]
            rnp3 = row["rnp3"]
            act17_2 = row["act17_2"]
            act17_1 = row["act17_1"]
            act17_3 = row["act17_3"]

            if fiscal_year not in corrective_actions_by_year:
                corrective_actions_by_year[fiscal_year] = {
                    "rnp3" : rnp3,
                    "act17_2" : act17_2,
                    "act17_1" : act17_1,
                    "act17_3" : act17_3
                }

        programObj["Corrective_Actions_By_Year"] = corrective_actions_by_year

        future_outlook_by_year = {}

        future_outlook_query = f"""
            SELECT DISTINCT
                a.Fiscal_Year,
                a.[Program_Name],
                b.Column_values AS [cyp15],
                d.Column_values AS [cyp20_2],
                e.Column_values AS [rtp4_2],
                f.Column_values AS [rap5],
                g.Column_values AS [rap6],
                c.[Outlays_Current_Year+1_Amount],
                c.[IP_Current_Year+1_Amount],
                c.[Unknown_Curent_Year+1_Amount],
                c.[IP_Unknown_Current_Year+1_Rate],
                c.[IP_Unknown_Target_Rate]
            FROM principal_table_columns AS a
            LEFT JOIN (
                SELECT * FROM principal_table_columns
                WHERE Column_names = 'cyp15' AND Column_values <> ''
            ) AS b
                ON a.Agency = b.Agency
                AND a.Program_Name = b.Program_Name
                AND a.Fiscal_Year = b.Fiscal_Year
            LEFT JOIN all_programs_data_aggregation c
                ON a.Agency = c.Agency
                AND a.Program_Name = c.Program_Name
                AND a.Fiscal_Year = c.Fiscal_Year
            LEFT JOIN principal_table_columns AS d
                ON a.Agency = d.Agency
                AND a.[Program_Name] = d.[Program_Name]
                AND a.Fiscal_Year = d.Fiscal_Year
                AND d.Column_names = 'cyp20_2'
                AND d.Column_values <> ''
            LEFT JOIN principal_table_columns AS e
                ON a.Agency = e.Agency
                AND a.[Program_Name] = e.[Program_Name]
                AND a.Fiscal_Year = e.Fiscal_Year
                AND e.Column_names = 'rtp4_2'
                AND e.Column_values <> ''
            LEFT JOIN principal_table_columns AS f
                ON a.Agency = f.Agency
                AND a.[Program_Name] = f.[Program_Name]
                AND a.Fiscal_Year = f.Fiscal_Year
                AND f.Column_names = 'rap5'
                AND f.Column_values <> ''
            LEFT JOIN principal_table_columns AS g
                ON a.Agency = g.Agency
                AND a.[Program_Name] = g.[Program_Name]
                AND a.Fiscal_Year = g.Fiscal_Year
                AND g.Column_names = 'rap6'
                AND g.Column_values <> ''
            WHERE a.[Program_Name] = ?
        """

        cursor.execute(future_outlook_query, (program["Program_Name"],))

        future_outlook = cursor.fetchall()

        for row in future_outlook:
            fiscal_year = row["Fiscal_Year"]
            cyp15 = row["cyp15"]
            cyp20_2 = row["cyp20_2"]
            rtp4_2 = row["rtp4_2"]
            rap5 = row["rap5"]
            rap6 = row["rap6"]
            outlays_current_year_plus_1_amount = row["Outlays_Current_Year+1_Amount"]
            ip_current_year_plus_1_amount = row["IP_Current_Year+1_Amount"]
            unknown_curent_year_plus_1_amount = row["Unknown_Curent_Year+1_Amount"]
            ip_unknown_current_year_plus_1_rate = row["IP_Unknown_Current_Year+1_Rate"]
            ip_unknown_target_rate = row["IP_Unknown_Target_Rate"]

            if fiscal_year not in future_outlook_by_year:
                future_outlook_by_year[fiscal_year] = {
                    "cyp15" : cyp15,
                    "cyp20_2" : cyp20_2,
                    "rtp4_2" : rtp4_2,
                    "rap5" : rap5,
                    "rap6" : rap6,
                    "Outlays_Current_Year_Plus_1_Amount" : outlays_current_year_plus_1_amount,
                    "IP_Current_Year_Plus_1_Amount" : ip_current_year_plus_1_amount,
                    "Unknown_Curent_Year_Plus_1_Amount" : unknown_curent_year_plus_1_amount,
                    "IP_Unknown_Current_Year_Plus_1_Rate" : ip_unknown_current_year_plus_1_rate,
                    "IP_Unknown_Target_Rate" : ip_unknown_target_rate
                }

        programObj["Future_Outlook_By_Year"] = future_outlook_by_year

        additional_information_by_year = {}

        additional_information_query = f"""
            SELECT DISTINCT
                a.Fiscal_Year,
                a.[Program_Name],
                b.Column_values AS [pro1],
                d.Column_values AS [rnp4]
            FROM principal_table_columns AS a
            LEFT JOIN (
                SELECT * FROM principal_table_columns
                WHERE Column_names = 'pro1' AND Column_values <> ''
            ) AS b
                ON a.Agency = b.Agency
                AND a.Program_Name = b.Program_Name
                AND a.Fiscal_Year = b.Fiscal_Year
            LEFT JOIN principal_table_columns AS d
                ON a.Agency = d.Agency
                AND a.[Program_Name] = d.[Program_Name]
                AND a.Fiscal_Year = d.Fiscal_Year
                AND d.Column_names = 'rnp4'
                AND d.Column_values <> ''
            WHERE a.[Program_Name] = ?
        """

        cursor.execute(additional_information_query, (program["Program_Name"],))

        additional_information = cursor.fetchall()

        for row in additional_information:
            fiscal_year = row["Fiscal_Year"]
            pro1 = row["pro1"]
            rnp4 = row["rnp4"]

            if fiscal_year not in additional_information_by_year:
                additional_information_by_year[fiscal_year] = {
                    "pro1" : pro1,
                    "rnp4" : rnp4
                }

        programObj["Additional_Information_By_Year"] = additional_information_by_year

        with open(os.path.join(PROGRAM_SPECIFIC_DIR, SLUGIFIED_PROGRAM_NAME_MAPPINGS[program["Program_Name"]] + ".md"), 'w', encoding='utf-8') as file:
            file.write('---\n')
            yaml.dump(programObj, file, allow_unicode=True)
            file.write('---\n')
    print("Successfully generated program-specific markup files")

# Temporary for UAT - can be removed later
def generate_placeholder_program_specific_pages(cursor):
    with open(os.path.join(PROGRAM_SPECIFIC_DIR, "EXAMPLE.md"), 'w', encoding='utf-8') as file:
        file.write('---\n')
        yaml.dump({
            'layout': 'programs',
            'permalink': '/programs/EXAMPLE',
            'title': 'Programs'
        }, file, allow_unicode=True)
        file.write('---\n')

    print("Successfully generated placeholder program-specific markup file")

def main():
    try:
        conn = sqlite3.connect(DB_FULL_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        slugifyProgramNames(cursor)
        generate_home_page(cursor)
        generate_agency_programs_page(cursor)
        generate_agency_specific_pages(cursor)
        generate_placeholder_agency_specific_pages(cursor)
        generate_program_specific_pages(cursor)
        generate_placeholder_program_specific_pages(cursor)

    except sqlite3.Error as e:
        print(f"Database error occurred: {e}")
        raise e
    except Exception as e:
        print(f"An error occurred: {e}")
        raise e
    finally:
        if 'conn' in locals():
            conn.close()
if __name__ == "__main__":
    main()