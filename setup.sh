#!/usr/bin/env bash
set -e

source ${BASH_SOURCE%/*}/vault_auth.sh

echo "Installing Pip and required Python packages"
apt-get install python3-pip -y > /dev/null
pip3 install -q -r requirements.txt
if ! id -u bb8 > /dev/null 2>&1; then
    useradd bb8
    password=$(vault read --field password secret/backup/bb8/user)
    echo "bb8:$password" | chpasswd
fi

echo "-------------------------------------------"
echo "Running setup.py:"
su -c "source ${BASH_SOURCE%/*}/vault_auth.sh && ${BASH_SOURCE%/*}/setup.py" bb8

echo "-------------------------------------------"
echo "Setup complete. To schedule backups, run ./schedule.py"
echo "To perform a restore, run ./restore.py"
