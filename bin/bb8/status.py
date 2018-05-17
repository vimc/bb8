import docker as docker

from bb8.settings import load_settings


def get_last_backup():
    return "??"


def last_modified_remote(target, docker, starport):
    remote_cmd = 'find -L ./starport/montagu/teamcity -type f -print0 | xargs -0 stat --format "%Y :%y" | sort -nr | cut -d: -f2- | head -n 1'
    cmd = ["ssh", "{user}@{addr}".format(**starport), remote_cmd]
    volumes = {
        "bb8_ssh": {"bind": "/root/.ssh", "mode": "ro"}
    }
    output = docker.containers.run("instrumentisto/rsync-ssh",
                                   command=cmd,
                                   volumes=volumes,
                                   remove=True)
    return output.decode('utf-8').strip()


def last_modified_local(target, docker):
    cmd = 'find -L /data -type f -print0' \
          ' | xargs -0 stat -c "%y"' \
          ' | sort -nr' \
          ' | head -n 1'
    volumes = {target.mount_id: {"bind": "/data", "mode": "ro"}}
    output = docker.containers.run("bash",
                                   command=["bash", "-c", cmd],
                                   volumes=volumes,
                                   remove=True)
    return output.decode('utf-8').strip()


def print_target_status(target, docker, settings):
    starport = settings.starport
    values = {
        "target": target.name,
        "last_backup": get_last_backup(),
        "last_modified_local": last_modified_local(target, docker),
        "last_modified_remote": last_modified_remote(target, docker, starport)
    }
    template = """
{target}
------------    
Last backup:               {last_backup}
Local copy last modified:  {last_modified_local}
Remote copy last modified: {last_modified_remote}
    """
    print(template.format(**values))


def print_status(args, settings_source=load_settings, docker=docker.from_env()):
    settings = settings_source()
    targets = list(t for t in settings.targets if t.name == "teamcity")
    for target in targets:
        print_target_status(target, docker, settings)
