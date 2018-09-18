from flask import Response
import json
from metrics.metrics import label_metrics


def target_metrics(bb8_status):
    metrics = {}
    targets = json.loads(bb8_status)
    for target in targets:
        print(target)
        item_metrics = {"last_backup": target["last_backup"]}
        item_metrics = label_metrics(item_metrics, {"target_id": target["target"]})
        metrics.update(item_metrics)
    return metrics

