Yes, this is absolutely doable with Ansible + WLST (WebLogic Scripting Tool). The approach is:

Ansible SSHs into the OSB server, switches to the oracle user
Deploys a WLST (Jython) script that connects to the running OSB admin server
The script uses the ALSBConfigurationMBean (read-only) to export all projects as a JAR
Cleans up the temporary script
This is entirely read-only — it only reads from the OSB runtime and writes a JAR file to disk. Nothing is modified on the server or application.

Files You Need
1. Inventory file

# inventory.ini
[osb_server]
your-osb-hostname-or-ip ansible_user=your_ssh_username

Replace your-osb-hostname-or-ip with the OSB server's hostname/IP and your_ssh_username with the account you use to SSH in (Ansible will then sudo to oracle).

How to Run
Step 1 — On your Ubuntu/Ansible control machine, create a working directory and place both files:

mkdir ~/osb-export && cd ~/osb-export
# create inventory.ini and osb_export_playbook.yml with the contents above

Step 2 — Edit the playbook vars: section with your real values:

Variable	What to set
oracle_home	The Middleware/Oracle home on the OSB server (e.g. /u01/app/oracle/middleware)
admin_url	t3://localhost:7001 if running from the server itself; change host/port if different
osb_username	The shared/common OSB service account
osb_password	Its password
backup_dir	Filesystem path where the JAR will be written
Step 3 — Run:
ansible-playbook -i inventory.ini osb_export_playbook.yml

If your SSH user needs a password for sudo to oracle:
ansible-playbook -i inventory.ini osb_export_playbook.yml --ask-become-pass

What Happens (end to end)
Step	Action	Modifies anything?
1	Creates backup_dir on disk if missing	Only creates a directory for the JAR output
2	Copies a temp Python script to /tmp/	Temp file, removed at end
3	Runs wlst.sh which connects to the already running Admin Server and calls the read-only export() API	No — read-only MBean call
4–5	Prints output, verifies the JAR exists	No
6	Deletes the temp script	Cleans up after itself
The resulting JAR file in backup_dir is identical to what you'd get by opening the OSB console → Export → selecting all projects → downloading the JAR.

Key Notes
SSL/T3S: If your admin server uses SSL, change t3:// to t3s:// in admin_url.
Port: Default is 7001; check your environment's actual admin port.
wlst.sh path: If oracle_common/common/bin/wlst.sh doesn't exist at that path, run find $ORACLE_HOME -name wlst.sh on the server to locate it.
No sessions created: The script does NOT call createSession() — it uses the read-only ALSBConfigurationMBean directly, so there's zero risk of leftover sessions or locks.
