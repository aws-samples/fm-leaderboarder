import json
import pandas as pd
from os import listdir
from os.path import isfile, join

def create_response_output_view(result_html_folder, tmp_json_files, models_scores):
    models_run = list(models_scores.keys())
    if len(models_run) > 0:
        metrics_used = list(models_scores[models_run[0]].keys())
    
    for model_id, scores in models_scores.items():
        model_json_filename = f"{tmp_json_files}/{model_id}_metrics.jsonl"
        data = []
        with open(model_json_filename, "r") as file:
            for line in file:
                data.append(json.loads(line))

        df = pd.DataFrame(data)
        print(metrics_used)
        for idx, mu in enumerate(metrics_used):
            df[mu] = df['scores'].apply(lambda x: x[idx]['value'])

        colors = ['#CEFED7', '#CEF9FE']
        file = open(f"{result_html_folder}/{model_id}_results.html", "w", encoding='utf-8-sig')

        file.write("<html>")
        file.write("<head>")
        file.write("<title>Test samples analysis</title>")
        file.write("</head>")
        file.write("<body>")
        file.write(f"<h1>{model_id} -  test samples analysis</h1>")
        file.write("<table align=center><tr><th bgcolor = navy><font color=white>Model input</font></th>"
                   "<th bgcolor = navy><font color=white>Model output</font></th>"
                   "<th bgcolor = navy><font color=white>Target output</font></th>")
        for mu in metrics_used:
            file.write(f"<th bgcolor = navy><font color=white>{mu}</font></th>")
        file.write("</tr>")

        for index, row in df.iterrows():
            c = colors[index%2]
            p = row['prompt'].replace("\n","<br>").replace("<s>","").replace("</s>","")
            m = row['model_output'].replace("\n", "<br>").replace("<s>","").replace("</s>","")
            t = row['target_output'].replace("\n", "<br>").replace("<s>","").replace("</s>","")
            file.write(f"<tr><td bgcolor={c}>{p}</td>"
                       f"<td bgcolor={c}>{m}</td>"
                       f"<td bgcolor={c}>{t}</td>")
            
            for mu in metrics_used:
                file.write(f"<td bgcolor={c}>{row[mu]}</td>")
        file.write("</table>")
        file.write("</body>")
        file.write("</html>")

        file.close()