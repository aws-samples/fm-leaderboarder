import json
import pandas as pd
from os import listdir
from os.path import isfile, join

def create_response_output_view(result_html_folder, tmp_json_files, models_scores):
    models_run = list(models_scores.keys())
    if len(models_run) > 0:
        metrics_used = list(models_scores[models_run[0]].keys())
    
    for model_id, scores in models_scores.items():
        title = f'Model [{model_id}] - testset results'
        # generate headers name
        headers = ['Model input', 'Model output', 'Target Output']
        for mu in metrics_used:
            headers.append(mu)

        model_json_filename = f"{tmp_json_files}/{model_id}_metrics.jsonl"
        data = []
        with open(model_json_filename, "r") as file:
            for line in file:
                data.append(json.loads(line))

        df = pd.DataFrame(data)
        for idx, mu in enumerate(metrics_used):
            df[mu] = df['scores'].apply(lambda x: x[idx]['value'])

        # generate row data
        rows = []
        for index, item in df.iterrows():
            row = [item['prompt'], item['model_output'], item['target_output']]        
            for mu in metrics_used:
                row.append(item[mu])
            rows.append(row)
        
        with open(f"{result_html_folder}/{model_id}_results.html", "w", encoding='utf-8-sig') as file:
            from .dashboard_template import generate_dashboard_string
            file.write(generate_dashboard_string(title = title, column_names = headers, rows = rows))