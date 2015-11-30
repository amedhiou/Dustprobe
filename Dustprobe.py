#!/uer/bin/python

#============================ adjust path =====================================

import sys
import os
import re
import serial
import glob
import time

if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))
#============================ verify installation =============================

from SmartMeshSDK import SmsdkInstallVerifier
(goodToGo,reason) = SmsdkInstallVerifier.verifyComponents(
    [
        SmsdkInstallVerifier.PYTHON,
        SmsdkInstallVerifier.PYSERIAL,
    ]
)
if not goodToGo:
    print ("Your installation does not allow this application to run:\n")
    print (reason)
    input("Press any button to exit")
    sys.exit(0)

#============================ imports =========================================

import random
from SmartMeshSDK                       import AppUtils, \
                                               FormatUtils
from SmartMeshSDK                       import HrParser
from SmartMeshSDK                       import sdk_version
from SmartMeshSDK.ApiDefinition         import IpMgrDefinition
from SmartMeshSDK.IpMgrConnectorSerial  import IpMgrConnectorSerial
from SmartMeshSDK.IpMgrConnectorMux     import IpMgrSubscribe

#============================ defines =========================================
DEFAULT_MgrSERIALPORT   = '/dev/ttyUSB3'
mymanager               = IpMgrConnectorSerial.IpMgrConnectorSerial()

#============================ helper functions ================================
def find_connected_devices(mymanager):
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    print "Scannining for avaible networks ..."
    result = []
    port_cntr = 0
    for port in ports:
        try:
    #        print port
            s = serial.Serial(port)
            s.close()
            port_cntr = port_cntr + 1
            mymanager.connect({'port': port.strip()})
            temp = mymanager.dn_getNetworkConfig()
            print 'Found Network ',port_cntr,' at ', port.strip(),' NetId :', temp.networkId
            result.append(port)

        except:
            pass
    print "End of scan "
    return result


def connect_manager_serial( mymanager , ports ):
    #Function to connect Manager to Serial port
    for port in ports:
        serialport = port.strip()

    if not ports:
        print " No networks connected "
        os._exit(0)

    try:
        mymanager.connect({'port': serialport})
        print "connected to manager at : ", serialport
    except Exception as err:
        print('failed to connect to manager at {0}, error ({1})\n{2}'.format(
            serialport,
            type(err),
            err
        ))
        raw_input('Aborting. Press Enter to close.')
        os._exit(0)

def handle_data(notifName, notifParams):
    mac        = FormatUtils.formatMacString(notifParams.macAddress)
    hrParser   = HrParser.HrParser()

    print "--------------------------- MSG ------------------------ "
    print mac
    print mymanager.dn_getNetworkConfig()
    print notifParams.payload
    hr    = hrParser.parseHr(notifParams.payload)
    print hrParser.formatHr(hr)
#    hrReport = '{'+mac+'}\n'+'{'+hrParser.formatHr(hr)+'}'
    print hr    #Report
    print "-------------------------- END MSG --------------------- "

#============================ main ============================================

print( '===================================================\n')

#===== connect to the manager

ports = find_connected_devices(mymanager)

connect_manager_serial(mymanager, ports)

# subscribe to data notifications

subscriber = IpMgrSubscribe.IpMgrSubscribe(mymanager)
subscriber.start()
subscriber.subscribe(
    notifTypes =    [
                        IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                    ],
    fun =           handle_data,
    isRlbl =        False,
)
#subscriber.subscribe(
#    notifTypes =    [
#        IpMgrSubscribe.IpMgrSubscribe.ERROR,
#        IpMgrSubscribe.IpMgrSubscribe.FINISH,
#    ],
#    fun =           self.disconnectedCallback,
#    isRlbl =        True,
#    )

raw_input("hit any key to quit\n")
mymanager.disconnect()
os._exit(0)



