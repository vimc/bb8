#!/usr/bin/env bash
set -e
echo "#!/usr/bin/env bash" > /etc/cron.hourly/bb8
echo "bb8 backup" >> /etc/cron.hourly/bb8
chmod 755 /etc/cron.hourly/bb8
echo "Scheduled hourly backups ☺️"
