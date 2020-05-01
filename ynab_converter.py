#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv

import xlrd
import os
import datetime
import io


def parse_leumi_data(row, wb):
    line_buffer = ""
    valid_cols = [0, 1, 3, 4]
    for col, col_value in enumerate(row):
        if col in valid_cols:
            if col == 0:
                date_tuple = xlrd.xldate_as_tuple(col_value.value, wb.datemode)
                value = datetime.datetime(*date_tuple).strftime('%d/%m/%Y')
                line_buffer += value + ","
            elif col == 3:
                value = str(col_value.value)
                line_buffer += value + ",,"
            else:
                value = str(col_value.value)
                line_buffer += value + ","
        if col > max(valid_cols):
            break
    return line_buffer


def parse_leumi_card_data(row):
    line_buffer = ""
    valid_cols = [0, 1, 5, 10]
    for col, col_value in enumerate(row):
        if col in valid_cols:
            value = col_value.value
            if col == 5:
                value = str(value)
            line_buffer += value + ","
        if col > max(valid_cols):
            break
    return line_buffer


def csv_from_excel(leumi_card, path):
    for subdir, dirs, files in os.walk(path):
        for file_name in files:
            if not file_name.endswith("csv"):
                file_path = subdir + os.sep + file_name
                wb = xlrd.open_workbook(file_path)
                for sheet in wb.sheets():
                    labels = ["Date", "Payee", "Outflow", "Memo", "Inflow"]
                    clean_sheet_name = sheet.name.replace('"', '')
                    if leumi_card:
                        clean_sheet_name += " - " + sheet.row(1)[0].value + " - " + sheet.row(2)[0].value.replace("/", "-")
                    with io.open(path + "\\" + clean_sheet_name + ".csv", 'w', encoding="utf-8") as csv_output:
                        for label in labels:
                            csv_output.write(label + ",")
                        csv_output.write("\n\r")
                        for row in range(4, sheet.nrows):
                            if sheet.row(row)[0].value != "":
                                if leumi_card:
                                    line_buff = parse_leumi_card_data(sheet.row(row))
                                else:
                                    line_buff = parse_leumi_data(sheet.row(row), wb)
                                csv_output.write(line_buff + "\n\r")


def main():
    csv_from_excel(int(argv[1]), argv[2])


if __name__ == "__main__":
    main()
