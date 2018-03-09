#!/usr/bin/env python3

import os
from subprocess import check_output

from os.path import join, isdir

secrets_dir = "secrets"
ssh_key_path = join(secrets_dir, "ssh_key")
host_key_path = join(secrets_dir, "host_key")


def get_secret(name):
    path = "secret/{}".format(name)
    return check_output(["vault", "read", "-field=value", path]).decode('utf-8')


def save_securely(path, data):
    with open(path, 'a'):  # Create file if does not exist
        pass
    os.chmod(path, 0o600)
    with open(path, 'w') as f:
        f.write(data)


if __name__ == "__main__":
    print("Obtaining secrets from the vault. If you are not authenticated with the vault, this will fail.")
    if not isdir(secrets_dir):
        os.mkdir(secrets_dir)

    ssh_key = get_secret("annex/id_rsa")
    host_key = get_secret("annex/host_key")

    save_securely(ssh_key_path, ssh_key)
    save_securely(host_key_path, host_key)
