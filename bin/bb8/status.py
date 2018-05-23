import json
import sys
from os.path import join

import docker as docker
from dateutil import parser
from tzlocal import get_localzone

from .remote_paths import RemotePaths
from .settings import load_settings


def _run_remote_cmd(remote_cmd: str, docker_client, paths: RemotePaths):
    cmd = ["ssh", paths.host, remote_cmd]
    volumes = {
        "bb8_ssh": {"bind": "/root/.ssh", "mode": "ro"}
    }
    return docker_client.containers.run("instrumentisto/rsync-ssh",
                                        command=cmd,
                                        volumes=volumes,
                                        remove=True)


def get_last_backup(paths: RemotePaths, docker_client):
    remote_cmd = "cat {}".format(join(paths.meta(), "metadata.json"))
    output = _run_remote_cmd(remote_cmd,  docker_client, paths)
    metadata = json.loads(output)
    return normalize_timestamp(metadata["last_backup"])


def interpret_timestamp_output(raw, timezone=None):
    string = raw.decode('utf-8').strip()
    if string:
        return normalize_timestamp(string, timezone)
    else:
        return "No files present"


def normalize_timestamp(string, timezone=None):
    timezone = timezone or get_localzone()
    return parser.parse(string) \
        .replace(microsecond=0) \
        .astimezone(timezone) \
        .isoformat(" ")


def last_modified_remote(paths: RemotePaths, docker_client):
    remote_cmd = 'find -L {} -type f -print0'.format(paths.data()) + \
                 ' | xargs -0 stat --format "%Y :%y"' \
                 ' | sort -nr' \
                 ' | cut -d: -f2-' \
                 ' | head -n 1'
    output = _run_remote_cmd(remote_cmd, docker_client, paths)
    return interpret_timestamp_output(output)


def last_modified_local(target, docker_client):
    cmd = 'find -L /data -type f -print0' \
          ' | xargs -0 stat -c "%y"' \
          ' | sort -nr' \
          ' | head -n 1'
    volumes = {target.mount_id: {"bind": "/data", "mode": "ro"}}
    output = docker_client.containers.run("bash",
                                          command=["bash", "-c", cmd],
                                          volumes=volumes,
                                          remove=True)
    return interpret_timestamp_output(output)


def get_target_status(target, docker_client, settings):
    starport = settings.starport
    paths = RemotePaths(target.name, starport)
    return {
        "target": target.name,
        "last_backup": get_last_backup(paths, docker_client),
        "last_modified_local": last_modified_local(target, docker_client),
        "last_modified_remote": last_modified_remote(paths, docker_client)
    }


def print_target_status(data):
    template = """
{target}
------------    
Last backup:               {last_backup}
Local copy last modified:  {last_modified_local}
Remote copy last modified: {last_modified_remote}"""
    print(template.format(**data), flush=True)


def print_status(args, settings_source=load_settings,
                 docker_client=docker.from_env()):
    settings = settings_source()
    targets = settings.targets
    if args["TARGET"]:
        targets = list(t for t in targets if t.name in args["TARGET"])
        remainder = set(args["TARGET"]) - set(t.name for t in targets)
        if remainder:
            print("Unknown targets specified: " + " ".join(remainder))
            sys.exit(-1)

    statuses = (get_target_status(t, docker_client, settings) for t in targets)
    if args["--json"]:
        print(json.dumps(list(statuses), indent=4))
    else:
        for status in statuses:
            print_target_status(status)
