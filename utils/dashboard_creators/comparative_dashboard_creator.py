import json
from os import listdir
from os.path import isfile, join


def create_comparive_dashboard(result_html_folder, tmp_json_files):
    model_outputs = dict()
    test_samples = []

    for result_file in listdir(tmp_json_files):
        if not result_file.endswith("_metrics.jsonl"):
            continue

        model = result_file.replace("_metrics.jsonl", "")

        model_outputs[model] = dict()

        data = []
        filename = join(tmp_json_files, result_file)
        with open(filename, "r") as file:
            for line in file:
                data.append(json.loads(line))

        if len(test_samples) == 0:
            for d in data:
                test_samples.append((d['model_input'], d['target_output']))

        for d in data:
            model_outputs[model][d['target_output']] = d['model_output']

    colors = ['#CEFED7', '#CEF9FE']
    file = open(f"{result_html_folder}/output_comparison.html", "w", encoding='utf-8-sig')
    models = list(model_outputs.keys())

    file.write("<html>")
    file.write("<head>")
    file.write("<title>Results comparison</title>")
    file.write("</head>")
    file.write("<body>")
    file.write(f"<h1>Results Comparison</h1>")
    file.write("<table align=center><tr><th bgcolor = navy><font color=white>Model input</font></th>"
               "<th bgcolor = navy><font color=white>GT</font></th>")
    for m_name in models:
        file.write(f"<th bgcolor = navy><font color=white>{m_name}</font></th>")
    file.write("</tr>")

    index = 0
    for samples in test_samples:
        index += 1
        c = colors[index%2]

        file.write(f"<tr><td bgcolor={c}>{samples[0]}</td>"
                   f"<td bgcolor={c}>{samples[1]}</td>")
        for m_name in models:
            file.write(f"<td bgcolor={c}>{model_outputs[m_name][samples[1]]}</td>")
        file.write("</tr>")

    file.write("</table>")
    file.write("</body>")
    file.write("</html>")

    file.close()