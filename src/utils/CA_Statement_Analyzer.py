# from findaddy.decorators import timer_decorator
# from django.conf import settings
import shutil
import os
import pandas as pd
from openpyxl.styles import Font
import logging
from openpyxl import Workbook, load_workbook
import sys

bold_font = Font(bold=True)
pd.options.display.float_format = "{:,.2f}".format
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from utils.common_functions import CommonFunctions
from utils.ats_statement_analyzer import ATSFunctions
from utils.model_loader import model


class CABankStatement:
    def __init__(
            self, bank_names, pdf_paths, pdf_passwords, start_date, end_date, CA_ID, progress_data
    ):
        self.writer = None
        self.bank_names = bank_names
        self.pdf_paths = pdf_paths
        self.pdf_passwords = pdf_passwords
        self.start_date = start_date
        self.end_date = end_date
        self.account_number = ""
        self.file_name = None
        self.CA_ID = CA_ID
        self.commoner = CommonFunctions(bank_names, pdf_paths, pdf_passwords, start_date, end_date, CA_ID)
        self.atser = ATSFunctions(bank_names, pdf_paths, pdf_passwords, CA_ID)
        self.progress_function = progress_data.get('progress_func')
        self.current_progress = progress_data.get('current_progress')
        self.total_progress = progress_data.get('total_progress')

    def CA_Bank_statement(self, filename, dfs, name_dfs):
        data = []
        # num_pairs = len(pd.Series(dfs).to_dict())

        for key, value in name_dfs.items():
            bank_name = key
            acc_name = value[0]
            acc_num = value[1]
            if str(acc_num) == "None":
                masked_acc_num = "None"
            else:
                masked_acc_num = "X" * (len(acc_num) - 4) + acc_num[-4:]
            data.append([masked_acc_num, acc_name, bank_name])
            for item in data:
                item[2] = "".join(
                    character for character in item[2] if character.isalpha()
                )

        name_n_num_df = self.commoner.process_name_n_num_df(data)

        initial_df = pd.concat(list(dfs.values())).fillna("").reset_index(drop=True)
        self.progress_function(self.current_progress, self.total_progress, info=f"Categorizing transactions")
        self.current_progress += 1
        df = self.commoner.category_add_ca(initial_df)
        new_tran_df = self.commoner.another_method(df)

        eod_sheet_df = self.commoner.eod(df)

        opening_bal, closing_bal = self.commoner.opening_and_closing_bal(
            eod_sheet_df, df
        )
        self.progress_function(self.current_progress, self.total_progress, info=f"Generating summary sheet")
        self.current_progress += 1
        sheet_name = "Summary"
        summary_df_list = self.commoner.summary_sheet(df, opening_bal, closing_bal, new_tran_df)

        name_n_num_df.to_excel(self.writer, sheet_name=sheet_name, index=False)
        summary_df_list[0].to_excel(
            self.writer,
            sheet_name=sheet_name,
            startrow=name_n_num_df.shape[0] + 2,
            index=False,
        )
        summary_df_list[1].to_excel(
            self.writer,
            sheet_name=sheet_name,
            startrow=name_n_num_df.shape[0] + summary_df_list[0].shape[0] + 4,
            index=False,
        )
        summary_df_list[2].to_excel(
            self.writer,
            sheet_name=sheet_name,
            startrow=name_n_num_df.shape[0]
                     + summary_df_list[0].shape[0]
                     + summary_df_list[1].shape[0]
                     + 6,
            index=False,
        )
        summary_df_list[3].to_excel(
            self.writer,
            sheet_name=sheet_name,
            startrow=name_n_num_df.shape[0]
                     + summary_df_list[0].shape[0]
                     + summary_df_list[1].shape[0]
                     + summary_df_list[2].shape[0]
                     + 8,
            index=False,
        )

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Transaction Sheet")
        self.current_progress += 1
        transaction_sheet_df = self.commoner.transaction_sheet(df)
        transaction_sheet_df['Value Date'] = pd.to_datetime(transaction_sheet_df['Value Date']).dt.strftime('%d-%m-%Y')

        new_tran_df = self.commoner.another_method(transaction_sheet_df)
        new_tran_df.to_excel(self.writer, sheet_name='Transactions', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating EOD Balance Sheet")
        self.current_progress += 1
        eod_sheet_df.to_excel(self.writer, sheet_name='EOD Balance', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Investment Sheet")
        self.current_progress += 1
        investment_df = self.commoner.total_investment(new_tran_df)
        investment_df.to_excel(self.writer, sheet_name='Investment', index=False)

        # redemption_investment_df = self.commoner.redemption_investment(transaction_sheet_df)
        # redemption_investment_df.to_excel(self.writer, sheet_name='Redemption of Investment', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Creditors Sheet")
        self.current_progress += 1
        creditor_df = self.commoner.creditor_list(transaction_sheet_df)
        creditor_df.to_excel(self.writer, sheet_name='Creditors', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Debtors Sheet")
        self.current_progress += 1
        debtor_df = self.commoner.debtor_list(transaction_sheet_df)
        debtor_df.to_excel(self.writer, sheet_name='Debtors', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Cash Withdrawal Sheet")
        self.current_progress += 1
        cash_withdrawal_df = self.commoner.cash_withdraw(new_tran_df)
        cash_withdrawal_df.to_excel(self.writer, sheet_name='Cash Withdrawal', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Cash Deposit Sheet")
        self.current_progress += 1
        cash_deposit_df = self.commoner.cash_depo(new_tran_df)
        cash_deposit_df.to_excel(self.writer, sheet_name='Cash Deposit', index=False)

        self.progress_function(self.current_progress, self.total_progress,
                               info=f"Generating Redemption, Dividend & Interest Sheet")
        self.current_progress += 1
        dividend_int_df = self.commoner.div_int(new_tran_df)
        dividend_int_df.to_excel(self.writer, sheet_name='Redemption, Dividend & Interest', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Probable EMI Sheet")
        self.current_progress += 1
        emi_df = self.commoner.emi(new_tran_df)
        emi_df.to_excel(self.writer, sheet_name='Probable EMI', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Refund-Reversal Sheet")
        self.current_progress += 1
        refund = self.commoner.refund_reversal(new_tran_df)
        refund.to_excel(self.writer, sheet_name='Refund-Reversal', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Suspense Credit Sheet")
        self.current_progress += 1
        suspense_credit_df = self.commoner.suspense_credit(new_tran_df)
        suspense_credit_df.to_excel(self.writer, sheet_name='Suspense Credit', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Suspense Debit Sheet")
        self.current_progress += 1
        suspense_debit_df = self.commoner.suspense_debit(new_tran_df)
        suspense_debit_df.to_excel(self.writer, sheet_name='Suspense Debit', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Payment Sheet")
        self.current_progress += 1
        Payment = self.commoner.payment(new_tran_df)
        Payment.to_excel(self.writer, sheet_name='Payment Voucher', index=False)

        self.progress_function(self.current_progress, self.total_progress, info=f"Generating Receipt Sheet")
        self.current_progress += 1
        Receipt = self.commoner.receipt(new_tran_df)
        Receipt.to_excel(self.writer, sheet_name='Receipt Voucher', index=False)

        bank_avg_balance_df = self.commoner.calculate_fixed_day_average(eod_sheet_df)
        loan_value_df = self.commoner.process_avg_last_6_months(filename, bank_avg_balance_df, eod_sheet_df)

        return loan_value_df

    # @timer_decorator
    def start_extraction(self):
        CA_ID = self.CA_ID

        dfs = {}
        name_dfs = {}
        i = 0

        for bank in self.bank_names:
            bank = str(f"{bank}{i}")
            pdf_path = self.pdf_paths[i]
            pdf_password = self.pdf_passwords[i]
            start_date = self.start_date[i]
            end_date = self.end_date[i]

            self.progress_function(self.current_progress, self.total_progress, info=f"Extracting bank statement")
            self.current_progress += 1
            dfs[bank], name_dfs[bank] = self.commoner.extraction_process(bank, pdf_path, pdf_password, start_date,
                                                                         end_date)
            self.progress_function(self.current_progress, self.total_progress,
                                   info=f"Extraction completed successfully")
            self.current_progress += 1
            print(f"Extracted {bank} bank statement successfully")
            self.account_number += f"{name_dfs[bank][1][:4]}x{name_dfs[bank][1][-4:]}_"
            i += 1

        print("|------------------------------|")
        print(self.account_number)
        print("|------------------------------|")

        single_df = self.atser.single_person_sheets(dfs, name_dfs)
        cummalative_df = self.atser.cummalative_person_sheets(single_df)
        # print(cummalative_df)

        # TODO: Save the excel file
        # cummalative_df.to_excel("src/data/cummalative_df.xlsx")

        folder_path = "saved_pdf"
        try:
            shutil.rmtree(folder_path)
            print(f"Removed all contents in '{folder_path}'")
        except Exception as e:
            print(f"Failed to remove '{folder_path}': {e}")

        # return (self.account_number, self.current_progress)
        return {"single_df":single_df, "cummalative_df":cummalative_df}

### --------------------------------------------------------------------------------------------------------- ###
#
# settings.configure(USE_TZ=True)
# bank_names = ["hdfc"]
# pdf_paths = ["hdfc.xlsx"]
# passwords = [""]
# start_date = ["1/04/2022"]
# end_date = ["31/03/2022"]
# CA_ID = "hdfc"
# progress_data = {
#     'progress_func': lambda current, total, info: print(f"{info} ({current}/{total})"),
#     'current_progress': 10,
#     'total_progress': 100
# }

# converter = CABankStatement(bank_names, pdf_paths, passwords, start_date, end_date, CA_ID, progress_data)
# converter.start_extraction()