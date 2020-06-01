def parse_max_data(row):
    line_buffer = ""
    valid_cols = [0, 1, 5, 10]
    for col, col_value in enumerate(row):
        if col in valid_cols:
            if col == 0:
                day, month, year = col_value.value.split("-")
                value = year + "-" + month + "-" + day
            else:
                value = col_value.value
            if col == 5:
                value = str(value)
            line_buffer += value + ","
        if col > max(valid_cols):
            break
    return line_buffer
