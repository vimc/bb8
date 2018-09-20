#!/usr/bin/env python3
from flask import Flask

from subprocess import check_output
from metrics.metrics import render_metrics, label_metrics
import json

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    bb8_status = check_output(["bb8", "status", "--json"]).decode('utf-8')
    return render_metrics(build_target_metrics(bb8_status))


def build_target_metrics(bb8_status):
    metrics = {}
    targets = json.loads(bb8_status)
    for target in targets:
        item_metrics = {"last_backup": target["last_backup"]}
        item_metrics = label_metrics(item_metrics, {"target_id": target["target"]})
        metrics.update(item_metrics)
    return metrics

