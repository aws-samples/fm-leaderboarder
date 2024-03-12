import json
from os import listdir
from os.path import isfile, join


def create_main_html(result_folder, models_scores):
    model_outputs = dict()
    test_samples = []

    filename = f"{result_folder}/index.html"
    file = open(filename, "w", encoding='utf-8-sig')

    html_header = f""" 
    <!DOCTYPE html>
    <html lang="en" xmlns="http://www.w3.org/1999/html">
    <head>
        <meta charset="UTF-8">
        <title>NLG Evaluation</title>
    </head>
    <body>
        <h1 align="center">NLG Evaluation</h1>

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
            <table align="left" width="80%">
                <tr>
                    <th bgcolor="navy"><font color="white">Model</font></th>
    """


    file.write(html_header)

    models_run = list(models_scores.keys())
    if len(models_run) > 0:
        metrics_used = list(models_scores[models_run[0]].keys())
        for mu in metrics_used:
            file.write(f"<th bgcolor=navy><font color=white>{mu}</font></th>")

    file.write("</tr>")


    for model_id, scores in models_scores.items():
        row_str = f"""
            <tr>
                <td bgcolor="#faebd7"><a href="html_files/{model_id}_results.html">{model_id}</a></td>
                """
        file.write(row_str)
        for mu in metrics_used:
            file.write("<td>")
            file.write("{:.4f}".format(scores[mu]))
            file.write("</td>")
        file.write("</tr>")

    html_suffix = """
            </table>
        </p>
    </body>
    </html>

    """
    file.write(html_suffix)

    file.close()
    return filename
