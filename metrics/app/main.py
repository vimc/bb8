#!/usr/bin/env python3
from flask import Flask

from subprocess import check_output
from metrics import render_metrics, target_metrics

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    bb8_status = check_output(["bb8", "status", "--json"]).decode('utf-8')
    metrics = target_metrics(bb8_status)
    return render_metrics(metrics)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)