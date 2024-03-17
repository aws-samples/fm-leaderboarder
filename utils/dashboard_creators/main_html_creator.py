import json
from os import listdir
from os.path import isfile, join


def create_main_html(result_folder, models_scores):
    model_outputs = dict()
    test_samples = []

    title = 'Summarization Evaluation'

    pre_table_html = """ 
<ul>
    <li><a href="html_files/test_samples.html">Your testset</a></li>
    <li>Testset statistics:<br/>
        <img src="imgs/dataset_stats.png" width="30%">
    </li>
    <li><a href="html_files/output_comparison.html">Side-by-side model responses</a></li>
</ul>

<h2>Leaderboard</h2>
Note you can sort columns and search by a keyword to filter
    """

  # generate headers name
    headers = ['Model']
    models_run = list(models_scores.keys())
    if len(models_run) > 0:
        metrics_used = list(models_scores[models_run[0]].keys())
        for mu in metrics_used:
            headers.append(f'Metric: {mu}')

    # generate row data
    rows = []
    for model_id, scores in models_scores.items():
        row = [f'<a href="html_files/{model_id}_results.html">{model_id}</a>']
        for mu in metrics_used:
            row.append("{:.4f}".format(scores[mu]))
        rows.append(row)

    index_filename = f"{result_folder}/index.html"
    with open(index_filename, "w", encoding='utf-8-sig') as file:
        from .dashboard_template import generate_dashboard_string
        file.write(generate_dashboard_string(title = title, pre_table_html = pre_table_html, column_names = headers, rows = rows))

    return index_filename
