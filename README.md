# bb8
This repository is a set of bash and Python scripts that wrap around rsync.

# Configuration
bb8 backs up data to another server, which we call the Starport, via ssh.
We create a "source" configuration file that lists all targets. Then, when we
set up a particular machine to either backup or restore, we choose which targets
we want to backup and/or restore on this machine.

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
"type", which can be `directory` or `named_volume`, and a name, which is unique
across all targets. Each type of target requires further options.

### Directory
Simplest option. Requires a `path` to a directory.

### Named volume
`volume`: The name`volume` of the volume.

# Setup
## Setup starport
So that bb8 can communicate with the Starport via ssh,
 we first need to generate a key pair which we store in the vault, then add the public key to the authorized_keys
 file on Starport. This is done by running `./setup_starport.sh` on the Starport. To run backups
  bb8 needs the corresponding private key and a JSON configuration file.
 When bb8 has been configured, these live in this repo at `./etc/config.json` and `./etc/id_rsa`, respectively.

## Setup leaf machine
```
./setup.sh PATH_TO_SOURCE_CONFIG [TARGET ...]
```

This builds a new docker image. It includes the source config, filtered to 
the requested targets, and the SSL secrets from the Vault. For this reason, 
it is important that you do not push this image to any remote registry.

Once the docker image is build, the setup script also creates required 
volumes for bb8, and invokes the built image to dump out the SSH key and 
known hosts file that will be required for the rsync container.

# Using bb8
You can invoke the image built by setup.sh with the `./bb8` wrapper script. e.g.

```
./bb8 backup
```

or to see all options, just:

```
./bb8
```

## Schedule backups
`schedule.py`: Creates a cron job that runs backup.sh every hour and logs to 
the `bb8_logs` volume. Must be run as root.

# Setup record
Steps taken to set up the annex
1. Clone this repo anywhere
```
git clone https://github.com/vimc/bb8
```

2. Run `./setup_starport.sh` as root.
```
sudo /montagu/bb8/setup.sh
```

That's it. Note that this will create a `bb8` user and the starport location will be `/var/lib/bb8/starport`


# Support
Steps taken to set up on support:
1. Clone this repo into the `montagu` directory
```
git clone https://github.com/vimc/bb8
```

2. Run `./setup.sh` as root. When prompted for a config file choice, choose 'support'
```
sudo /montagu/bb8/setup.sh
```

NB: The `bb8` group now owns the directory, so to enable pulling from git without `sudo`,
 add your user to the `bb8` group

3. Run `./schedule.py` as root
```
sudo /montagu/bb8/schedule.py
```
