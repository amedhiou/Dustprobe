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
from SmartMeshSDK.IpMgrConnectorMux     import IpMgrSubscribe, IpMgrConnectorMux

#============================ defines =========================================
DEFAULT_MgrSERIALPORT   = '/dev/ttyUSB3'
mymanager               = IpMgrConnectorSerial.IpMgrConnectorSerial()

#============================ functions =======================================

#----------------------------------------------------
# find_connected_devices(mymanager):
#     - The point of this function is to scan for
#       all connected USB devices and recognize the
#       Dust Managers
#     - This should be platform independent
#     - TODO: Scanning should be implemented by
#       listening to com/tty ports instead of writing
#----------------------------------------------------

def find_connected_devices(mymanager):
    """ Lists serial port names
        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    # All platform Support
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
    return result
    # This part needs to be changed
    # At this point I will hard code the port name
    # and will not scan com ports
    """
    for port in ports:
        try:
            print port
            s = serial.Serial(DEFAULT_MgrSERIALPORT, 9600 ,timeout=3)
            s.close()
            while (True):
                print "test"
                hello = s.readline().decode()
                print hello
            port_cntr = port_cntr + 1
            s.close()
            mymanager.connect({'port': port.strip()})
            temp = mymanager.dn_getNetworkConfig()
            print 'Found Network ',port_cntr,' at ', port.strip(),' NetId :', temp.networkId
            result.append(port)

        except:
            pass
    print "End of scan "

    return result
    """

#----------------------------------------------------
# connect_manager_serial( mymanager , ports ):
#     - This function gets the list of available Dust
#       managers and gives the user the choise of 
#       connecting to some or all of them
#     - TODO: remove the hard coded serialport and
#       add nessasary changes
#----------------------------------------------------

def connect_manager_serial( mymanager , ports ):
    # This part checks for the list of available Dust Ports
    # The Com port is now set to default so no need to go through the list
    """    for port in ports:
        serialport = port.strip()

    if not ports:
        print " No networks connected "
        os._exit(0)
    """
    serialport = DEFAULT_MgrSERIALPORT # in my set up its /dev/ttyUSB3
    try:
        mymanager.connect({'port': serialport})
        print "connected to manager at : ", serialport
    except Exception as err:
        print('failed to connect to manager at {0}, error ({1})\n{2}'.format(
            serialport ,
            type(err) ,
            err
        ))
        raw_input('Aborting. Press Enter to close.')
        os._exit(0)

#----------------------------------------------------
# handle_data(notifName, notifParams):
#     - This function parses the Health reports recieved
#     - TODO: the data should be saved for further processing
#----------------------------------------------------
def handle_data(notifName, notifParams):

    mac        = FormatUtils.formatMacString(notifParams.macAddress)
    hrParser   = HrParser.HrParser()

    print "--------------------------- MSG ------------------------ "
    hr    = hrParser.parseHr(notifParams.payload)
    hrReport = '{'+mac+'}\n'+'{'+hrParser.formatHr(hr)+'}'
    print hrReport
    print "-------------------------- END MSG --------------------- "

#============================ main ============================================

print( '===================================================\n')

#===== connect to the manager

ports = find_connected_devices(mymanager)
ports = "/dev/ttyUSB3"
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


currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
continueAsking = True
returnVal = []



# the bellow subroutine should be done once every 15 minutes
while continueAsking:
    try:
        res = mymanager.dn_getMoteConfig(currentMac,True)
        print "MoteID: ", res.moteId,", MAC: ",res.macAddress,", AP:", res.isAP,", State:", res.state, ", Routing:", res.isRouting

    except:
        continueAsking = False
    else:
        if ((not res.isAP) and (res.state in [4,])):
            returnVal.append(tuple(res.macAddress))
        currentMac = res.macAddress

#raw_input("hit any key to quit\n")
#mymanager.disconnect()
#os._exit(0)


