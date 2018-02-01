#!/usr/bin/env bash
set -e

source ${BASH_SOURCE%/*}/vault_auth.sh

echo "Installing Pip and required Python packages"
apt-get install python3-pip -y > /dev/null
pip3 install -q -r requirements.txt

echo "-------------------------------------------"
echo "Installing bb8 user and group"

if ! id -u bb8 > /dev/null 2>&1; then
    useradd bb8
    password=$(vault read --field password secret/backup/bb8/user)
    echo "bb8:$password" | chpasswd

    # set bb8 home dir
    mkdir /var/lib/bb8/.ssh
    usermod -m -d /var/lib/bb8 bb8
    chown -R bb8:bb8 /var/lib/bb8

    # add to docker group
    usermod -aG docker bb8
fi

if ! /usr/bin/getent group bb8 2>&1 > /dev/null; then
    groupadd bb8
fi

# add bb8 user to bb8 group
usermod -aG bb8 bb8

# give bb8 group owernship of this dir
chgrp -R bb8 .

echo "-------------------------------------------"
echo "Running setup.py:"
su -c "source ${BASH_SOURCE%/*}/vault_auth.sh && ${BASH_SOURCE%/*}/setup.py" bb8

echo "-------------------------------------------"

echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"
