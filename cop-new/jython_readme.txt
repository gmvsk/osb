How to run it manually (without Ansible)

# SSH into the OSB server, switch to oracle user
sudo su - oracle

# Make sure backup directory exists
mkdir -p /opt/osb_backups

# Run with wlst.sh (adjust the path to your environment)
/u01/app/oracle/middleware/oracle_common/common/bin/wlst.sh osb_export_all_projects.py

What each step does
Step	API call	Effect
connect()	Opens a read-only JMX connection to the Admin Server	No changes
domainRuntime()	Switches the MBean navigation tree	No changes
findService()	Looks up the ALSBConfigurationMBean	No changes
getRefs(Ref.DOMAIN)	Lists all resource references across the domain	Read-only
export(allRefs, True, None)	Serializes all resources into an in-memory JAR byte array	Read-only — no session, no lock
FileOutputStream.write()	Writes the JAR bytes to your BACKUP_DIR	Only writes the output file
disconnect()	Closes the JMX connection	Cleanup
The True parameter in export() means "include dependencies" — ensures a complete, self-contained backup. The None means no passphrase on the exported JAR.

