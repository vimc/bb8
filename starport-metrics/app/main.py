#!/usr/bin/env python3
from flask import Flask
import json
import os
from metrics.metrics import render_metrics, label_metrics, parse_timestamp, seconds_elapsed_since

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    return render_metrics(build_target_metrics("/starport"))


def build_target_metrics(starport):
    targets = os.listdir(starport)
    metrics = {"number_of_targets": len(targets)}
    for target in targets:
        try:
            with open(os.path.join(starport, target, "meta", "metadata.json")) as json_data:
                data = json.load(json_data)
                last_backup = parse_timestamp(data["last_backup"])
                since_last_backup = seconds_elapsed_since(last_backup)
                item_metrics = {
                    "metadata_present": True,
                    "time_since_last_backup_seconds": round(since_last_backup),
                    "time_since_last_backup_minutes": round(since_last_backup / 60),
                    "time_since_last_backup_hours": round(since_last_backup / 3600),
                    "time_since_last_backup_days": round(since_last_backup / (3600*24))
                }

                item_metrics = label_metrics(item_metrics, {"target_id": target})
                metrics.update(item_metrics)
        except Exception as e:
            print(e)
            item_metrics = {"metadata_present": False}
            item_metrics = label_metrics(item_metrics, {"target_id": target})
            metrics.update(item_metrics)
    return metrics
