import json
import sys

import docker as docker
from dateutil import parser
from tzlocal import get_localzone

from .remote_file_manager import RemoteFileManager
from .remote_paths import RemotePaths
from .settings import load_settings


def get_last_backup(fm: RemoteFileManager):
    metadata = fm.get_metadata()
    if metadata:
        return normalize_timestamp(metadata["last_backup"])
    else:
        return "Never backed up"


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


def last_modified_remote(fm: RemoteFileManager, paths: RemotePaths):
    remote_cmd = 'find -L {}  -print0 -type f -o -type d'.format(paths.data) + \
                 ' | xargs -0 stat --format "%Y :%y"' \
                 ' | sort -nr' \
                 ' | cut -d: -f2-' \
                 ' | head -n 1'
    output = fm.run_remote_cmd(remote_cmd)
    return interpret_timestamp_output(output)


def last_modified_local(target, docker_client):
    cmd = 'find -L /data -type f -o -type d -print0' \
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
    fm = RemoteFileManager(paths, docker_client)
    return {
        "target": target.name,
        "last_backup": get_last_backup(fm),
        "last_modified_local": last_modified_local(target, docker_client),
        "last_modified_remote": last_modified_remote(fm, paths)
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
