from flask import Response
import json

def render_value(value):
    if value is True:
        return 1
    elif value is False:
        return 0
    else:
        return value


def render_metrics(metrics):
    output = ""
    for k, v in metrics.items():
        output += "{k} {v}\n".format(k=k, v=render_value(v))
    return Response(output, mimetype='text/plain')


def label_metrics(metrics, labels):
    label_items = ",".join('{k}="{v}"'.format(k=k, v=v) for k, v in labels.items())
    label = "{" + label_items + "}"

    labelled = {}
    for k, v in metrics.items():
        labelled[k + label] = v
    return labelled


def target_metrics(bb8_status):
    metrics = {}
    targets = json.loads(bb8_status)
    for target in targets:
        print(target)
        item_metrics = {"last_backup": target["last_backup"]}
        item_metrics = label_metrics(item_metrics, {"target_id": target["target"]})
        metrics.update(item_metrics)
    return metrics

