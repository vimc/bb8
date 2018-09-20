#!/usr/bin/env python3
from flask import Flask
import json
import os
from metrics.metrics import render_metrics, label_metrics

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    return render_metrics(build_target_metrics("/starport"))


def build_target_metrics(starport):
    metrics = {}
    targets = os.listdir(starport)
    for target in targets:
        try:
            with open(os.path.join(starport, target, "meta", "metadata.json")) as json_data:
                d = json.load(json_data)
                item_metrics = label_metrics(d, {"target_id": target})
                metrics.update(item_metrics)
        except:
            item_metrics = {"missing_metadata": True}
            item_metrics = label_metrics(item_metrics, {"target_id": target})
            metrics.update(item_metrics)
    return metrics
