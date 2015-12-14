#!/uer/bin/python

#============================ adjust path =====================================

import sys
import os
import re
import serial
import glob
import time
import datetime

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
NUMBER_OF_NETWORKS = 3
mymanagers = []
for i in range(NUMBER_OF_NETWORKS):
    mymanagers.append(IpMgrConnectorSerial.IpMgrConnectorSerial())
#mymanager3               = IpMgrConnectorSerial.IpMgrConnectorSerial()
#mymanager4               = IpMgrConnectorSerial.IpMgrConnectorSerial()
#mymanager5               = IpMgrConnectorSerial.IpMgrConnectorSerial()
#mymanager6               = IpMgrConnectorSerial.IpMgrConnectorSerial()
#mymanager7               = IpMgrConnectorSerial.IpMgrConnectorSerial()
#mymanager8               = IpMgrConnectorSerial.IpMgrConnectorSerial()

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
        #        print("message recieved from port")
        #        print mes
                print "Found new Device at :", port
                print("message recieved from port")
                print(mes.decode('unicode-escape'))
                mes_inhex=":".join("{:02x}".format(ord(c)) for c in mes)
                print(mes_inhex)
                result.append(port)
            s.close()

        except serial.SerialException as e:
            pass
        except OSError as e:
            pass
    try:
        objfile = open('obj/portList', 'r')
        print "... Checking connection history:"
        for line in objfile:
            oldPort = line.strip()
            if oldPort in result:
                pass
            else:
                result.append(oldPort)
        objfile.close()
    except:
        print "No connection history found"
        pass

  
    objfile = open('obj/portList', 'w')

    for r in result:
        objfile.write(r)

    objfile.close()

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


#-----------------------------------------------------
# data_handlers
# array of functions to be called by the subscriber on recieveing a health report.
# This way each subscriber can use the correct manager, which is required for some data
#-----------------------------------------------------
def data_handler1(notifName, notifParams):
    handle_data(notifName,notifParams, mymanagers[0])

def data_handler2(notifName, notifParams):
    handle_data(notifName,notifParams, mymanagers[1])

data_handlers = [data_handler1,data_handler2]


#----------------------------------------------------
# handle_data(notifName, notifParams):
#     - This function parses the Health reports recieved and puts the data into a JSON file for upload
#     - TODO: the data should be sent to the database as soon as it's recieved
#----------------------------------------------------
firstNotifHandled = False
def handle_data(notifName, notifParams, mymanager):

    global firstNotifHandled
    print "Health report recieved"
    print notifName
    print notifParams

    mac        = FormatUtils.formatMacString(notifParams.macAddress)
    hrParser   = HrParser.HrParser()
    hr    = hrParser.parseHr(notifParams.payload)
    timestamp = datetime.datetime.utcnow()

    try:
        res = mymanager.dn_getMoteConfig(notifParams.macAddress,False)
        print "MoteID: ", res.moteId,", MAC: ",res.macAddress,", AP:", res.isAP,", State:", res.state, ", Routing:", res.isRouting
        moteId = res.moteId
        isAP   = res.isAP
        isRouting = res.isRouting
        state  = res.state
    except:
        print "error connecting to mote"
        moteId = -1
        isAP   = "unknown"
        isRouting = "unknown"
        state  = "unknown"
        
    with open('datafile', 'ar+') as datafile:
        
        print timestamp
        print mac
        print res.moteId
        print str(hr)
        print type(moteId)

        #if a health notification is already in the datafile, remove the ']}' at the end of the file
        #and write a ',' so the json in datafile is formatted properly
        print firstNotifHandled
        if firstNotifHandled:
    
            datafile.seek(0, os.SEEK_END)
            pos = datafile.tell() - 1

            while pos > 0 and datafile.read(1) != "\n":
                pos -= 1
                datafile.seek(pos, os.SEEK_SET)

            if pos > 0:
                datafile.seek(pos, os.SEEK_SET)
                datafile.truncate()
                write(',\n')

        #write the health report to the datafile
        datafile.write('\n{"TIME":"' + str(timestamp) + '",')
        datafile.write('\n')
        datafile.write('"MAC" : "' + mac + '",')
        datafile.write('\n')
        datafile.write('"moteID" : "' + str(moteId) + '",')
        datafile.write('\n')
        datafile.write('"isAP" : "' + str(isAP) + '",')
        datafile.write('\n')
        datafile.write('"isRouting" : "' + str(isRouting) + '",')
        datafile.write('\n')
        datafile.write('"state" : "' + str(state) + '",')
        datafile.write('\n')
        datafile.write(str(hr))
        datafile.write('}')
        datafile.write('\n')
        datafile.write(']}')
        datafile.write('\n')

        print "health report handled successfully"

    firstNotifHandled = True

#============================ main ============================================

print( '===================================================\n')

#===== connect to the manager

ports = find_connected_devices(mymanagers[0])

result = []
port_cntr = 0

try:
    # Checking the connected networks
    print "Found Networks At :"
    for port in ports:
        try:
            mymanagers[0].connect({'port': port.strip()})
            res = mymanagers[0].dn_getNetworkConfig()
            port_cntr = 1 + port_cntr
            result.append(port.strip())
            print " network ", port_cntr," found at ", result[port_cntr-1], " with NetId ", res.networkId
            mymanagers[0].disconnect()

        except:
            print "Something wrong happend here !!!!"
            pass
except:
    print "No Connected Dust Devices Found"
    os._exit(0)

#mymanager.disconnect()
while(1):
    sel = raw_input("Enter the network's number or 'a' to connect to all : \n")
    if sel == 'a':
        portNum = 'a'
        break
    try:
        portNum = int(sel)
        if portNum > 0 and portNum <= NUMBER_OF_NETWORKS:
            break
        else:
            print("Please select a number between 1 and " + str(NUMBER_OF_NETWORKS))
    except ValueError:
       print("Please select a number between 1 and " + str(NUMBER_OF_NETWORKS))

#prepare the output file, write the first line of JSON      
with open('datafile', 'w') as datafile:
    datafile.write('{"Samples": [')
    datafile.write('\n')

if portNum == 'a':

    subscribers = []
    for p in range(port_cntr):
        connect_manager_serial(mymanagers[p],result[p] )

        # subscribe to data notifications
        subscriber = IpMgrSubscribe.IpMgrSubscribe(mymanagers[p])
        subscriber.start()

        subscriber1.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                        ],
        fun =           data_handlers[p],
        isRlbl =        True,
        )

        subscribers.append(subscriber)

else:
    connect_manager_serial(mymanagers[portNum], result[portNum-1] )
    # subscribe to data notifications
    subscriber = IpMgrSubscribe.IpMgrSubscribe(mymanagers[portNum])
    subscriber.start()
    subscriber.subscribe(
        notifTypes =    [
                            IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                        ],
        fun =           data_handlers[portNum],
        isRlbl =        True,
    )

raw_input("Enter to EXIT : \n")
os._exit(0)


currentMac     = (0,0,0,0,0,0,0,0) # start getMoteConfig() iteration with the 0 MAC address
continueAsking = True
returnVal = []



# the bellow subroutine should be done once every 15 minutes
#
while continueAsking:
    try:
        res = mymanagers[0].dn_getMoteConfig(currentMac,True)
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



