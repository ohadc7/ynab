#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv
from pathlib import Path

import xlrd
import os
import io
from Parse_Leumi_Card import parse_leumi_card_data
from Parse_Leumi import parse_leumi_data

LEUMI = 1
LEUMI_CARD = 2


def csv_from_excel(path):
    for subdir, dirs, files in os.walk(path):
        for file_name in files:
            if "out" in subdir:
                continue
            Path(subdir + "\\out").mkdir(parents=True, exist_ok=True)
            if "Leumi_Card" in subdir:
                source = LEUMI_CARD
            else:
                source = LEUMI
            file_path = subdir + os.sep + file_name
            wb = xlrd.open_workbook(file_path)
            for sheet in wb.sheets():
                labels = ["Date", "Payee", "Outflow", "Memo", "Inflow"]
                clean_sheet_name = sheet.name.replace('"', '')
                if source == LEUMI_CARD:
                    clean_sheet_name += " - " + sheet.row(1)[0].value + " - " + sheet.row(2)[0].value.replace("/", "-")
                with io.open(subdir + "\\out\\" + clean_sheet_name + ".csv", 'w', encoding="utf-8") as csv_output:
                    for label in labels:
                        csv_output.write(label + ",")
                    csv_output.write("\n\r")
                    for row in range(4, sheet.nrows):
                        if sheet.row(row)[0].value != "":
                            if source == LEUMI_CARD:
                                line_buff = parse_leumi_card_data(sheet.row(row))
                            else:
                                line_buff = parse_leumi_data(sheet.row(row), wb)
                            csv_output.write(line_buff + "\n\r")


def main():
    csv_from_excel(argv[1])


if __name__ == "__main__":
    main()
