from collections import defaultdict

def create_model_ranking(models_scores:dict):
    model_ranking = defaultdict(int)
    totals = len(models_scores) * len(list(models_scores.values())[0])
    # Iterate over the metrics
    metrics = set()
    for model_id in models_scores:
        metrics.update(models_scores[model_id].keys())

    for metric in metrics:
        # Sort the models for the current metric
        sorted_models = sorted(
            [(model_id, models_scores[model_id][metric]) for model_id in models_scores if metric in models_scores[model_id]],
            key=lambda x: x[1],
            reverse=False
        )

        # Assign points to the models based on their ranking for the current metric
        for rank, (model_id, _) in enumerate(sorted_models, start=1):
            model_ranking[model_id] += rank / totals

    # Sort the models based on their total points
    return model_ranking

    for rank, (model_id, total_points) in enumerate(sorted_model_ranking, start=1):
        ret[model_id] = rank

    return ret
