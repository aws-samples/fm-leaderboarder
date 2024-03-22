from collections import defaultdict

def create_model_ranking(models_scores):
    model_ranking = defaultdict(int)

    # Iterate over the metrics
    metrics = set()
    for model_id in models_scores:
        metrics.update(models_scores[model_id].keys())

    for metric in metrics:
        # Sort the models for the current metric
        sorted_models = sorted(
            [(model_id, models_scores[model_id][metric]) for model_id in models_scores if metric in models_scores[model_id]],
            key=lambda x: x[1],
            reverse=True
        )

        # Assign points to the models based on their ranking for the current metric
        for rank, (model_id, _) in enumerate(sorted_models, start=1):
            model_ranking[model_id] += rank

    # Sort the models based on their total points
    sorted_model_ranking = sorted(model_ranking.items(), key=lambda x: x[1])
    ret = dict()
    # Print the model ranking
    for rank, (model_id, total_points) in enumerate(sorted_model_ranking, start=1):
        ret[model_id] = rank

    return ret
