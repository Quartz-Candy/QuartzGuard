

def create_table(data, column=4):
    table_html = ['<table class="customTable has-fixed-layout" style="width:100%; table-layout:fixed; border-collapse:collapse;">']

    entry_counter = 0
    row_html = ""
    for stat in data:
        # rewrite to be just {stat}
        row_html += f'<td>{stat[0]}: {stat[1]}</td>'
        entry_counter += 1

        if entry_counter >= column:
            table_html.append(f'<tr>{row_html}</tr>')
            entry_counter = 0
            row_html = ""

    table_html.append('</tbody></table><hr>')

    return "".join(table_html)