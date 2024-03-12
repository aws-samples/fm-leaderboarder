from datasets import load_dataset
import re
import json
from unicodedata import normalize


def create_data_preview_view(test_file_path, result_html_folder):

    with open(test_file_path, 'r') as json_file:
        json_list = list(json_file)

    for json_str in json_list:
        result = json.loads(json_str)

    colors= ['#CEFED7','#CEF9FE']

    file = open(f"{result_html_folder}/test_samples.html", "w", encoding='utf-8-sig')

    # Write HTML content
    file.write("<html>")
    file.write("<head>")
    file.write("<title>Test samples</title>")
    file.write("</head>")
    file.write("<body>")
    file.write(f"<h1>Test samples</h1>")
    file.write("<table align=center><tr><th bgcolor = navy><font color=white>Input</font></th><th bgcolor = navy><font color=white>Ground Truth</font></th></tr>")
    i = 0
    for json_str in json_list:
        result = json.loads(json_str)
        i += 1
        if i < 100:
            c = colors[i%2]
            doc_txt = result['document'].replace("\n","<br>")
            summary_txt = result['summary'].replace("\n","<br>")
            file.write(f"<tr><td bgcolor={c}>{doc_txt}</td><td bgcolor={c}>{summary_txt}</td></tr>")
        else:
            break
    file.write("</table>")
    file.write("</body>")
    file.write("</html>")

    file.close()