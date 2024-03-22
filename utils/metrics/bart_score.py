"""
This code calculates BARTscore.
The metric was introduced in NeurIPS 2021. Paper: https://arxiv.org/pdf/2106.11520.pdf
The code was adjusted from the official code in: https://github.com/neulab/BARTScore (Apache 2.0 license: https://github.com/neulab/BARTScore/blob/main/LICENSE)
"""
from transformers import BartTokenizer, BartForConditionalGeneration
import torch
import torch.nn as nn
import traceback
from typing import List
import numpy as np
import json
from os import listdir
from os.path import isfile, join


class BARTScorer:
    def __init__(self, device='cuda:0', max_length=1024, checkpoint='facebook/bart-large-cnn'):
        # Set up model
        self.device = device
        self.max_length = max_length
        self.tokenizer = BartTokenizer.from_pretrained(checkpoint)
        self.model = BartForConditionalGeneration.from_pretrained(checkpoint)
        self.model.eval()
        self.model.to(device)

        # Set up loss
        self.loss_fct = nn.NLLLoss(reduction='none', ignore_index=self.model.config.pad_token_id)
        self.lsm = nn.LogSoftmax(dim=1)

    def load(self, path=None):
        """ Load model from paraphrase finetuning """
        if path is None:
            path = 'models/bart.pth'
        self.model.load_state_dict(torch.load(path, map_location=self.device))

    def score(self, srcs, tgts, batch_size=4):
        """ Score a batch of examples """
        score_list = []
        for i in range(0, len(srcs), batch_size):
            src_list = srcs[i: i + batch_size]
            tgt_list = tgts[i: i + batch_size]
            try:
                with torch.no_grad():
                    encoded_src = self.tokenizer(
                        src_list,
                        max_length=self.max_length,
                        truncation=True,
                        padding=True,
                        return_tensors='pt'
                    )
                    encoded_tgt = self.tokenizer(
                        tgt_list,
                        max_length=self.max_length,
                        truncation=True,
                        padding=True,
                        return_tensors='pt'
                    )
                    src_tokens = encoded_src['input_ids'].to(self.device)
                    src_mask = encoded_src['attention_mask'].to(self.device)

                    tgt_tokens = encoded_tgt['input_ids'].to(self.device)
                    tgt_mask = encoded_tgt['attention_mask']
                    tgt_len = tgt_mask.sum(dim=1).to(self.device)

                    output = self.model(
                        input_ids=src_tokens,
                        attention_mask=src_mask,
                        labels=tgt_tokens
                    )
                    logits = output.logits.view(-1, self.model.config.vocab_size)
                    loss = self.loss_fct(self.lsm(logits), tgt_tokens.view(-1))
                    loss = loss.view(tgt_tokens.shape[0], -1)
                    loss = loss.sum(dim=1) / tgt_len
                    curr_score_list = [-x.item() for x in loss]
                    score_list += curr_score_list

            except RuntimeError:
                traceback.print_exc()
                print(f'source: {src_list}')
                print(f'target: {tgt_list}')
                exit(0)
        return score_list


def calculate_bartscore(tmp_json_files, models_scores, path_to_finetuned_bart):
    if torch.cuda.is_available():
        device = 'cuda:0'
    else:
        device = 'cpu'
        
    bart_scorer = BARTScorer(device=device, checkpoint='facebook/bart-large-cnn')
    if len(path_to_finetuned_bart)>0:
        bart_scorer.load(path=path_to_finetuned_bart)
    scores_dict = dict()

    for result_file in listdir(tmp_json_files):
        if not result_file.endswith("_metrics.jsonl"):
            continue

        model = result_file.replace("_metrics.jsonl", "")
        scores_dict[model] = []
        data = []

        filename = join(tmp_json_files, result_file)

        with open(filename, "r") as file:
            for line in file:
                data.append(json.loads(line))

        print(f"Evaluating {model} model")


        processed_samples_ctr = 0
        
        for sample in data:
            model_output = sample['model_output'].strip()
            target_output = sample['target_output'].strip()
            score = bart_scorer.score([model_output], [target_output])[0]
            scores_dict[model].append(score)
            sample['scores'].append({'name': 'bartscore', 'value': score})
            
            processed_samples_ctr += 1
            if processed_samples_ctr % 10 == 0:
                print(f"Processed {processed_samples_ctr}/{len(data)} samples.")
        
        # dump the new metric to appear in the the output view dashboard
        with open(filename, 'w') as outfile:
            for entry in data:
                json.dump(entry, outfile)
                outfile.write('\n')
        
        # update the models_score to appear in the index.html leaderboard
        current_metrics = models_scores[model]
        current_metrics['bartscore'] = np.average(scores_dict[model])
        models_scores[model] = current_metrics
        
    