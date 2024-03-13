import json
from os import listdir
from os.path import isfile, join


def create_main_html(result_folder, models_scores):
    model_outputs = dict()
    test_samples = []

    title = 'Summarization Evaluation'

    pre_table_html = """ 
        <a href="html_files/test_samples.html">Test set snapshot</a><br>
        <p>
            <u>Data statistics:</u><br>
            <img src="imgs/dataset_stats.png" width="30%">
        </p><br>
        <p>
        <u>Insights:</u>
        <ul>
            <li>Dataset used for the evaluation is <a href=https://aclanthology.org/2021.findings-emnlp.24.pdf>TWEETSUMM</a> (published in EMNLP 2021) - a customer/agent conversation summarization task</li>
            <li>Metric details:
            <ul>
                <li>Word matching metrics (<a href=https://en.wikipedia.org/wiki/METEOR#:~:text=METEOR%20(Metric%20for%20Evaluation%20of,recall%20weighted%20higher%20than%20precision.>METEOR</a> <a href=https://en.wikipedia.org/wiki/ROUGE_(metric)>ROUGE</a>) - based on precision and recall of overlapping N-Grams. Higer value indicates superior generation capabilities.</li>
                <li>Semantic word matching metric (<a href=https://arxiv.org/pdf/1904.09675.pdf>BERTscore</a>) - based on semantical representations matching. Higer value indicates superior generation capabilities.</li>
                <li>Textual generation evaluation (<a href=https://arxiv.org/pdf/2106.11520.pdf>BARTscore</a>) - based on pretrained BART model. A number closer to 0 indicates a better model.</li>
            </ul>
            </li>
            <li>None of the prompts was optimized for any specific model. The prompt is shared across models with minimal modification for adjusting to model's requirements.</li>
            <li>If you wish to check hallucinations by the model, consider the following method from Amazon Science - <a href=https://github.com/amazon-science/RefChecker?tab=readme-ov-file>RefChecker</a></li>
        </ul>
        </p>
        <p>
            <u>Results</u> <a href="html_files/output_comparison.html">(response comparison dashboard)</a>: <br>
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
