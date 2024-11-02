import os
from dateutil import parser
from django.utils import timezone
from django.conf import settings
from openpyxl.styles import Font
from pypdf import PdfReader
import re
import shutil
import io
import openpyxl
from openpyxl.styles import Alignment
import time
import pandas as pd
import numpy as np
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import pdfplumber
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import regex as re
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl import load_workbook
import datefinder
from calendar import monthrange
import calendar
from openpyxl.styles import Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from openpyxl import Workbook, load_workbook
from openpyxl.utils import get_column_letter
import openpyxl
from openpyxl.styles import PatternFill
from openpyxl.styles import Border, Side
from openpyxl.styles import Border, Side
from openpyxl.styles import Font
import logging
import openpyxl
from openpyxl.styles import Alignment

bold_font = Font(bold=True)
pd.options.display.float_format = "{:,.2f}".format
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from utils.common_functions import CommonFunctions

class ATSFunctions:
    def __init__(
        self, bank_names, pdf_paths, pdf_passwords, CASE_ID
    ):
        self.writer = None
        self.bank_names = bank_names
        self.pdf_paths = pdf_paths
        self.pdf_passwords = pdf_passwords
        self.account_number = ""
        self.file_name = None
        self.CASE_ID = CASE_ID
        start_date = "1"
        end_date = "2"
        self.commoner = CommonFunctions(
            bank_names, pdf_paths, pdf_passwords, start_date, end_date, CASE_ID
        )

    def single_name_entity_addition(self, df):
        df['Entity'] = df['Category']
        return df

    def single_analyze_entities(self, df):
        entity_analysis_df = df.groupby('Entity').agg(
            Entity_Name=('Entity', 'first'),
            Total_Debit=('Debit', 'sum'),
            Total_Credit=('Credit', 'sum'),
            No_of_times_occurred=('Entity', 'count')
        ).reset_index(drop=True)
        entity_analysis_df = entity_analysis_df.sort_values(by='No_of_times_occurred', ascending=False).reset_index(
            drop=True)
        return entity_analysis_df

    def single_bidirectional_analysis(self, df):
        # 1. Split Analysis Between Inflows and Outflows
        outflows = df[df['Debit'] > 0]
        inflows = df[df['Credit'] > 0]

        # 2. Category-Level Bidirectional Analysis
        category_summary = df.groupby('Category').agg({
            'Debit': 'sum',
            'Credit': 'sum',
            'Balance': 'last',
            'Value Date': 'count'
        }).rename(columns={'Value Date': 'Transaction Count'}).reset_index()
        category_summary['Net Flow'] = category_summary['Credit'] - category_summary['Debit']

        # 3. Entity-Level Bidirectional Analysis
        entity_summary = df.groupby('Entity').agg({
            'Debit': 'sum',
            'Credit': 'sum',
            'Balance': 'last',
            'Value Date': 'count'
        }).rename(columns={'Value Date': 'Transaction Count'}).reset_index()
        entity_summary['Net Flow'] = entity_summary['Credit'] - entity_summary['Debit']

        # 4. Net Cash Flow Calculation
        net_cash_flow = df['Credit'].sum() - df['Debit'].sum()

        # 5. Trend Analysis Over Time
        df['Value Date'] = pd.to_datetime(df['Value Date'], format='%d-%m-%Y', errors='coerce')
        df['YearMonth'] = df['Value Date'].dt.to_period('M')
        monthly_summary = df.groupby('YearMonth').agg({
            'Debit': 'sum',
            'Credit': 'sum',
            'Balance': 'last'
        }).reset_index()
        monthly_summary['Net Flow'] = monthly_summary['Credit'] - monthly_summary['Debit']

        # 6. Balance Analysis
        df['Daily Net Flow'] = df['Credit'].fillna(0) - df['Debit'].fillna(0)
        df['Cumulative Balance'] = df['Daily Net Flow'].cumsum() + df['Balance'].iloc[0]

        # 7. Extract Useful Insights for Bidirectional Analysis
        top_expense_categories = category_summary.sort_values(by='Debit', ascending=False).head(5)
        top_income_sources = entity_summary.sort_values(by='Credit', ascending=False).head(5)
        high_net_flow_entities = entity_summary.sort_values(by='Net Flow', ascending=False).head(5)

        # Returning all results
        return {
            'outflows': outflows,
            'inflows': inflows,
            'category_summary': category_summary,
            'entity_summary': entity_summary,
            'net_cash_flow': net_cash_flow,
            'monthly_summary': monthly_summary,
            'cumulative_balance': df[['Value Date', 'Cumulative Balance']],
            'top_expense_categories': top_expense_categories,
            'top_income_sources': top_income_sources,
            'high_net_flow_entities': high_net_flow_entities
        }

    def single_fifo_analysis(self, df):
        # Step 1: Separate Credits and Debits
        credits = df[df['Credit'] > 0].copy()
        debits = df[df['Debit'] > 0].copy()
        credits['Remaining'] = credits['Credit']

        # Step 2: Apply FIFO Logic for Allocating Credits to Debits
        allocation_summary = []

        for j, credit in credits.iterrows():
            credit_amount = credit['Remaining']

            for i, debit in debits.iterrows():
                if credit_amount <= 0:
                    break
                if debit['Debit'] > 0:
                    allocation = min(credit_amount, debit['Debit'])

                    # Create detailed allocation record
                    allocation_summary.append({
                        'allocated_date': credit['Value Date'],
                        'allocated_entity': credit['Entity'],
                        'allocated_category': credit['Category'],
                        'allocated_amount': allocation,
                        'allocated_description': credit['Description'],
                        'used_in_date': debit['Value Date'],
                        'used_in_entity': debit['Entity'],
                        'used_in_category': debit['Category'],
                        'used_in_description': debit['Description'],
                        'remaining_amount': credit_amount - allocation,
                        'days_in_between_allocation_and_usage': max((debit['Value Date'] - credit['Value Date']).days,
                                                                    0)
                    })

                    # Update remaining balance of the credit and debit
                    credits.at[j, 'Remaining'] -= allocation
                    debits.at[i, 'Debit'] -= allocation

                    # Decrease credit amount to be allocated
                    credit_amount -= allocation

        allocation_df = pd.DataFrame(allocation_summary)

        # Step 3: Group by Entity and Category for Detailed Insights
        entity_summary = allocation_df.groupby('allocated_entity').agg({
            'allocated_amount': 'sum',
            'used_in_description': 'count'
        }).rename(columns={'allocated_amount': 'Total_Allocated', 'used_in_description': 'Transaction_Count'})

        category_summary = allocation_df.groupby('allocated_category').agg({
            'allocated_amount': 'sum',
            'used_in_description': 'count'
        }).rename(columns={'allocated_amount': 'Total_Allocated', 'used_in_description': 'Transaction_Count'})

        # Step 4: Add Summary Notes
        summary_note = """
        FIFO Analysis Summary:
        - Allocations are made using a FIFO approach where the earliest credits are used to cover debits.
        - The 'allocation_df' DataFrame contains detailed records of all debit-credit allocations.
        """
        print(summary_note)

        return {
            'debits': debits,
            'credits': credits,
            'allocation_df': allocation_df,
            'entity_summary': entity_summary,
            'category_summary': category_summary
        }

    def single_money_trail_analysis(self, df):
        # Step 1: Summarize inflows and outflows for each Entity
        entity_summary = df.groupby('Entity').agg(
            total_inflows=pd.NamedAgg(column='Credit', aggfunc='sum'),
            total_outflows=pd.NamedAgg(column='Debit', aggfunc='sum'),
            transaction_count=pd.NamedAgg(column='Value Date', aggfunc='count')
        ).reset_index()

        print("Entity-wise Summary of Inflows and Outflows:")
        print(entity_summary)

        # Step 2: Identify transaction patterns over time
        df['Value Date'] = pd.to_datetime(df['Value Date'])

        # Deeper analysis - calculating net flow and cumulative balance per entity
        df['Net Flow'] = df['Credit'].fillna(0) - df['Debit'].fillna(0)
        cumulative_balance = df.groupby('Entity').agg(
            total_net_flow=pd.NamedAgg(column='Net Flow', aggfunc='sum'),
            avg_balance=pd.NamedAgg(column='Balance', aggfunc='mean'),
            max_balance=pd.NamedAgg(column='Balance', aggfunc='max'),
            min_balance=pd.NamedAgg(column='Balance', aggfunc='min')
        ).reset_index()

        print("Deeper Analysis - Cumulative Balance and Net Flow per Entity:")
        print(cumulative_balance)

        # Finding entities with significant inflows or outflows
        significant_inflows = df[df['Credit'] > df['Credit'].quantile(0.95)]
        significant_outflows = df[df['Debit'] > df['Debit'].quantile(0.95)]

        print("Entities with Significant Inflows (Top 5%):")
        print(significant_inflows[['Entity', 'Credit', 'Value Date', 'Description']])

        print("Entities with Significant Outflows (Top 5%):")
        print(significant_outflows[['Entity', 'Debit', 'Value Date', 'Description']])

        return df

    def single_person_sheets(self, dfs, name_dfs):
        result = {}

        # Iterate over the keys of dfs and name_dfs (which are identical)
        for key in dfs:
            # Retrieve the corresponding dataframe
            one_df = dfs[key]

            initial_df = one_df.copy()   
            df = self.commoner.category_add_ca(initial_df)
            df = self.single_name_entity_addition(df)
            df['Value Date'] = pd.to_datetime(df['Value Date'], format='%d-%m-%Y', errors='coerce')
            new_tran_df = self.commoner.another_method(df) 

            fifo = self.single_fifo_analysis(new_tran_df)
            money_trail = self.single_money_trail_analysis(new_tran_df)
            entity_analysis = self.single_analyze_entities(new_tran_df)
            bidirectional_analysis = self.single_bidirectional_analysis(new_tran_df)

            transaction_sheet_df = self.commoner.transaction_sheet(df)
            # transaction_sheet_df['Value Date'] = pd.to_datetime(transaction_sheet_df['Value Date']).dt.strftime('%d-%m-%Y')

            new_tran_df = self.commoner.another_method(transaction_sheet_df)
            eod_sheet_df = self.commoner.eod(df)
            investment_df = self.commoner.total_investment(new_tran_df)
            creditor_df = self.commoner.creditor_list(transaction_sheet_df)
            debtor_df = self.commoner.debtor_list(transaction_sheet_df)
            cash_withdrawal_df = self.commoner.cash_withdraw(new_tran_df)
            cash_deposit_df = self.commoner.cash_depo(new_tran_df)
            dividend_int_df = self.commoner.div_int(new_tran_df)
            emi_df = self.commoner.emi(new_tran_df)
            refund = self.commoner.refund_reversal(new_tran_df)
            suspense_credit_df = self.commoner.suspense_credit(new_tran_df)
            suspense_debit_df = self.commoner.suspense_debit(new_tran_df)

            # Extract the name and account number from name_dfs
            name, acc_number = name_dfs[key]

            # Store the combined information in the result dictionary
            result[key] = {
                "name":name,
                "acc_number":acc_number,
                "data":{
                    "df":df,
                    "new_tran_df":new_tran_df,
                    "fifo":fifo,
                    "money_trail":money_trail,
                    "entity_analysis":entity_analysis,
                    "bidirectional_analysis":bidirectional_analysis,
                    "transaction_sheet_df":transaction_sheet_df,
                    "eod_sheet_df":eod_sheet_df,
                    "investment_df":investment_df,
                    "creditor_df":creditor_df,
                    "debtor_df":debtor_df,
                    "cash_withdrawal_df":cash_withdrawal_df,
                    "cash_deposit_df":cash_deposit_df,
                    "dividend_int_df":dividend_int_df,
                    "emi_df":emi_df,
                    "refund":refund,
                    "suspense_credit_df":suspense_credit_df,
                    "suspense_debit_df":suspense_debit_df
                }
            }
        # Return the resulting dictionary
        return result
    

    def cummalative_person_sheets(self, single_person_output):
        # Extract the 'new_tran_df' from each entry in the output
        # new_tran_dfs = (dataframes[1] for _, _, dataframes in single_person_output.values())

        new_tran_dfs = (data_dict["data"]["new_tran_df"] for data_dict in single_person_output.values())

        # Concatenate all new_tran_df DataFrames into a single DataFrame
        cumulative_df = pd.concat(new_tran_dfs, ignore_index=True)

        # Return the concatenated DataFrame
        return cumulative_df
