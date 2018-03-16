# bb8
This repository is a set of bash and Python scripts that wrap around rsync.

# Configuration
bb8 backs up data to another server, which we call the Starport, via ssh.
Before running any scripts, bb8 needs a JSON configuration file. It should live in this repo at `./etc/config.json`.

## Sample configuration file
Here's a sample configuration file. It should be mostly self explanatory.

```
{
    "starport": {
        "addr": "annex.montagu.dide.ic.ac.uk",
        "user": "montagu",
        "backup_location": "testrsync/"
    },
    "targets": [
        {
            "type": "directory",
            "name": "test",
            "path": "/testrsync/"
        }
    ]
}

```

## Targets
Targets are what should be backed up (and restored). Each target must specify a
"type", which can be `directory` or `named_volume`. Each of these
requires further options.

### Directory
Simplest option. Requires a `path` to a directory.

### Named volume
Requires the `name` of the volume.

# Scripts
So that bb8 can communicate with the Starport via ssh,
 we first need to generate a key pair which we store in the vault, then add the public key to the authorized_keys
 file on Starport. This is done by running `./setup_starport.sh` on the Starport. To run backups
  bb8 needs the corresponding private key and a JSON configuration file.
 When bb8 has been configured, these live in this repo at `./etc/config.json` and `./etc/id_rsa`, respectively.
There are six entrypoints to the backup module.

1. `setup_starport.sh`: To be run on Starport. So that bb8 can communicate with the Starport via ssh,
 we first need to generate a key pair which
 we store in the vault, then add the public key to the authorized_keys
 file on Starport. You will be prompted for Vault (GitHub) access token. Should be run as the user you want to connect
 via ssh with.
1. `setup_config.py`: This allows the user to choose which target should be backed up and/or restored on this machine
1. `setup.sh`: This creates a user `bb8`, installs dependencies and then reads secrets from the vault and stores them
   in `./etc`. You will be prompted for Vault (GitHub) access token. Must be run as root.
1. `backup.py`: Runs a one-off backup. Output is logged to this repo at `./log/.` Should be run as the bb8 user.
1. `backup.sh`: Creates a lock directory and runs a one-off backup, then removes lock directory.
 If a lock directory exists and there is a running process, exits without doing anything.
  If a lock file exists and no running process, removes the lock directory.
1. `schedule.py`: Creates a cron job that runs backup.sh every hour and logs to `./log`. Must be run as root.
1. `restore.py`:  Restores the configured targets. Creates directories and volumes if they don't exist.

# Setup
Note: Montagu specific setup instructions here: https://github.com/vimc/montagu-bb8.
If setting up Montagu backup, follow those instructions first. Then, from this directory:

1. run `./setup_config.py` as root to configure targets.
2. run `./setup.sh` as root.

NB: The `bb8` group now owns the directory, so to enable pulling from git without `sudo`,
 add your user to the `bb8` group

3. Use one of the entry points listed above to backup, schedule backups, or restore.

# Tests

Run the test suite with

```
pip3 install -r requirements-dev.txt
nosetests3
```
