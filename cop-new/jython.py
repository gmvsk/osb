# osb_export_all_projects.py
#
# WLST/Jython script to export ALL Oracle Service Bus projects to a JAR file.
# This is a READ-ONLY operation — no sessions are created, nothing is modified.
#
# Usage:
#   /path/to/wlst.sh osb_export_all_projects.py

from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.config import Ref
from java.io import FileOutputStream
import time
import sys

# =======================================================================
# UPDATE THESE VALUES FOR YOUR ENVIRONMENT
# =======================================================================
ADMIN_URL  = 't3://localhost:7001'
USERNAME   = 'weblogic'
PASSWORD   = 'YourSharedPasswordHere'
BACKUP_DIR = '/opt/osb_backups'
# =======================================================================

timestamp   = time.strftime('%Y%m%d_%H%M%S')
export_file = BACKUP_DIR + '/osb_backup_all_projects_' + timestamp + '.jar'

print '=' * 60
print 'OSB Full Export — Starting'
print '=' * 60
print 'Admin URL  : ' + ADMIN_URL
print 'Username   : ' + USERNAME
print 'Export File : ' + export_file
print '=' * 60

try:
    # Step 1 — Connect to the running Admin Server (read-only)
    print '\n[1/5] Connecting to Admin Server ...'
    connect(USERNAME, PASSWORD, ADMIN_URL)
    print '[1/5] Connected.'

    # Step 2 — Switch to domain-runtime MBean tree
    print '[2/5] Switching to domain runtime ...'
    domainRuntime()

    # Step 3 — Locate the Service Bus configuration MBean
    print '[3/5] Locating ALSBConfigurationMBean ...'
    alsbMBean = findService(ALSBConfigurationMBean.NAME,
                            ALSBConfigurationMBean.TYPE)
    if alsbMBean is None:
        print 'ERROR: ALSBConfigurationMBean not found. Is OSB deployed?'
        sys.exit(1)

    # Step 4 — Gather every resource reference in the domain
    print '[4/5] Retrieving all project resources ...'
    allRefs = alsbMBean.getRefs(Ref.DOMAIN)
    print '       Found ' + str(allRefs.size()) + ' resources.'

    if allRefs.size() == 0:
        print 'WARNING: No resources found. Nothing to export.'
        disconnect()
        exit()

    # Step 5 — Export all resources (read-only, returns byte[] JAR)
    print '[5/5] Exporting to JAR ...'
    jarBytes = alsbMBean.export(allRefs, True, None)
    print '       Generated ' + str(len(jarBytes)) + ' bytes.'

    # Write the JAR bytes to disk
    fos = FileOutputStream(export_file)
    fos.write(jarBytes)
    fos.close()

    print '\n' + '=' * 60
    print 'SUCCESS'
    print 'File : ' + export_file
    print 'Size : ' + str(len(jarBytes)) + ' bytes'
    print '=' * 60

except Exception, e:
    print '\nERROR: ' + str(e)
    raise e

finally:
    try:
        disconnect()
    except:
        pass
    exit()
