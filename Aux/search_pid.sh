#!/usr/bin/env bash

if [ "$EUID" -ne 0 ];then
    echo "Please run this script as root user"
    exit 1
fi

# Remove all audit log files to avoid getting results from previous attacks
rm /var/log/audit/audit.log*

# Create a new empty log file
touch /var/log/audit/audit.log
chmod 0600 /var/log/audit/audit.log
# Enable Service
service auditd start

# Remove possible rules on the service
auditctl -D

# Add filter to pid and ppid
# Since we can't follow the entire process tree
# We are basing our search on the fact that when a new process is created
# USUALLY has an higher pid than it's parent
# Important to mencion that the OS sometimes shifts the pid's values (Otherwise the pid values would increase until
# infinite)

# We are aware of this possibility, however audit is not our main auditing tool, but rather a validation tool
# to the main one

# As a precaution we added the ppid=$1 wich will track child processes even if their pid is inferior, however this does
# not apply to grand-children of the main process and might cause duplication
default_IFS="$IFS"
IFS=','
for i in $1
do
	# Maybe could be added later if we implement it also in our module
	# auditctl -a exit,always -F ppid=$i -S all -k parent_pid
	auditctl -a exit,always -F pid\>=$i -S all -k greater_than
done
