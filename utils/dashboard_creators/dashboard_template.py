def generate_dashboard_string(columns_name, rows):
    columns_html = ""
    for name in columns_name:
        columns_html += f"<th>{name}</th>\n"

    table_data_html = ""
    for row in rows:
        table_data_html += f"<tr>\n"
        for item in row:
            table_data_html += f"<td>{item}</td>\n"
        table_data_html += "</tr>\n"

    args = {'columns_html' : columns_html, 'table_data_html' :table_data_html}

    return '''
<html>
<link rel="stylesheet" href="https://cdn.datatables.net/2.0.1/css/dataTables.dataTables.css" />
<head>
<title>Results comparison</title>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script src="https://cdn.datatables.net/2.0.1/js/dataTables.js"></script>
<script>
    $(document).ready( function () {{
        $('#myTable').DataTable({{
            "pageLength": 500
        }});
    }})
</script>
</head>
<body>
<h1>Results Comparison</h1>
<table id="myTable" class="cell-border hover order-column stripe" align="left">
<thead>
<tr>
{columns_html}
</tr>
</thead>
<tbody>
{table_data_html}
</tbody>
</table>
</body>
</html>
    '''.format(**args)

#print(generate_dashboard_string(["a", "b"], [[1, 2], [3, 4]]))