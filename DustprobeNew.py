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
    input ("Press any button to exit")
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
DEFAULT_MgrSERIALPORT    = '/dev/ttyUSB3'
mymanager                = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager1               = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager2               = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager3               = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager4               = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager5               = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager6               = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager7               = IpMgrConnectorSerial.IpMgrConnectorSerial()
mymanager8               = IpMgrConnectorSerial.IpMgrConnectorSerial()
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

    elif sys.platform('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')

    print "Scanning for available networks ..."
    result = []
    port_cntr = 0

    # scan the available ports looking for the one(s) sending the HDLC hello message
    # put these ports in the result array and return that array
    for port in ports:
    #    print (port)
        try:
            s = serial.Serial(port,
                baudrate = 115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2)

            s.flushOutput()
            mes = s.read(10)

            if mes:
<<<<<<< HEAD
        #        print("message recieved from port")
        #        print mes
                print "Found new Device at :", port
=======
                print("message recieved from port")
                print(mes.decode('unicode-escape'))
                mes_inhex=":".join("{:02x}".format(ord(c)) for c in mes)
                print(mes_inhex)
>>>>>>> d02cce2f69e53b0bbaf1b19d2715f4824f7cebf7
                result.append(port)
            s.close()

        except serial.SerialException as e:
            pass
        except OSError as e:
            pass
    try:
        file = open('obj/portList', 'r')
        print "... Checking connection history:"
        for line in file:
            oldPort = line.strip()
            if oldPort in result:
                pass
            else:
                result.append(oldPort)
    except:
        print "No connection history found"
        pass
    return result

#----------------------------------------------------
# connect_manager_serial( mymanager , ports ):
#     - This function gets the list of available Dust
#       managers and gives the user the choise of 
#       connecting to some or all of them
#     - TODO: remove the hard coded serialport and
#       add nessasary changes
#----------------------------------------------------

def connect_manager_serial( mymanager , port ):
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
        mymanager.connect({'port': port})
        print "connected to manager at : ", port
    except Exception as err:
        print('failed to connect to manager at {0}, error ({1})\n{2}'.format(
            port ,
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

result = []
port_cntr = 0

try:
    # Checking the connectd networks
    print "Found Networks At :"
    for port in ports:
        try:
            mymanager.connect({'port': port.strip()})
            res = mymanager.dn_getNetworkConfig()
            port_cntr = 1 + port_cntr
            result.append(port.strip())
            print " network ", port_cntr," found at ", result[port_cntr-1], " with NetId ", res.networkId
            mymanager.disconnect()

        except:
            print "Something wrong happend here !!!!"
            pass
except:
    print "No Connected Dust Devices Found"
    os._exit(0)

#mymanager.disconnect()

sel = raw_input("Enter the network's number or 'a' to connect to all : \n")


if sel == '1':
    connect_manager_serial(mymanager1, result[port_cntr-1] )
    # subscribe to data notifications
    subscriber = IpMgrSubscribe.IpMgrSubscribe(mymanager1)
    subscriber.start()
    subscriber.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                        ],
        fun =           handle_data,
        isRlbl =        True,
    )

if sel == '2':
    connect_manager_serial(mymanager1,result[port_cntr-2] )
    # subscribe to data notifications
    subscriber = IpMgrSubscribe.IpMgrSubscribe(mymanager1)
    subscriber.start()
    subscriber.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                        ],
        fun =           handle_data,
        isRlbl =        True,
    )

if sel == 'a':
    connect_manager_serial(mymanager1,result[port_cntr-2] )
    connect_manager_serial(mymanager2,result[port_cntr-1] )

    # subscribe to data notifications
    subscriber1 = IpMgrSubscribe.IpMgrSubscribe(mymanager1)
    subscriber2 = IpMgrSubscribe.IpMgrSubscribe(mymanager2)

    subscriber1.start()
    subscriber2.start()

    subscriber1.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                        ],
        fun =           handle_data,
        isRlbl =        True,
    )
    subscriber2.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                        ],
        fun =           handle_data,
        isRlbl =        True,
    )


raw_input("Enter to EXIT : \n")
os._exit(0)


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



