import html

def generate_dashboard_string(title = 'page title', pre_table_html = "", column_names = [], rows = []):
    columns_html = ""
    for name in column_names:
        columns_html += f"<th>{html.escape(str(name))}</th>\n"

    table_data_html = ""
    for row in rows:
        table_data_html += f"<tr>\n"
        for item in row:
            str_item = str(item) # in case of a number
            if str_item.strip().startswith("<a href"): # temp workaround
                escaped_item = str_item
            else:
                escaped_item = html.escape(str_item)
            table_data_html += f"<td>{escaped_item}</td>\n"
        table_data_html += "</tr>\n"

    args = {'title' : html.escape(str(title)), 'pre_table_html' : pre_table_html, 'columns_html' : columns_html, 'table_data_html' :table_data_html}

    return '''
<html>
<link rel="stylesheet" href="https://cdn.datatables.net/2.0.1/css/dataTables.dataTables.css" />
<head>
<title>{title}</title>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.7.1/jquery.min.js"></script>
<script src="https://cdn.datatables.net/2.0.1/js/dataTables.js"></script>
<script>
    $(document).ready( function () {{
        $('#myTable').DataTable({{
            "pageLength": 500,
            initComplete: function() {{
                var api = this.api();

                api.columns(':not(:first)').every(function() {{
                    // get sorted list
                    var col = this.index();
                    var data = this.data().unique().map(function(value) {{
                      return parseFloat(value);
                    }})
                    .toArray()
                    .sort(function(a, b){{return b-a}});

                    // paint top K results
                    api.cells(null, col).every( function() {{
                      var cell = parseFloat(this.data());
                      if (cell === data[0]) {{
                        $(this.node()).css('background-color', 'Green')
                      }}
                      else if (cell === data[1]) {{
                        $(this.node()).css('background-color', 'Orange')
                      }}
                    }});
                }});
            }}
        }});
    }});
</script>
</head>
<body>
<h1>{title}</h1>
{pre_table_html}
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

# testcases
def test_generate_dashboard_string():
    print(generate_dashboard_string(title = 'mytitle', column_names = ["a", "b"], rows = [[1, 2], [3, 4]]))
    print(generate_dashboard_string(title = 'mytitle', pre_table_html= "<div>1</div>", column_names = ["a", "b"], rows = [[1, 2], [3, 4]]))
    print(generate_dashboard_string(column_names = ["a", "b"], rows = [['<a href="..">link</a>', 2], [3, 4]]))


#test_generate_dashboard_string()