import html

def get_optional_tooltip_html(name : str):
    tips_by_metric = { 
        "meteor" : "METEOR is a metric for text similarity between the machine-produced summary and human-produced reference summaries.",
        "rouge" : "The ROUGE metric measures text similarity by computing overlapping n-grams between a machine-generated text and one or more reference human-written texts.",
        "bertscore" : "The BERTScore is a text similarity metric that leverages BERT's contextual embeddings to compute token similarities between the candidate and reference texts.",
        "bartscore" : "",
    }
    if name.lower().startswith("metric:"):
        metric_name = name.lower().split(' ')[-1]
        if metric_name in tips_by_metric:  
            tip = tips_by_metric[metric_name]             
            tooltip_html ='''
                <span class="tooltip">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                    <span class="tooltiptext">{}</span>
                </span>
            '''.format(tip)
            return tooltip_html
    return ""
            

def generate_dashboard_string(title = 'page title', pre_table_html = "", column_names = [], rows = []):
    columns_html = ""
    for name in column_names:
        tooltip_html = get_optional_tooltip_html(str(name))
        columns_html += f"<th>{html.escape(str(name))}" + f"{tooltip_html}</th>\n"

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
<link rel="stylesheet" href="styles.css">
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
    print(generate_dashboard_string(column_names = ["Metric: meteor", "b"], rows = [['<a href="..">link</a>', 2], [3, 4]]))

#test_generate_dashboard_string()