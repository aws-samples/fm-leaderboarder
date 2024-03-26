import json
from os import listdir
from os.path import isfile, join

from utils.model_runners.pricing_calculator import PricingCalculator


def create_main_html(result_folder, models_scores, model_usage, model_ranking):
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

<h2>
    Leaderboard
    <span class="tooltip">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        <span class="tooltiptext">You can sort by columns and search by a keyword to filter</span>
      </span>
</h2>

<div id="legend">
  Legend: 
  <span style="background-color: darkgreen; color: white; padding: 2px 5px;">1st Best Result</span>
  <span style="background-color: green; color: white; padding: 2px 5px;">2nd Best Result</span>
  <span style="background-color: lightgreen; padding: 2px 5px;">3rd Best Result</span>
</div>

    """

  # generate headers name
    headers = ['Model']
    models_run = list(models_scores.keys())
    headers.append('Win Rate')
    if len(models_run) > 0:
        metrics_used = list(models_scores[models_run[0]].keys())
        for mu in metrics_used:
            headers.append(f'Metric: {mu}')
    headers.append('Total Costs ($)')
    headers.append('Latency (s)')
    headers.append('cost/1MT In ($)')
    headers.append('cost/1MT Out ($)')
    
    # generate row data
    rows = []
    for model_id, scores in models_scores.items():
        row = [f'<a href="html_files/{model_id}_results.html">{model_id}</a>']
        row.append("{:.3f}".format(model_ranking[model_id]) )
        for mu in metrics_used:
            row.append("{:.4f}".format(scores[mu]))
        if model_id in model_usage and model_usage[model_id] is not None and model_usage[model_id]['cost_model'] == PricingCalculator.COST_PER_TOKEN:
            row.append("{:.2f}".format(model_usage[model_id]['cost']))        
            row.append("{:.2f}".format(model_usage[model_id]['processing_time']))
            row.append("{:.4f}".format(model_usage[model_id]['cost_input_1M']))
            row.append("{:.4f}".format(model_usage[model_id]['cost_output_1M']))
        else:
            row.append('-')
            row.append('-')
            row.append('-')
            row.append('-')
        rows.append(row)
        
    index_filename = f"{result_folder}/index.html"

    with open(index_filename, "w", encoding='utf-8-sig') as file:
        from .dashboard_template import generate_dashboard_string
        file.write(generate_dashboard_string(title = title, pre_table_html = pre_table_html, column_names = headers, rows = rows))

    # CSS
    # copy CSS file from ./static/styles.css to the result folder
    # get current python file folder
    import os
    import shutil
    shutil.copyfile(f'{os.path.dirname(os.path.abspath(__file__))}/static/styles.css', f'{result_folder}/styles.css')

    return index_filename
