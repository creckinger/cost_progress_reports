"""
Version 1.1
This script processes and generates progress reports for a construction project, using data from an Excel file.
Improved rounding
"""

import pandas as pd
from pathlib import Path
from datetime import date
import xlsxwriter
import decimal
import math

# USER INPUTS
# filename = "EA-VILLAPETRUSSE-PEINTURE.xlsx"
# prorata_base = "htva"  # choose htva or ttc
# language = "french"  # choose french, german, or english

# Global Variables To Generate Automatically
# CURRENT_DIR = Path(__file__).parent
# DATA_DIR = CURRENT_DIR/"data"
# filepath = DATA_DIR / filename
# filename_base = filepath.stem
# OUTPUT_DIR = CURRENT_DIR /"output"

# Translations
translations = {
    "french": {
        "title": "ETAT D'AVANCEMENT",
        "project": "Projet :",
        "date": "Date :",
        "state": "Etat :",
        "company": "Entreprise :",
        "period": "Période :",
        "totals": "TOTAUX* :",
        "pos": "Pos",
        "position_label": "Libellé position",
        "unit": "Unité",
        "unit_price": "Prix U",
        "planned_quantity": "Quantité prévue",
        "current_period_quantity": "Quantité période actuelle",
        "previous_periods_quantity": "Quantités périodes précécentes",
        "total_quantity": "Quantité totale cumulée",
        "planned_sum": "Somme quantités prévues",
        "current_period_sum": "Somme période actuelle",
        "previous_periods_sum": "Somme périodes précédentes",
        "total_sum_no_discount": "Somme totale cumulée sans remise",
        "discount_pct": "Remise %",
        "discount_amount": "Montant remise",
        "total_sum_with_discount": "Somme totale cumulée avec remise",
        "rounding_warning": "En raison d'erreurs d'arrondi dues à la facturation cumulée, il peut arriver que les totaux indiqués ne correspondent pas à 100% à la facture définitive."
    },
    "german": {
        "title": "FORTSCHRITTSBERICHT",
        "project": "Projekt :",
        "date": "Datum :",
        "state": "Zustand :",
        "company": "Unternehmen :",
        "period": "Zeitraum :",
        "totals": "SUMMEN* :",
        "pos": "Pos",
        "position_label": "Positionsbezeichnung",
        "unit": "Einheit",
        "unit_price": "Stückpreis",
        "planned_quantity": "Geplante Menge",
        "current_period_quantity": "Menge laufender Zeitraum",
        "previous_periods_quantity": "Mengen vorherige Zeiträume",
        "total_quantity": "Gesamtmenge kumuliert",
        "planned_sum": "Geplante Summe",
        "current_period_sum": "Summe laufender Zeitraum",
        "previous_periods_sum": "Summe vorherige Zeiträume",
        "total_sum_no_discount": "Gesamtsumme ohne Rabatt",
        "discount_pct": "Rabatt %",
        "discount_amount": "Rabattbetrag",
        "total_sum_with_discount": "Gesamtsumme mit Rabatt",
        "rounding_warning": "Aufgrund von Rundungsfehlern bei der kumulierten Abrechnung kann es vorkommen, dass die angegebenen Summen nicht zu 100% mit der Endrechnung übereinstimmen."
    },
    "english": {
        "title": "PROGRESS REPORT",
        "project": "Project :",
        "date": "Date :",
        "state": "State :",
        "company": "Company :",
        "period": "Period :",
        "totals": "TOTALS* :",
        "pos": "Pos",
        "position_label": "Position Label",
        "unit": "Unit",
        "unit_price": "Unit Price",
        "planned_quantity": "Planned Quantity",
        "current_period_quantity": "Current Period Quantity",
        "previous_periods_quantity": "Previous Periods Quantities",
        "total_quantity": "Total Quantity Cumulative",
        "planned_sum": "Planned Sum",
        "current_period_sum": "Current Period Sum",
        "previous_periods_sum": "Previous Periods Sum",
        "total_sum_no_discount": "Total Sum Without Discount",
        "discount_pct": "Discount %",
        "discount_amount": "Discount Amount",
        "total_sum_with_discount": "Total Sum With Discount",
        "rounding_warning": "Due to rounding errors caused by cumulative billing, the indicated totals may not match 100% with the final invoice."
    }
}

# Define rounding function
def round_half_up(n, decimals=2):
    # Set the precision high enough to handle the multiplication accurately
    decimal.getcontext().prec = 10
    decimal.getcontext().rounding = decimal.ROUND_HALF_UP
    
    # Perform the multiplication using Decimal
    n = decimal.Decimal(str(n))
    factor = decimal.Decimal(10) ** decimals
    shifted = n * factor
    
    # Round the shifted value
    rounded_value = shifted.to_integral_value()
    return float(rounded_value / factor)


# Convert percentage to integer
def percent_to_integer(decimal_number):
    return math.floor(decimal_number * 100)

# Compute main dataframe
def compute_main_dataframe(df_quantities, state_list, current_state):
    current_state_main_data = df_quantities[["Pos", "Type", "Désignation (libellé position)", "Unités", "Prix unitaire", "Remise"]].copy()
    current_state_main_data["Quantité prévue"] = df_quantities["Quantité prévue"]
    current_state_main_data["Quantité période actuelle"] = df_quantities[current_state].apply(round_half_up)
    current_state_main_data["Quantités périodes précécentes"] = 0
    for state in state_list:
        if state != current_state:
            current_state_main_data["Quantités périodes précécentes"] += df_quantities[state].apply(round_half_up)
        else:
            break
    current_state_main_data["Quantités cumulés"] = (current_state_main_data["Quantité période actuelle"] + current_state_main_data["Quantités périodes précécentes"]).apply(round_half_up)
    current_state_main_data["Somme quantité prévue"] = (df_quantities["Prix unitaire"] * df_quantities["Quantité prévue"]).apply(round_half_up)
    current_state_main_data["Somme période actuelle"] = (df_quantities["Prix unitaire"] * current_state_main_data["Quantité période actuelle"]).apply(round_half_up)
    current_state_main_data["Somme périodes précédentes"] = (df_quantities["Prix unitaire"] * current_state_main_data["Quantités périodes précécentes"]).apply(round_half_up)
    current_state_main_data["Somme totale cumulée sans remise"] = (df_quantities["Prix unitaire"] * current_state_main_data["Quantités cumulés"]).apply(round_half_up)
    current_state_main_data["Montant remise"] = (current_state_main_data["Somme totale cumulée sans remise"] * df_quantities["Remise"]/100).apply(round_half_up)
    current_state_main_data["Somme totale cumulée avec remise"] = (current_state_main_data["Somme totale cumulée sans remise"] - current_state_main_data["Montant remise"]).apply(round_half_up)
    return current_state_main_data

# Compute billing block
def compute_billing_block(current_state_main_data, sum_invoices_before_current_state, current_state_vat, current_state_guaranty, current_state_prorata, prorata_base, has_discount):
    billing_block_dict = {}
    if has_discount:
        billing_block_dict["Valeur totale nette des travaux exécutés (HTVA)"] = round_half_up(current_state_main_data["Somme totale cumulée avec remise"].sum())
    else:
        billing_block_dict["Valeur totale nette des travaux exécutés (HTVA)"] = round_half_up(current_state_main_data["Somme totale cumulée sans remise"].sum())      
    billing_block_dict["Valeur totale des acomptes déjà payés (HTVA)"] = sum_invoices_before_current_state
    billing_block_dict["Valeur des travaux nouvellement exécutés (HTVA)"] = billing_block_dict["Valeur totale nette des travaux exécutés (HTVA)"] - billing_block_dict["Valeur totale des acomptes déjà payés (HTVA)"]
    billing_block_dict[f"TVA {current_state_vat} %"] = round_half_up(billing_block_dict["Valeur des travaux nouvellement exécutés (HTVA)"] * float(current_state_vat / 100))
    billing_block_dict["Valeur des travaux nouvellement exécutés (TTC)"] = billing_block_dict["Valeur des travaux nouvellement exécutés (HTVA)"] + billing_block_dict[f"TVA {current_state_vat} %"]
    billing_block_dict[f"Garantie {current_state_guaranty} %"] = -round_half_up(billing_block_dict["Valeur des travaux nouvellement exécutés (HTVA)"] * float(current_state_guaranty / 100))
    if current_state_prorata != 0:
        if prorata_base == "ttc":
            billing_block_dict[f"Pro Rata {current_state_prorata} % sur TTC"] = -round_half_up(billing_block_dict["Valeur des travaux nouvellement exécutés (TTC)"] * float(current_state_prorata / 100))
            _prorata_amount_final = billing_block_dict[f"Pro Rata {current_state_prorata} % sur TTC"]
        elif prorata_base == "htva":
            billing_block_dict[f"Pro Rata {current_state_prorata} % sur HTVA"] = -round_half_up(billing_block_dict["Valeur des travaux nouvellement exécutés (HTVA)"] * float(current_state_prorata / 100))
            _prorata_amount_final = billing_block_dict[f"Pro Rata {current_state_prorata} % sur HTVA"]
        else:
            raise Exception("Choose a basis for Pro Rata please")
    else:
        _prorata_amount_final = 0
    billing_block_dict["Total à payer (EUR)"] = round_half_up(
        billing_block_dict["Valeur des travaux nouvellement exécutés (TTC)"] + 
        billing_block_dict[f"Garantie {current_state_guaranty} %"] + 
        _prorata_amount_final
    )
    return billing_block_dict

# Write header
def write_header(workbook, worksheet, has_discount, current_state, revision, project_name, document_date, period, lang):
    trans = translations[lang]
    text_format_title = workbook.add_format({'bold': True, 'align': 'center'})
    format_cell = workbook.add_format({"bottom": 0, "top": 1, "left": 0, "right": 0})
    text_format_key = workbook.add_format({'bold': True})
    text_format_value = workbook.add_format({'bold': True})
    text_format_value_date = workbook.add_format({'bold': True, 'num_format': 'dd/mm/yyyy'})
    text_format = workbook.add_format({'bold': True, 'text_wrap': True, "bottom": 1, "top": 1, "left": 0, "right": 0, "align": "center", "valign": "vcenter"})

    # Merge and write title
    title_range = "A1:O1" if has_discount else "A1:L1"
    worksheet.merge_range(title_range, f"{trans['title']} {current_state} - rev {revision}", text_format_title)

    # Fill cells for header layout
    columns = ["A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "I2", "J2", "K2", "L2"]
    if has_discount:
        columns += ["M2", "N2", "O2"]
    for col in columns:
        worksheet.write(col, "", format_cell)

    # Write project info
    worksheet.write(2, 0, trans["project"], text_format_key)
    worksheet.write(2, 1, project_name, text_format_value)

    date_col = "M3" if has_discount else "J3"
    date_range = "N3:O3" if has_discount else "K3:L3"
    worksheet.write(date_col, trans["date"], text_format_key)
    worksheet.merge_range(date_range, document_date, text_format_value_date)

    worksheet.write("A4", trans["state"], text_format_key)
    worksheet.write("B4", f"{current_state} - rev {revision}", text_format_value)

    worksheet.write("A5", trans["company"], text_format_key)
    worksheet.write("B5", "RECKINGER PEINTURES-DECORS SARL", text_format_value)

    worksheet.merge_range("E4:F4", trans["period"], text_format_key)
    worksheet.merge_range("G4:I4", period, text_format_value)

    # Write column titles
    column_titles = [
        trans['pos'], trans['position_label'], trans['unit'], trans['unit_price'], trans['planned_quantity'], trans['current_period_quantity'],
        trans['previous_periods_quantity'], trans['total_quantity'], trans['planned_sum'],
        trans['current_period_sum'], trans['previous_periods_sum'], trans['total_sum_no_discount']
    ]
    if has_discount:
        column_titles += [trans['discount_pct'], trans['discount_amount'], trans['total_sum_with_discount']]
    for col_num, title in enumerate(column_titles):
        worksheet.write(6, col_num, title, text_format)
    return 7

# Write main dataframe
def write_main_dataframe_to_excel(workbook, worksheet, current_state_main_data, start_row, has_discount):
    row_text_format_title = workbook.add_format({'bold': True, "bottom": 0, "top": 0, "left": 0, "right": 0, "align": "left"})
    row_text_format_position = workbook.add_format({'bold': False, "bottom": 0, "top": 0, "left": 0, "right": 0})
    row_number_format_amount = workbook.add_format({'bold': False, "bottom": 0, "top": 0, "left": 0, "right": 0, 'num_format': '#,##0.00'})
    row_number_format_pct = workbook.add_format({'bold': False, "bottom": 0, "top": 0, "left": 0, "right": 0, 'num_format': '#,##0.0'})

    xlsxrow = start_row
    for index, row in current_state_main_data.iterrows():
        if row["Type"] == "T":
            worksheet.write_string(xlsxrow, 0, row["Pos"], row_text_format_title)
            worksheet.write_string(xlsxrow, 1, row["Désignation (libellé position)"], row_text_format_title)
        elif row["Type"] == "P":
            worksheet.write_string(xlsxrow, 0, row["Pos"], row_text_format_position)
            worksheet.write_string(xlsxrow, 1, row["Désignation (libellé position)"], row_text_format_position)
            worksheet.write_string(xlsxrow, 2, row["Unités"], row_text_format_position)
            worksheet.write_number(xlsxrow, 3, row["Prix unitaire"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 4, row["Quantité prévue"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 5, row["Quantité période actuelle"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 6, row["Quantités périodes précécentes"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 7, row["Quantités cumulés"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 8, row["Somme quantité prévue"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 9, row["Somme période actuelle"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 10, row["Somme périodes précédentes"], row_number_format_amount)
            worksheet.write_number(xlsxrow, 11, row["Somme totale cumulée sans remise"], row_number_format_amount)
            if has_discount:
                worksheet.write_number(xlsxrow, 12, row["Remise"], row_number_format_pct)
                worksheet.write_number(xlsxrow, 13, row["Montant remise"], row_number_format_amount)
                worksheet.write_number(xlsxrow, 14, row["Somme totale cumulée avec remise"], row_number_format_amount)
        xlsxrow += 1
    return xlsxrow

# Write totals row
def write_totals_row_to_excel(workbook, worksheet, current_state_main_data, start_row, has_discount, lang):
    trans = translations[lang]
    text_format_sums = workbook.add_format({'bold': True, "bottom": 0, "top": 1, "left": 0, "right": 0})
    number_format_sums = workbook.add_format({'bold': True, "bottom": 0, "top": 1, "left": 0, "right": 0, 'num_format': '#,##0.00'})
    blank_cell_format = workbook.add_format({"bottom": 0, "top": 1, "left": 0, "right": 0})

    for col in range(0, 8):
        worksheet.write(start_row, col, "", blank_cell_format)

    worksheet.write_string(start_row, 7, trans["totals"], text_format_sums)
    worksheet.write_number(start_row, 8, round_half_up(current_state_main_data["Somme quantité prévue"].sum()), number_format_sums)
    worksheet.write_number(start_row, 9, round_half_up(current_state_main_data["Somme période actuelle"].sum()), number_format_sums)
    worksheet.write_number(start_row, 10, round_half_up(current_state_main_data["Somme périodes précédentes"].sum()), number_format_sums)

    if has_discount:
        worksheet.write_number(start_row, 11, round_half_up(current_state_main_data["Somme totale cumulée sans remise"].sum()), number_format_sums)
        worksheet.write(start_row, 12, "", blank_cell_format)
        worksheet.write(start_row, 13, "", blank_cell_format)
        worksheet.write_number(start_row, 14, round_half_up(current_state_main_data["Somme totale cumulée avec remise"].sum()), number_format_sums)
    else:
        worksheet.write_number(start_row, 11, round_half_up(current_state_main_data["Somme totale cumulée sans remise"].sum()), number_format_sums)

    return start_row + 1

# Write billing block
def write_billing_block_to_excel(workbook, worksheet, billing_block_dict, start_row, has_discount):
    text_format_key = workbook.add_format({'bold': True, 'align': "right"})
    number_format_value = workbook.add_format({'bold': True, 'num_format': '#,##0.00'})
    _rowtowrite = start_row
    col_key = 13 if has_discount else 10
    col_value = 14 if has_discount else 11
    for key, value in billing_block_dict.items():
        worksheet.write_string(_rowtowrite, col_key, key, text_format_key)
        worksheet.write_number(_rowtowrite, col_value, value, number_format_value)
        _rowtowrite += 1
    return _rowtowrite

# Write comments section
def write_comments_section_to_excel(workbook, worksheet, start_row, lang):
    trans = translations[lang]
    comments = trans['rounding_warning'].split(', ')
    text_format_normal = workbook.add_format({'bold': False, 'italic': True, "bottom": 0, "top": 0, "left": 0, "right": 0})
    current_row = start_row
    for comment in comments:
        worksheet.write_string(current_row, 0, comment, text_format_normal)
        current_row += 1
    return current_row


def process_excel_file(filepath, language, prorata_base):
    # Load the Excel file
    df_projinfo = pd.read_excel(filepath, sheet_name="projinfo", index_col="key")
    project_name = df_projinfo.loc["project_name", "value"]

    df_statelist = pd.read_excel(filepath, sheet_name="statelist", index_col="state")

    df_quantities = pd.read_excel(filepath, sheet_name="quantities", dtype={"Pos": "str"})
    has_discount = df_quantities["Remise"].sum() > 0

    # Your script logic based on user inputs
    if prorata_base == 'htva':
        # Implement HTVA logic
        pass
    elif prorata_base == 'ttc':
        # Implement TTC logic
        pass
    
    if language == 'french':
        # Implement French language logic
        pass
    elif language == 'german':
        # Implement German language logic
        pass
    elif language == 'english':
        # Implement English language logic
        pass

    if "language" in df_projinfo.index:
        language = df_projinfo.loc["language", "value"]

    # DATA CLEANING AND FORMATTING

    df_statelist["invoice_net"] = df_statelist["invoice_net"].fillna(0)
    df_statelist["invoice_number"] = df_statelist["invoice_number"].fillna("")

    df_statelist['period_start'] = df_statelist['period_start'].apply(lambda x: x.date() if not pd.isnull(x) else x)
    df_statelist['period_end'] = df_statelist['period_end'].apply(lambda x: x.date() if not pd.isnull(x) else x)

    df_quantities.fillna({
        "Pos": "",
        "Type": "",
        "Désignation (libellé position)": "",
        "Unités": "",
        "Prix unitaire": 0,
        "Remise": 0,
        "Quantité prévue": 0,
    }, inplace=True)

    state_list = df_statelist.index.tolist()
    df_quantities[state_list] = df_quantities[state_list].fillna(0)

    processed_files = []

    # Main loop
    for _statenumber, state in enumerate(df_statelist.index.tolist(), 1):
        current_state = state
        state_list_exct_current = state_list[:_statenumber - 1]

        current_state_revision = df_statelist.loc[str(current_state), "revision"]
        current_state_period_start = df_statelist.loc[str(current_state), "period_start"]
        current_state_period_end = df_statelist.loc[str(current_state), "period_end"]
        current_state_period = f"{current_state_period_start} --- {current_state_period_end}"
        current_state_vat = df_statelist.loc[str(current_state), "vat_pct"]
        current_state_guaranty = df_statelist.loc[str(current_state), "guaranty_pct"]
        current_state_prorata = df_statelist.loc[str(current_state), "prorata_pct"]

        if "prorata_type" in df_statelist.columns: # remove when all templates are at the new version and adapt script completely!
            current_state_prorata_base = df_statelist.loc[str(current_state), "prorata_type"]
        else:
            current_state_prorata_base = prorata_base


        sum_invoices_before_current_state = sum(df_statelist["invoice_net"][:_statenumber - 1])
        current_state_document_date = date.today()

        current_state_main_data = compute_main_dataframe(df_quantities, state_list, current_state)

        billing_block_dict = compute_billing_block(
            current_state_main_data,
            sum_invoices_before_current_state,
            current_state_vat,
            current_state_guaranty,
            current_state_prorata,
            current_state_prorata_base,
            has_discount
        )

        # List to collect all processed file paths
        print(filepath)
        filename_base = Path(filepath).stem
        processed_filepath = Path(f"{filename_base}-{current_state}-rev{current_state_revision}.xlsx")
        processed_files.append(processed_filepath)

        workbook = xlsxwriter.Workbook(processed_filepath)
        worksheet = workbook.add_worksheet("Etat d'avancement")

        worksheet.set_column(0, 0, 15)
        worksheet.set_column(1, 1, 40)
        worksheet.set_column(2, 2, 6)
        worksheet.set_column(3, 3, 8)

        start_row_current_state_main_data = write_header(workbook, worksheet, has_discount, current_state, current_state_revision, project_name, current_state_document_date, current_state_period, language)
        next_row = write_main_dataframe_to_excel(workbook, worksheet, current_state_main_data, start_row_current_state_main_data, has_discount)
        next_row_after_totals = write_totals_row_to_excel(workbook, worksheet, current_state_main_data, next_row, has_discount, language)
        next_row_after_billing = write_billing_block_to_excel(workbook, worksheet, billing_block_dict, next_row_after_totals + 1, has_discount)
        next_row_after_comments = write_comments_section_to_excel(workbook, worksheet, next_row_after_billing, language)

        workbook.close()
    
    return processed_files