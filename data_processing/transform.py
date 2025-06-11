"""
Transform extracted program information and store the transformed
information in a SQLite database for generation of mardown files.
"""

import os
import pandas as pd
import sqlite3
from io import StringIO

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# transformed database, for use in the load / generate stage
TRANSFORMED_FILES_DIRECTORY = "transformed"
TRANSFORMED_DB_FILE_NAME = "transformed_data.db"
TRANSFORMED_DB_FILE_PATH = os.path.join(BASE_DIR, TRANSFORMED_FILES_DIRECTORY, TRANSFORMED_DB_FILE_NAME)

# extracted file paths
EXTRACTED_FILES_DIRECTORY = "extracted"
EXTRACTED_ALL_PROGRAMS_CSV_NAME = "MY_OMB_ImproperPayment_Payment_Accuracy_All_Program_vw.csv"
EXTRACTED_PROGRAM_DATA_RAW_CSV_NAME = "MY_OMB_ImproperPayment_PaymentAccuracy_ProgramData_raw_vw.csv"
EXTRACTED_AGENCY_DATA_RAW_CSV_NAME = "MY_OMB_ImproperPayment_PaymentAccuracy_AgencyData_raw_vw.csv"
EXTRACTED_IP_AGENCY_POCS_CSV_NAME = "IP_Agency_POCs.csv"
EXTRACTED_PRINCIPAL_TABLE_COLUMNS_CSV_NAME = "MY_OMB_ImproperPayment_Payment_Accuracy_Principal_Table_Columns_vw.csv"
EXTRACTED_PAYMENT_RECOVERY_DETAILS_CSV_NAME = "MY_OMB_ImproperPayment_Payment_Recovery_Details_unpivotted_vw.csv"
EXTRACTED_PAYMENT_CONFIRMED_FRAUD_CSV_NAME = "MY_OMB_ImproperPayment_Payment_Confirmed_Fraud_vw.csv"
EXTRACTED_PROGRAM_COMPLIANCE_CSV_NAME = "MY_OMB_ImproperPayment_Payment_Program_Compliance_vw.csv"
EXTRACTED_RISKS_CSV_NAME = "MY_OMB_ImproperPayment_Payment_Risk_Assessments_vw.csv"
EXTRACTED_NEW_RISKS_CSV_NAME = "MY_OMB_ImproperPayment_Payment_New_Risk_Assessments_vw.csv"
ELIGIBILITY_THEMES_CSV_NAME = "Eligibility_Themes.csv"
EXTRACTED_RECOVERY_AMOUNTS_CSV_NAME = "MY_OMB_ImproperPayment_Payment_Accuracy_Rate_and_Amt_of_Recovery_vw.csv"
EXTRACTED_SURVEY_ROOT_CAUSE = "KPI_ImproperPaymentSurveyRootCause_vw_IP.csv"
EXTRACTED_IP_ROOT_CAUSES = "MY_OMB_ImproperPayment_Payment_IP_Root_Causes_vw.csv"

ALL_PROGRAMS_DATA_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_ALL_PROGRAMS_CSV_NAME)
PROGRAM_DATA_RAW_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_PROGRAM_DATA_RAW_CSV_NAME)
AGENCY_DATA_RAW_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_AGENCY_DATA_RAW_CSV_NAME)
IP_AGENCY_POCS_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_IP_AGENCY_POCS_CSV_NAME)
PRINCIPAL_TABLE_COLUMNS_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_PRINCIPAL_TABLE_COLUMNS_CSV_NAME)
PAYMENT_RECOVERY_DETAILS_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_PAYMENT_RECOVERY_DETAILS_CSV_NAME)
PAYMENT_CONFIRMED_FRAUD_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_PAYMENT_CONFIRMED_FRAUD_CSV_NAME)
PROGRAM_COMPLIANCE_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_PROGRAM_COMPLIANCE_CSV_NAME)
RISKS_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_RISKS_CSV_NAME)
NEW_RISKS_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_NEW_RISKS_CSV_NAME)
ELIGIBILITY_THEMES_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, ELIGIBILITY_THEMES_CSV_NAME)
RECOVERY_AMOUNTS_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_RECOVERY_AMOUNTS_CSV_NAME)
SURVEY_ROOT_CAUSE_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_SURVEY_ROOT_CAUSE)
IP_ROOT_CAUSES_PATH = os.path.join(BASE_DIR, EXTRACTED_FILES_DIRECTORY, EXTRACTED_IP_ROOT_CAUSES)

ALL_PROGRAMS_DATA_AGGREGATION_DROP_TABLE_SQL = """
    DROP TABLE IF EXISTS all_programs_data_aggregation;
    """

ALL_PROGRAMS_DATA_AGGREGATION_CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS all_programs_data_aggregation (
        Agency VARCHAR(20),
        Fiscal_Year INT,
        Program_Name VARCHAR(100),
        Start_Date TEXT,
        End_Date TEXT,
        CY_Confidence_Level TEXT,
        CY_Margin_of_Error TEXT,
        Outlays DECIMAL(15,5),
        IP_Amount DECIMAL(15,5),
        CY_Overpayment_Amount DECIMAL(15,5),
        CY_Underpayment_Amount DECIMAL(15,5),
        CY_Technically_Improper_Amount DECIMAL(15,5),
        CY_Unknown_Payments DECIMAL(15,5),
        IP_Rate DECIMAL(15,5),
        Unknown_Payments_Rate DECIMAL(15,5),
        Payment_Accuracy_Rate DECIMAL(15,5),
        Susceptible_Program INT,
        High_Priority_Program INT,
        Confirmed_Fraud INT,
        Phase_2_Program INT,
        [Outlays_Current_Year+1_Amount] DECIMAL(15,5),
        [IP_Current_Year+1_Amount] DECIMAL(15,5),
        [Unknown_Curent_Year+1_Amount] DECIMAL(15,5),
        [IP_Unknown_Current_Year+1_Rate] DECIMAL(15,5),
        [IP_Unknown_Target_Rate] DECIMAL(15,5)
    );
    """

ALL_PROGRAMS_DATA_AGGREGATION_SELECT_AND_INSERT_SQL = """
    INSERT INTO all_programs_data_aggregation (
        Agency,
        Fiscal_Year,
        Program_Name,
        Start_Date,
        End_Date,
        CY_Confidence_Level,
        CY_Margin_of_Error,
        Outlays,
        IP_Amount,
        CY_Overpayment_Amount,
        CY_Underpayment_Amount,
        CY_Technically_Improper_Amount,
        CY_Unknown_Payments,
        IP_Rate,
        Unknown_Payments_Rate,
        Payment_Accuracy_Rate,
        Susceptible_Program,
        High_Priority_Program,
        Confirmed_Fraud,
        Phase_2_Program,
        [Outlays_Current_Year+1_Amount],
        [IP_Current_Year+1_Amount],
        [Unknown_Curent_Year+1_Amount],
        [IP_Unknown_Current_Year+1_Rate],
        [IP_Unknown_Target_Rate]
    )
    SELECT
        a.Agency,
        a.Fiscal_Year,
        a.Program_Name,
        a.[Month_and_Year_start__date_for_data] AS [Start_Date],
        a.[Month_and_Year_end__date_for_data] AS [End_Date],
        a.[CY_Confidence_Level_%] AS [CY_Confidence_Level],
        a.[CY_Margin__of_Error_+/-] AS [CY_Margin_of_Error],
        CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5)) AS Outlays,
        CAST(COALESCE(a.[IP_Amount_($M)], '0') AS DECIMAL(15,5)) AS IP_Amount,
        CAST(COALESCE(a.[CY_Over-payment_$], '0') AS DECIMAL(15,5)) AS CY_Overpayment_Amount,
        CAST(COALESCE(a.[CY_Under-payment_$], '0') AS DECIMAL(15,5)) AS CY_Underpayment_Amount,
        CAST(COALESCE(a.[CY_Technically_Improper__due_to_Statute_or_Reg_$], '0') AS DECIMAL(15,5)) AS CY_Technically_Improper_Amount,
        CAST(COALESCE(a.[CY_Unknown_Payments_$], '0') AS DECIMAL(15,5)) AS CY_Unknown_Payments,
        100 * CAST(COALESCE(a.[IP_Rate], '0') AS DECIMAL(15,5)) AS IP_Rate,
        100 * CAST(COALESCE(a.[CY_Unknown_Payments_$], '0') AS DECIMAL(15,5)) / CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5)) AS Unknown_Payments_Rate,
        100 - (100 * CAST(COALESCE(a.[IP_Amount_($M)], '0') AS DECIMAL(15,5)) / CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5)))
            - (100 * CAST(COALESCE(a.[CY_Unknown_Payments_$], '0') AS DECIMAL(15,5)) / CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5))) as Payment_Accuracy_Rate,
        CASE
            WHEN b.[Program_Name] IS NOT NULL THEN CAST(1 as BIT)
            ELSE CAST(0 AS BIT)
        END AS [Susceptible_Program],
        CASE
            WHEN c.[Program Name] IS NOT NULL THEN CAST(1 as BIT)
            ELSE CAST(0 AS BIT)
        END AS [High_Priority_Program],
        d.[Confirmed_Fraud],
        CASE
            WHEN e.[Program_Name] IS NOT NULL THEN CAST(1 as BIT)
            ELSE CAST(0 AS BIT)
        END AS [Phase_2_Program],
        a.[Outlays_Current_Year+1_Amount],
        a.[IP_Current_Year+1_Amount],
        a.[Unknown_Curent_Year+1_Amount],
        a.[IP_Unknown_Current_Year+1_Rate],
        a.[IP_Unknown_Target_Rate]
    FROM all_programs_data a
        LEFT JOIN (
            SELECT
                Fiscal_Year,
                Agency,
                Program_Name
            FROM principal_table_columns
            WHERE Column_names = 'app3_1'
                AND Reporting_Phases_Current_FY = 'Phase 2'
        ) b
        ON a.[Agency] = b.[Agency]
            AND a.[Program_Name] = b.[Program_Name]
            AND a.[Fiscal_Year] = b.[Fiscal_Year]
        LEFT JOIN (
            SELECT
                Fiscal_Year,
                agency,
                [Program Name]
            FROM program_data_raw
            WHERE [key] = 'cyp19' AND LOWER([value]) = 'yes'
        ) c
        ON a.[Agency] = c.[agency]
            AND a.[Program_Name] = c.[Program Name]
            AND a.[Fiscal_Year] = c.[Fiscal_Year]
        LEFT JOIN (
            SELECT * FROM payment_confirmed_fraud
        ) d ON a.[Agency] = d.[Agency] AND a.[Fiscal_Year] = d.[Fiscal_Year] AND upper(a.[Program_Name]) = upper(d.[Program_or_Activity])
        LEFT JOIN (
            SELECT
                Fiscal_Year,
                Agency,
                Program_Name
            FROM principal_table_columns
            WHERE Column_names = 'app3_1' AND Reporting_Phases_Current_FY = 'Phase 2'
        ) e
        ON a.[Agency] = e.[Agency]
            AND a.[Program_Name] = e.[Program_Name]
            AND a.[Fiscal_Year] = e.[Fiscal_Year]
    WHERE CAST(COALESCE([Outlays_($M)], '0') AS DECIMAL(15,5)) != 0

    """

ALL_AGENCIES_DATA_AGGREGATION_DROP_TABLE_SQL = """
    DROP TABLE IF EXISTS all_agencies_data_aggregation;
"""

ALL_AGENCIES_DATA_AGGREGATION_CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS all_agencies_data_aggregation (
        Agency VAR(20),
        Agency_Name VAR(50),
        Fiscal_Year INT,
        High_Priority_Programs INT,
        CY_Overpayment_Amount DECIMAL(15,5),
        CY_Underpayment_Amount DECIMAL(15,5),
        CY_Technically_Improper_Amount DECIMAL(15,5),
        IP_Amount DECIMAL(15,5),
        CY_Unknown_Payments DECIMAL(15,5),
        Outlays DECIMAL(15,5),
        Improper_Payments_Rate DECIMAL(15,5),
        Unknown_Payments_Rate DECIMAL(15,5),
        Payment_Accuracy_Rate DECIMAL(15,5),
        Num_Programs INT,
        Susceptible_Programs INT,
        Confirmed_Fraud INT
    );
"""

ALL_AGENCIES_DATA_AGGREGATION_SELECT_AND_INSERT_TABLE_SQL = """
    INSERT INTO all_agencies_data_aggregation (
        Agency,
        Agency_Name,
        Fiscal_Year,
        High_Priority_Programs,
        CY_Overpayment_Amount,
        CY_Underpayment_Amount,
        CY_Technically_Improper_Amount,
        IP_Amount,
        CY_Unknown_Payments,
        Outlays,
        Improper_Payments_Rate,
        Unknown_Payments_Rate,
        Payment_Accuracy_Rate,
        Num_Programs,
        Susceptible_Programs,
        Confirmed_Fraud
    )
    SELECT
        a.Agency,
        c.Agency_Name,
        a.Fiscal_Year,
        IFNULL(b.High_Priority_Programs, 0) AS High_Priority_Programs,
        SUM(CAST(COALESCE(a.[CY_Over-payment_$], '0') AS DECIMAL(15,5))) AS CY_Overpayment_Amount,
        SUM(CAST(COALESCE(a.[CY_Under-payment_$], '0') AS DECIMAL(15,5))) AS CY_Underpayment_Amount,
        SUM(CAST(COALESCE(a.[CY_Technically_Improper__due_to_Statute_or_Reg_$], '0') AS DECIMAL(15,5))) AS CY_Technically_Improper_Amount,
        SUM(CAST(COALESCE(a.[IP_Amount_($M)], '0') AS DECIMAL(15,5))) AS IP_Amount,
        SUM(CAST(COALESCE(a.[CY_Unknown_Payments_$], '0') AS DECIMAL(15,5))) AS CY_Unknown_Payments,
        SUM(CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5))) AS Outlays,
        100 * SUM(CAST(COALESCE(a.[IP_Amount_($M)], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5))) AS Improper_Payments_Rate,
        100 * SUM(CAST(COALESCE(a.[CY_Unknown_Payments_$], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5))) AS Unknown_Payments_Rate,
        100 - (100 * SUM(CAST(COALESCE(a.[IP_Amount_($M)], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5))))
            - (100 * SUM(CAST(COALESCE(a.[CY_Unknown_Payments_$], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE(a.[Outlays_($M)], '0') AS DECIMAL(15,5)))) AS Payment_Accuracy_Rate,
        f.Num_Programs,
        b.Susceptible_Programs,
        d.Confirmed_Fraud
    FROM all_programs_data a
    LEFT JOIN (
        SELECT
            Agency,
            Fiscal_Year,
            SUM(High_Priority_Program) AS High_Priority_Programs,
            SUM(Susceptible_Program) AS Susceptible_Programs
        FROM all_programs_data_aggregation
        GROUP BY Agency, Fiscal_Year
    ) b ON a.Agency = b.Agency AND a.Fiscal_Year = b.Fiscal_Year
    LEFT JOIN (
        SELECT * FROM ip_agency_pocs
    ) c ON a.Agency = c.Agency_Acronym
    LEFT JOIN (
        SELECT * FROM payment_confirmed_fraud
    ) d ON a.[Agency] = d.[Agency] AND a.[Fiscal_Year] = d.[Fiscal_Year] AND (d.[Program_or_Activity] IS NULL OR d.[Program_or_Activity] = '')
    LEFT JOIN (
        SELECT [Agency], [Fiscal_Year], COUNT(*) AS CT FROM [program_compliance] WHERE upper([pcp01_1]) = 'NO' GROUP BY [Agency], [Fiscal_Year]
    ) e ON a.[Agency] = e.[Agency] AND a.[Fiscal_Year] = e.[Fiscal_Year]
    LEFT JOIN (
        SELECT
            [Agency],
            [Fiscal_Year],
            COUNT(*) AS [Num_Programs]
        FROM [program_compliance]
        GROUP BY [Agency], [Fiscal_Year]
    ) f ON a.Agency = f.Agency AND a.Fiscal_Year = f.Fiscal_Year
    WHERE a.[Outlays_($M)] IS NOT NULL
    GROUP BY a.Agency, c.Agency_Name, a.Fiscal_Year, b.High_Priority_Programs
"""

GOVERNMENT_WIDE_DATA_AGGREGATION_DROP_VIEW_SQL = """
    DROP VIEW IF EXISTS government_wide_data_aggregation;
    """

GOVERNMENT_WIDE_DATA_AGGREGATION_CREATE_VIEW_SQL = """
    CREATE VIEW government_wide_data_aggregation AS
    SELECT
        Fiscal_Year,
        SUM(CAST(COALESCE([IP_Amount_($M)], '0') AS DECIMAL(15,5))) AS IP_Amount,
        SUM(CAST(COALESCE([CY_Unknown_Payments_$], '0') AS DECIMAL(15,5))) AS CY_Unknown_Payments,
        SUM(CAST(COALESCE([Outlays_($M)], '0') AS DECIMAL(15,5))) AS Outlays,
        100 * SUM(CAST(COALESCE([IP_Amount_($M)], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE([Outlays_($M)], '0') AS DECIMAL(15,5))) AS Improper_Payments_Rate,
        100 * SUM(CAST(COALESCE([CY_Unknown_Payments_$], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE([Outlays_($M)], '0') AS DECIMAL(15,5))) AS Unknown_Payments_Rate,
        100 - (100 * SUM(CAST(COALESCE([IP_Amount_($M)], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE([Outlays_($M)], '0') AS DECIMAL(15,5))))
            - (100 * SUM(CAST(COALESCE([CY_Unknown_Payments_$], '0') AS DECIMAL(15,5))) / SUM(CAST(COALESCE([Outlays_($M)], '0') AS DECIMAL(15,5)))) AS Payment_Accuracy_Rate
    FROM all_programs_data
    GROUP BY Fiscal_Year;
    """

ALL_AGENCIES_YEARS_DROP_VIEW_SQL = """
    DROP VIEW IF EXISTS all_agencies_years;
    """

ALL_AGENCIES_YEARS_CREATE_VIEW_SQL = """
    CREATE VIEW all_agencies_years AS
    SELECT
        a.[Agency],
        a.[Fiscal_Year],
        COALESCE(b.[Agency_Name],a.[Agency]) AS [Agency_Name]
    FROM (SELECT [Agency],[Fiscal_Year] FROM all_programs_data
    UNION
    SELECT [agency],[Fiscal_Year] FROM agency_data_raw
    UNION
    SELECT [agency],[Fiscal_Year] FROM program_data_raw
    UNION
    SELECT [Agency],[Fiscal_Year] FROM principal_table_columns
    UNION
    SELECT [Agency],[Fiscal_Year] FROM all_programs_data
    UNION
    SELECT [Agency],[Fiscal_Year] FROM payment_recovery_details
    UNION
    SELECT [Agency],[Fiscal_Year] FROM payment_confirmed_fraud
    UNION
    SELECT [Agency],[Fiscal_Year] FROM program_compliance
    UNION
    SELECT [Agency],[Fiscal_Year] FROM recovery_amounts) a
    LEFT JOIN [ip_agency_pocs] b
    ON a.[Agency] = b.[Agency_Acronym];
    """

# establish a database connection to store transformed data that is used
# in the load / generate stage
conn = sqlite3.connect(TRANSFORMED_DB_FILE_PATH)
cur = conn.cursor()

def load_csv_to_sqlite(path: str, table_name: str, conn: sqlite3.Connection):
    """
    Loads a CSV file into a specified SQLite table.
    """
    if not os.path.exists(path):
        print(f"{path} - Not Found")
        return
    
    with open(path, encoding="utf-8-sig") as f:
        csv_data = f.read()
    
    df = pd.read_csv(StringIO(csv_data))
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()
    print(f"Successfully loaded data into '{table_name}'")

def load_all_programs_file(conn):
    load_csv_to_sqlite(ALL_PROGRAMS_DATA_PATH, "all_programs_data", conn)

def load_program_data_raw_file(conn):
    load_csv_to_sqlite(PROGRAM_DATA_RAW_PATH, "program_data_raw", conn)

def load_agency_data_raw_file(conn):
    load_csv_to_sqlite(AGENCY_DATA_RAW_PATH, "agency_data_raw", conn)

def load_ip_agency_pocs_file(conn):
    load_csv_to_sqlite(IP_AGENCY_POCS_PATH, "ip_agency_pocs", conn)

def load_principal_table_columns_file(conn):
    load_csv_to_sqlite(PRINCIPAL_TABLE_COLUMNS_PATH, "principal_table_columns", conn)

def load_payment_recovery_details_file(conn):
    load_csv_to_sqlite(PAYMENT_RECOVERY_DETAILS_PATH, "payment_recovery_details", conn)

def load_payment_confirmed_fraud_file(conn):
    load_csv_to_sqlite(PAYMENT_CONFIRMED_FRAUD_PATH, "payment_confirmed_fraud", conn)

def load_program_compliance_file(conn):
    load_csv_to_sqlite(PROGRAM_COMPLIANCE_PATH, "program_compliance", conn)

def load_risks_file(conn):
    load_csv_to_sqlite(RISKS_PATH, "risks", conn)

def load_new_risks_file(conn):
    load_csv_to_sqlite(NEW_RISKS_PATH, "new_risks", conn)

def load_eligibility_themes_file(conn):
    load_csv_to_sqlite(ELIGIBILITY_THEMES_PATH, "eligibility_themes", conn)

def load_recovery_amounts_file(conn):
    load_csv_to_sqlite(RECOVERY_AMOUNTS_PATH, "recovery_amounts", conn)

def load_survey_root_cause_file(conn):
    load_csv_to_sqlite(SURVEY_ROOT_CAUSE_PATH, "survey_root_cause", conn)

def load_ip_root_causes_file(conn):
    load_csv_to_sqlite(IP_ROOT_CAUSES_PATH, "ip_root_causes", conn)

def transform_and_insert_all_programs_data_aggregation_data():
    """
    Query program level data into transformed database.
    """
    cur.execute(ALL_PROGRAMS_DATA_AGGREGATION_DROP_TABLE_SQL)
    cur.execute(ALL_PROGRAMS_DATA_AGGREGATION_CREATE_TABLE_SQL)
    cur.execute(ALL_PROGRAMS_DATA_AGGREGATION_SELECT_AND_INSERT_SQL)
    conn.commit()

def transform_and_insert_all_agencies_data_aggregation_data():
    """
    Query agency level data into transformed database.
    """
    cur.execute(ALL_AGENCIES_DATA_AGGREGATION_DROP_TABLE_SQL)
    cur.execute(ALL_AGENCIES_DATA_AGGREGATION_CREATE_TABLE_SQL)
    cur.execute(ALL_AGENCIES_DATA_AGGREGATION_SELECT_AND_INSERT_TABLE_SQL)
    conn.commit()

def transform_and_insert_government_wide_data_aggregation_data():
    """
    Query government-wide level data into transformed database.
    """
    cur.execute(GOVERNMENT_WIDE_DATA_AGGREGATION_DROP_VIEW_SQL)
    cur.execute(GOVERNMENT_WIDE_DATA_AGGREGATION_CREATE_VIEW_SQL)
    conn.commit()

def transform_and_insert_all_agencies_years_data():
    """
    Query list of all agency-year combinations that have data.
    """
    cur.execute(ALL_AGENCIES_YEARS_DROP_VIEW_SQL)
    cur.execute(ALL_AGENCIES_YEARS_CREATE_VIEW_SQL)
    conn.commit()

load_all_programs_file(conn)
load_program_data_raw_file(conn)
load_agency_data_raw_file(conn)
load_ip_agency_pocs_file(conn)
load_principal_table_columns_file(conn)
load_payment_recovery_details_file(conn)
load_payment_confirmed_fraud_file(conn)
load_program_compliance_file(conn)
load_risks_file(conn)
load_new_risks_file(conn)
load_eligibility_themes_file(conn)
load_recovery_amounts_file(conn)
load_survey_root_cause_file(conn)
load_ip_root_causes_file(conn)
transform_and_insert_all_programs_data_aggregation_data()
transform_and_insert_all_agencies_data_aggregation_data()
transform_and_insert_government_wide_data_aggregation_data()
transform_and_insert_all_agencies_years_data()

conn.close()
