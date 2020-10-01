# -*- coding: utf-8 -*-


class Parsers:

    def __init__(self, valid_cols):
        self.valid_cols = valid_cols

    def parse_leumi_data(self, row):
        line_buffer: str = ""
        for col, col_value in enumerate(row):
            if col in self.valid_cols:
                if col == 1:
                    day = col_value[0:2]
                    month = col_value[2:4]
                    year = int(col_value[4:6]) + 2000
                    line_buffer += str(year) + "-" + month + "-" + day + ","
                if col == 2:
                    line_buffer += ''.join(reversed(col_value)) + ","
                if col == 3:
                    if col_value.startswith("-"):
                        line_buffer += col_value[1:] + ","
                    else:
                        line_buffer += ", , " + col_value + ","
        comma_count = line_buffer.count(",")
        while comma_count < 5:
            line_buffer += ","
            comma_count += 1
        return line_buffer

    def parse_max_data(self, row):
        line_buffer = ""
        for col, col_value in enumerate(row):
            if col in self.valid_cols:
                if col == 0:
                    day, month, year = col_value.value.split("-")
                    value = year + "-" + month + "-" + day
                else:
                    value = col_value.value
                if col == 5:
                    value = str(value)
                line_buffer += value + ","
            if col > max(self.valid_cols):
                break
        return line_buffer
