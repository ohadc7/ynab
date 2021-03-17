# -*- coding: utf-8 -*-

import configparser
import io
import os
import sys
from datetime import date, timedelta
from pathlib import Path
import xlrd
from parsers import Parsers


class Utils:
    def __init__(self, transactions):
        self._dir_path = None
        self.make_new_dir()
        self._config = None
        self.init_config()
        self.tx_data = {"transactions": []}
        self.transactions = transactions

    @property
    def config(self):
        return self._config

    @property
    def dir_path(self):
        return self._dir_path

    def init_config(self):
        self._config = configparser.ConfigParser()
        self._config.read('../payload_data.ini')

    @staticmethod
    def create_csv_files(path, file_name):
        labels = ["Date", "Payee", "Outflow", "Memo", "Inflow"]
        csv_output = io.open(os.getcwd() + "\\" + path + "\\out\\" + file_name + ".csv", 'w', encoding="utf-8")
        for label in labels:
            csv_output.write(label + ",")
        csv_output.write("\n\r")
        return csv_output

    def make_new_dir(self):
        last_month = date.today().replace(day=1) - timedelta(days=1)
        self._dir_path = str(last_month.month) + "." + str(last_month.year)
        Path(self.dir_path).mkdir(parents=True, exist_ok=True)

    def get_tx_data(self):
        return self.tx_data

    def csv_from_excel(self, data):

        for subdir, dirs, files in os.walk(self.dir_path):
            for file_name in files:
                if "out" in subdir:
                    continue
                Path(subdir + "\\out").mkdir(parents=True, exist_ok=True)
                file_path = subdir + os.sep + file_name
                if "max" in subdir:
                    wb = xlrd.open_workbook(file_path)
                    for sheet in wb.sheets():
                        if "עסקאות שאושרו וטרם נקלטו" in sheet.name:
                            continue
                        clean_sheet_name = sheet.name.replace('"', '')
                        clean_sheet_name += " - " + sheet.row(1)[0].value + " - " + sheet.row(2)[0].value.replace("/",
                                                                                                                  "-")
                        account = data["data_cache"]["ohad_credit_card"]
                        csv_output = self.create_csv_files(subdir, clean_sheet_name)
                        parser = Parsers(valid_cols=[0, 1, 5, 10])
                        for row in range(4, sheet.nrows):
                            if sheet.row(row)[0].value != "":
                                line_buff = parser.parse_max_data(sheet.row(row))
                                csv_output.write(line_buff + "\n\r")
                                self.tx_data["transactions"] = \
                                    self.transactions.convert_csv_line_to_transaction(self.tx_data["transactions"],
                                                                                      line_buff, account)

                elif 'leumi' in subdir:
                    with open(file_path, "r", encoding='cp862') as dat_file:
                        lines_list = dat_file.readlines()
                        split_lines = [x.split(",") for x in lines_list]
                        csv_output = self.create_csv_files(subdir, "leumi")
                        account = data["data_cache"]["leumi_account_id"]
                        parser = Parsers(valid_cols=[1, 2, 3])
                        for row in split_lines:
                            line_buff = parser.parse_leumi_data(row)
                            csv_output.write(line_buff + "\n\r")
                            self.tx_data["transactions"] = self.transactions.convert_csv_line_to_transaction(
                                self.tx_data["transactions"], line_buff, account)
                else:
                    wb = xlrd.open_workbook(file_path)
                    for sheet in wb.sheets():
                        account = data["data_cache"]["shlomit_credit_card"]
                        csv_output = self.create_csv_files(subdir, sheet.name)
                        parser = Parsers(valid_cols=[0, 1, 4, 7])
                        # TODO: add the starting relevant number to payload_data
                        for row in range(6, sheet.nrows):
                            if sheet.row(row)[0].value != "":
                                line_buff = parser.parse_isracard_data(sheet.row(row))
                                csv_output.write(line_buff + "\n\r")
                                self.tx_data["transactions"] = \
                                    self.transactions.convert_csv_line_to_transaction(self.tx_data["transactions"],
                                                                                      line_buff, account)

    @staticmethod
    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, "resources", relative_path)
