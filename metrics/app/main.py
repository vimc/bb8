#!/usr/bin/env python3
from flask import Flask

from subprocess import check_output

app = Flask(__name__)


@app.route('/metrics')
def metrics():
    return check_output(["bb8", "status", "--json"])


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=5000)
