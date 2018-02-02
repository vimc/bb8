#!/usr/bin/env bash
set -e

HERE=${BASH_SOURCE%/*}
source ${HERE}/vault_auth.sh

echo "Installing Pip and required Python packages"
apt-get install python3-pip -y > /dev/null
pip3 install -q -r ${HERE}/requirements.txt

echo "-------------------------------------------"
echo "Installing bb8 user and group"

if ! id -u bb8 > /dev/null 2>&1; then
    useradd bb8 -d /var/lib/bb8
    password=$(vault read --field password secret/backup/bb8/user)
    echo "bb8:$password" | chpasswd

    mkdir -p /var/lib/bb8/.ssh

    # add to docker group
    usermod -aG docker bb8
fi

# add bb8 user to bb8 group
usermod -aG bb8 bb8

# give bb8 group owernship of this dir
chgrp -R bb8 $HERE

echo "-------------------------------------------"
echo "Running setup.py:"
(cd "$HERE" && su -c ./setup.py bb8)

echo "-------------------------------------------"

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"