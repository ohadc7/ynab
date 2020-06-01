def parse_leumi_data(row):
    line_buffer: str = ""
    valid_cols = [1, 2, 3]
    for col, col_value in enumerate(row):
        if col in valid_cols:
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
