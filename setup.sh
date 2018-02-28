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
    useradd bb8 -U -d /var/lib/bb8
    password=$(vault read --field password secret/backup/bb8/user)
    echo "bb8:$password" | chpasswd

    mkdir -p /var/lib/bb8/.ssh

    mkdir -p /var/log/bb8/
    chgrp -R bb8 /var/log/bb8/
    chmod 775 /var/log/bb8/

    # add to docker group
    usermod -aG docker bb8
fi

# give bb8 group ownership of this dir
chgrp -R bb8 $HERE
chmod -R 775 $HERE

echo "-------------------------------------------"
echo "Running setup.py:"
(cd "$HERE" && su -c ./setup.py bb8)

echo "-------------------------------------------"

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"