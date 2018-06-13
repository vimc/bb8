import json
import sys
from datetime import datetime

import docker as docker
from dateutil import parser
from tzlocal import get_localzone

from .targets import NamedVolumeTarget
from .remote_file_manager import RemoteFileManager
from .remote_paths import RemotePaths
from .settings import load_settings


def get_last_backup(fm: RemoteFileManager):
    metadata = fm.get_metadata()
    if metadata:
        return normalize_timestamp(metadata["last_backup"])
    else:
        return None


def interpret_timestamp_output(raw, timezone=None):
    string = raw.decode('utf-8').strip()
    if string:
        return normalize_timestamp(string, timezone)
    else:
        return None


def normalize_timestamp(string, timezone=None):
    timezone = timezone or get_localzone()
    return parser.parse(string) \
        .replace(microsecond=0) \
        .astimezone(timezone)


def last_modified_remote(fm: RemoteFileManager, paths: RemotePaths):
    remote_cmd = 'find -L {}  -print0 -type f -o -type d'.format(paths.data) + \
                 ' | xargs -0 stat --format "%Y :%y"' \
                 ' | sort -nr' \
                 ' | cut -d: -f2-' \
                 ' | head -n 1'
    output = fm.run_remote_cmd(remote_cmd)
    return interpret_timestamp_output(output)


def last_modified_local(target, docker_client):
    if isinstance(target, NamedVolumeTarget) and target.mount_id not in [v.id for v in docker_client.volumes.list()]:
        return None

    cmd = 'find -L /data  -print0 -type f -o -type d' \
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
    last_backup = data["last_backup"]
    mod_local = data["last_modified_local"]
    mod_remote = data["last_modified_remote"]

    template = """
{target}
------------    
Last backup:               {last_backup}
Local copy last modified:  {last_modified_local}
Remote copy last modified: {last_modified_remote}"""

    formatted = template.format(
        target=data["target"],
        last_backup=last_backup or "Never backed up",
        last_modified_local=mod_local or "No files present",
        last_modified_remote=mod_remote or "No files present"
    )
    print(formatted, flush=True)

    if mod_local and (not last_backup or mod_local > last_backup):
        print("Warning: Data has been modified since last backup. "
              "Consider running bb8 backup.")
    if mod_remote and (not mod_local or mod_remote > mod_local):
        print("Warning: Remote data has been modified since last restore. "
              "Consider running bb8 restore.")


def serialize_date(obj):
    # Note that we return dates in JSON as UTC whereas when printing them out in
    # a human-friendly way we use the user's timezone.
    if isinstance(obj, datetime):
        return obj.astimezone().isoformat(" ")
    raise TypeError("Type %s not serializable" % type(obj))


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
        print(json.dumps(list(statuses),
                         indent=4,
                         default=serialize_date))
    else:
        for status in statuses:
            print_target_status(status)
