# =============================================================================
# osb_export_all.py
# WLST script to export ALL Oracle Service Bus projects into a single JAR file.
# Executed via: wlst.sh osb_export_all.py
# =============================================================================

import sys
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION — edit these values to match your environment
# ---------------------------------------------------------------------------
OSB_ADMIN_HOST   = 'osb-server.example.com'   # WebLogic Admin Server hostname/IP
OSB_ADMIN_PORT   = '7001'                      # Admin Server port (default 7001)
OSB_PROTOCOL     = 't3'                        # Use 't3s' if SSL is enabled
OSB_USERNAME     = 'osb_shared_user'           # Shared/common OSB account username
OSB_PASSWORD     = 'YourPasswordHere'          # Shared/common OSB account password

# Output directory and filename
EXPORT_DIR       = '/opt/osb_backups'
TIMESTAMP        = datetime.now().strftime('%Y%m%d_%H%M%S')
EXPORT_FILENAME  = 'osb_all_projects_' + TIMESTAMP + '.jar'
EXPORT_PATH      = EXPORT_DIR + '/' + EXPORT_FILENAME

# ---------------------------------------------------------------------------
# Override config from environment variables if present (set by Ansible)
# ---------------------------------------------------------------------------
if os.environ.get('OSB_ADMIN_HOST'):
    OSB_ADMIN_HOST = os.environ.get('OSB_ADMIN_HOST')
if os.environ.get('OSB_ADMIN_PORT'):
    OSB_ADMIN_PORT = os.environ.get('OSB_ADMIN_PORT')
if os.environ.get('OSB_PROTOCOL'):
    OSB_PROTOCOL = os.environ.get('OSB_PROTOCOL')
if os.environ.get('OSB_USERNAME'):
    OSB_USERNAME = os.environ.get('OSB_USERNAME')
if os.environ.get('OSB_PASSWORD'):
    OSB_PASSWORD = os.environ.get('OSB_PASSWORD')
if os.environ.get('OSB_EXPORT_DIR'):
    EXPORT_DIR = os.environ.get('OSB_EXPORT_DIR')
    EXPORT_PATH = EXPORT_DIR + '/' + EXPORT_FILENAME

# ---------------------------------------------------------------------------
# Build connection URL
# ---------------------------------------------------------------------------
ADMIN_URL = OSB_PROTOCOL + '://' + OSB_ADMIN_HOST + ':' + OSB_ADMIN_PORT

# ---------------------------------------------------------------------------
# WLST imports (available in the WLST Jython runtime)
# ---------------------------------------------------------------------------
from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.config import Ref
from java.io import FileOutputStream
from java.util import HashSet

def export_all_osb_projects():
    """
    Connect to WebLogic Admin Server, discover all OSB projects,
    and export them into a single JAR file.
    """

    print('')
    print('=' * 70)
    print('  OSB Full Project Export')
    print('=' * 70)
    print('  Admin URL  : ' + ADMIN_URL)
    print('  Username   : ' + OSB_USERNAME)
    print('  Export Path : ' + EXPORT_PATH)
    print('=' * 70)
    print('')

    # ----- Step 1: Connect to WebLogic Admin Server -----
    print('[1/5] Connecting to WebLogic Admin Server...')
    try:
        connect(OSB_USERNAME, OSB_PASSWORD, ADMIN_URL)
        print('      Connected successfully.')
    except Exception, e:
        print('ERROR: Failed to connect to ' + ADMIN_URL)
        print('       ' + str(e))
        sys.exit(1)

    # ----- Step 2: Navigate to domainRuntime and get ALSBConfigurationMBean -----
    print('[2/5] Locating ALSBConfigurationMBean...')
    try:
        domainRuntime()
        configMBean = findService(ALSBConfigurationMBean.NAME, ALSBConfigurationMBean.TYPE)
        if configMBean is None:
            print('ERROR: ALSBConfigurationMBean not found. Is OSB deployed on this domain?')
            disconnect()
            sys.exit(1)
        print('      ALSBConfigurationMBean located.')
    except Exception, e:
        print('ERROR: Could not locate ALSBConfigurationMBean.')
        print('       ' + str(e))
        disconnect()
        sys.exit(1)

    # ----- Step 3: Discover all project-level references -----
    print('[3/5] Discovering all OSB projects...')
    try:
        allRefs = configMBean.getRefs(Ref.DOMAIN)
        print('      Total resources found: ' + str(allRefs.size()))

        # Collect unique project names for display
        projectNames = HashSet()
        iterator = allRefs.iterator()
        while iterator.hasNext():
            ref = iterator.next()
            projectNames.add(ref.getProjectName())

        print('      Projects discovered (' + str(projectNames.size()) + '):')
        pIterator = projectNames.iterator()
        while pIterator.hasNext():
            print('        - ' + pIterator.next())
    except Exception, e:
        print('ERROR: Failed to discover OSB projects.')
        print('       ' + str(e))
        disconnect()
        sys.exit(1)

    # ----- Step 4: Export all resources into a JAR byte array -----
    print('[4/5] Exporting all projects to JAR...')
    try:
        # export(refs, includeCredentials, passphrase)
        # - allRefs: the set of Ref objects to export
        # - True: include security/credential data (set False if not needed)
        # - None: no passphrase encryption on credentials
        jarBytes = configMBean.export(allRefs, True, None)
        print('      Export completed. JAR size: ' + str(len(jarBytes)) + ' bytes')
    except Exception, e:
        print('ERROR: Export failed.')
        print('       ' + str(e))
        disconnect()
        sys.exit(1)

    # ----- Step 5: Write JAR to filesystem -----
    print('[5/5] Writing JAR to ' + EXPORT_PATH + '...')
    try:
        # Ensure output directory exists (Jython/Java way)
        from java.io import File
        exportDir = File(EXPORT_DIR)
        if not exportDir.exists():
            exportDir.mkdirs()
            print('      Created directory: ' + EXPORT_DIR)

        fos = FileOutputStream(EXPORT_PATH)
        fos.write(jarBytes)
        fos.flush()
        fos.close()
        print('      JAR written successfully.')
    except Exception, e:
        print('ERROR: Failed to write JAR file.')
        print('       ' + str(e))
        disconnect()
        sys.exit(1)

    # ----- Cleanup -----
    disconnect()
    print('')
    print('=' * 70)
    print('  EXPORT COMPLETE')
    print('  File: ' + EXPORT_PATH)
    print('=' * 70)
    print('')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
export_all_osb_projects()
exit()
