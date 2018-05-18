import sys
from os.path import join

import docker as docker
from dateutil import parser

from .settings import load_settings


def get_last_backup():
    return "??"


def interpret_timestamp_output(raw, timezone=None):
    string = raw.decode('utf-8').strip()
    if string:
        return parser.parse(string) \
            .replace(microsecond=0) \
            .astimezone(timezone) \
            .isoformat(" ")
    else:
        return "No files present"


def last_modified_remote(target, docker_client, starport):
    remote_path = join(starport["backup_location"], target.mount_id.strip('/'))
    remote_cmd = 'find -L {} -type f -print0'.format(remote_path) + \
                 ' | xargs -0 stat --format "%Y :%y"' \
                 ' | sort -nr' \
                 ' | cut -d: -f2-' \
                 ' | head -n 1'
    cmd = ["ssh", "{user}@{addr}".format(**starport), remote_cmd]
    volumes = {
        "bb8_ssh": {"bind": "/root/.ssh", "mode": "ro"}
    }
    output = docker_client.containers.run("instrumentisto/rsync-ssh",
                                          command=cmd,
                                          volumes=volumes,
                                          remove=True)
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


def print_target_status(target, docker_client, settings):
    starport = settings.starport
    values = {
        "target": target.name,
        "last_backup": get_last_backup(),
        "modified_local": last_modified_local(target, docker_client),
        "modified_remote": last_modified_remote(target, docker_client, starport)
    }
    template = """
{target}
------------    
Last backup:               {last_backup}
Local copy last modified:  {modified_local}
Remote copy last modified: {modified_remote}"""
    print(template.format(**values), flush=True)


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

    for target in targets:
        print_target_status(target, docker_client, settings)
