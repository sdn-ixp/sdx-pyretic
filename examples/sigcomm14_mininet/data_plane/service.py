"""
Example service that manages Quagga routers
"""

from mininext.mount import MountProperties, ObjectPermissions, PathProperties
from mininext.moduledeps import serviceCheck
from mininext.service import Service

class QuaggaService( Service ):
    "Manages Quagga Software Router Service"

    def __init__( self, name="Quagga", **params ):
        "Initialize a QuaggaService object that can be used by multiple nodes"

        "Verify that Quagga is installed"
        serviceCheck( 'quagga', moduleName='Quagga (nongnu.org/quagga/)')

        "Call service initialization (it will take care of defaultGlobalParams)"
        Service.__init__( self, name=name, **params )

        self.getDefaultGlobalMounts()

    def getDefaultGlobalParams( self ):
        "Returns the default parameters for this service"
        defaults = { 'startCmd': '/etc/init.d/quagga start',
                     'stopCmd': '/etc/init.d/quagga stop',
                     'autoStart': True,
                     'autoStop': True,
                     'configPath': None }
        return defaults

    def getDefaultGlobalMounts( self ):
        "Service-wide default mounts for the Quagga service"

        mounts = []
        mountConfigPairs = {}

        "quagga configuration paths"
        quaggaConfigPerms = ObjectPermissions( username = 'quagga',
                                               groupname = 'quaggavty',
                                               mode = 0775,
                                               strictMode = False,
                                               enforceRecursive = True)
        quaggaConfigPath = PathProperties( path=None,
                                           perms=quaggaConfigPerms,
                                           create=True,
                                           createRecursive=True,
                                           setPerms=False,
                                           checkPerms=True )
        quaggaConfigMount = MountProperties( target='/etc/quagga',
                                             source = quaggaConfigPath )
        mounts.append(quaggaConfigMount)
        mountConfigPairs['quaggaConfigPath'] = quaggaConfigMount

        return mounts, mountConfigPairs