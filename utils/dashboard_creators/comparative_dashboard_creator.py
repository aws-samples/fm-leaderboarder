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

    models = list(model_outputs.keys())


    # generate headers name
    headers = ['Model input', 'Target output']
    for m_name in models:
        headers.append(m_name)

    # generate row data
    rows = []
    for samples in test_samples:
        row = [samples[0], samples[1]]
        for m_name in models:
            row.append(model_outputs[m_name][samples[1]])
        rows.append(row)

    with open(f"{result_html_folder}/output_comparison.html", "w", encoding='utf-8-sig') as file:
        from .dashboard_template import generate_dashboard_string
        file.write(generate_dashboard_string(headers, rows))