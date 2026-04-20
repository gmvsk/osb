from java.lang import System
from com.bea.wli.sb.management.configuration import SessionManagementMBean
from com.bea.wli.sb.management.configuration import ALSBConfigurationMBean
from com.bea.wli.sb.management.configuration import Exporter
from com.bea.wli.sb.management.query import ProjectQuery
from weblogic.management.scripting.utils import WLSTException

# ---------------------------
# Hardcoded configuration
# ---------------------------
ADMIN_URL = 't3://osb-admin-host:7001'
OSB_USER = 'osb_shared_user'
OSB_PASSWORD = 'password123'
EXPORT_FILE = '/u01/osb_backup/osb_all_projects.jar'

try:
    print('Connecting to OSB Admin Server...')
    connect(OSB_USER, OSB_PASSWORD, ADMIN_URL)

    domainRuntime()

    sessionName = 'osbExportSession'
    sessionMBean = findService(
        SessionManagementMBean.NAME,
        SessionManagementMBean.TYPE
    )
    sessionMBean.createSession(sessionName)

    print('Session created:', sessionName)

    alsbMBean = findService(
        ALSBConfigurationMBean.NAME,
        ALSBConfigurationMBean.TYPE
    )

    query = ProjectQuery()
    projects = alsbMBean.getProjects(query, sessionName)

    projectNames = []
    for p in projects:
        projectNames.append(p.getName())

    print('Projects found:', projectNames)

    exporter = Exporter(alsbMBean)
    exporter.exportProjects(projectNames, EXPORT_FILE, sessionName)

    print('Export successful:', EXPORT_FILE)

    sessionMBean.discardSession(sessionName)

except WLSTException as e:
    print('WLST Error:', e)

finally:
    disconnect()
    exit()
