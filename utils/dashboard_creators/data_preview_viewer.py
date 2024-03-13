from datasets import load_dataset
import re
import json
from unicodedata import normalize

def create_data_preview_view(test_file_path, result_html_folder):

    with open(test_file_path, 'r') as json_file:
        json_list = list(json_file)

    # generate headers name
    headers = ['Input', 'Ground Truth']

    # generate row data
    rows = []
    for json_str in json_list:
        result = json.loads(json_str)
        row = [result['document'], result['summary']]
        rows.append(row)
    
    with open(f"{result_html_folder}/test_samples.html", "w", encoding='utf-8-sig') as file:
        from .dashboard_template import generate_dashboard_string
        file.write(generate_dashboard_string(title = "", column_names=headers, rows = rows))
