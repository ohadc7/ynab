import datetime
import xlrd


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
