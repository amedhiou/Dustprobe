#!/uer/bin/python

#============================ imports =====================================

import sys
import os
import re
import serial
import glob
import time
import requests
import json 
import yaml
import getpass
import datetime
import csv
from time import sleep
from Queue import Queue
from threading import Thread

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

try:
    session = requests.Session()
except:
    print ("Your installation does not allow this application to run:\n")
    print ("Please install 'requests' for python")
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

#============================ Global Variables ================================

networkIds  = []
reportQueue = Queue(maxsize=0)
queueReady  = True
queueBusy   = False
session     = requests.Session()
mymanagers  = []
moteDict    = {}
for i in range(NUMBER_OF_NETWORKS):
    mymanagers.append(IpMgrConnectorSerial.IpMgrConnectorSerial())
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
            print port
            s = serial.Serial(port,
                baudrate = 115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=2)

            s.flushOutput()
            mes = s.read(10)

            if mes:
                print "Found new Device at :", port
                print "message recieved from port" 
                #print mes.decode('unicode-escape')
                mes_inhex=":".join("{:02x}".format(ord(c)) for c in mes)
                print mes_inhex
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
 

def checkQueue():
    global queueBusy

    queueBusy = True
    while(not reportQueue.empty()):
        args = reportQueue.get()
        timestamp  = datetime.datetime.utcnow()
        handle_data(args[0],args[1],args[2],args[3],timestamp)
        sleep(1)

    queueBusy = False


#-----------------------------------------------------
# data_handlers
# array of functions to be called by the subscriber on recieveing a health report.
# This way each subscriber can use the correct manager, which is required for some data
# ~~ I feel like there is a more elegant way to do this, using lamda functions or something. This works though, ill look into it later
#-----------------------------------------------------
def data_handler0(notifName, notifParams):    
    reportQueue.put([notifName,notifParams,mymanagers[0], networkIds[0]])
    if not queueBusy:
        checkQueue()

def data_handler1(notifName, notifParams):
    reportQueue.put([notifName,notifParams,mymanagers[1], networkIds[1]])
    if not queueBusy:
        checkQueue()


def data_handler2(notifName, notifParams):
    reportQueue.put([notifName,notifParams,mymanagers[2], networkIds[2]])
    if not queueBusy:
        checkQueue()

data_handlers = [data_handler0,data_handler1,data_handler2]


#-----------------------------------------------------------------------
# sendJSONtoServer(dataBaseJson)
#   - send dataBaseJson to the dustlab server to be placed in the database
#   - dataBaseJson must be a properly formatted JSON 
#------------------------------------------------------------------------
def sendJSONtoServer(dataBaseJson):
    try:
        
        response = session.post(
                'http://dustlab-dustcloud.rhcloud.com/dustlab/test/',
                data={"sample":dataBaseJson}
            )

        r = response.json()
        if r["SUCCESS"] == True:
            print "success adding to database\n"
            return
        else:
            print "failed to put into database"
    except:
        pass
#----------------------------------------------------
# handle_data(notifName, notifParams):
#     - This function parses the Health reports recieved and puts the data into a JSON file for upload
#     - TODO: the data should be sent to the database as soon as it's recieved
#----------------------------------------------------
firstNotifHandled = False
def handle_data(notifName, notifParams, mymanager, networkID, timestamp):


    print notifName, "recieved from network: " + str(networkID)

    ############# NotifHealthReport ###################
    if notifName == "notifHealthReport":

        global firstNotifHandled
        global queueReady

        mac        = FormatUtils.formatMacString(notifParams.macAddress)
        mac = mac.upper()
        hrParser   = HrParser.HrParser()
        hr         = hrParser.parseHr(notifParams.payload)
        

        try:
            res = mymanager.dn_getMoteConfig(notifParams.macAddress,False)
            print "MoteID: ", res.moteId,", MAC: ",mac,", AP:", res.isAP,", State:", res.state, ", Routing:", res.isRouting
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

        try:
            settingsDict = moteDict[str(mac)]
        except KeyError:
            print "macAddress: " + str(mac) + " not found in settings"

        if 'settingsDict' not in locals():
            try:
                settingsDict = moteDict[str(moteId)]
            except KeyError:
                print  "moteId: " + str(moteId) + " not found in settings"


        
        if 'settingsDict' in locals():
            if settingsDict['moteId'] != str(moteId):
                print "warning: moteId (" + settingsDict['moteId'] + ") in settings does not match actual moteId: " + str(moteId)
            x = settingsDict['x']
            y = settingsDict['y']
            z = settingsDict['z']
            substrate = settingsDict['substrate']
            antenna   = settingsDict['antenna']
        else:
            x = '-'
            y = '-'
            z = '-'
            substrate = 'unknown'
            antenna   = 'unknown'

        print "x ", x, "y ", x, "z ", z, "substrate: ", substrate, "antenna: ", antenna

        dataBaseJsonString  = ""
        dataBaseJsonString += "{'Time': "      + "'" + str(timestamp) + "' ,"
        dataBaseJsonString += "'networkID' : " + str(networkID) + ","
        dataBaseJsonString += "'MAC' : "       + mac            + ","
        dataBaseJsonString += "'moteID' : "    + str(moteId)    + ","
        dataBaseJsonString += "'isAP' : "      + str(isAP)      + ","
        dataBaseJsonString += "'isRouting' : " + str(isRouting) + ","
        dataBaseJsonString += "'state' : "     + str(state)     + ","

        if 'settingsDict' in locals():
            dataBaseJsonString += "'x' : "         + str(x)         + ","
            dataBaseJsonString += "'y' : "         + str(y)         + ","
            dataBaseJsonString += "'z' : "         + str(z)         + ","
            dataBaseJsonString += "'substrate' : " + str(substrate) + ","
            dataBaseJsonString += "'antenna' : "   + str(antenna)   + ","

        dataBaseJsonString += "'hr' : "        + str(hr)
        dataBaseJsonString += '}'

        dataBaseYaml = yaml.load(dataBaseJsonString)
        dataBaseJson = json.dumps(dataBaseYaml)
            
        with open('datafile', 'ar+') as datafile:
            
            print timestamp
            print "mac:" + mac
            print "moteid: " + str(moteId)
            print "payload: "
            print hrParser.formatHr(hr)
            

            #if a health notification is already in the datafile, remove the ']}' at the end of the file
            #and write a ',' so the json in datafile is formatted properly
            if firstNotifHandled:

                datafile.seek(0, os.SEEK_END)
                pos = datafile.tell() - 1

                while pos > 0 and datafile.read(1) != "\n":
                    pos -= 1
                    datafile.seek(pos, os.SEEK_SET)

                if pos > 0:
                    datafile.seek(pos, os.SEEK_SET)
                    datafile.truncate()
                    datafile.write(',\n')

            #write the health report to the datafile
            '''
            datafile.write("\n{'Time':"     + str(timestamp) + ",")
            datafile.write('\n')
            datafile.write("'networkID' : " + str(networkID) + ",")
            datafile.write('\n')
            datafile.write("'MAC' : "       + mac            + ",")
            datafile.write('\n')
            datafile.write("'moteID' : "    + str(moteId)    + ",")
            datafile.write('\n')
            datafile.write("'isAP' : "      + str(isAP)      + ",")
            datafile.write('\n')
            datafile.write("'isRouting' : " + str(isRouting) + ",")
            datafile.write('\n')
            datafile.write("'state' : "     + str(state)     + ",")
            datafile.write('\n')
            datafile.write(str(hr))
            datafile.write('}')
            datafile.write('\n')
            datafile.write(']}')
            datafile.write('\n')
            '''

            datafile.write('\n' + str(dataBaseJson))
            datafile.write('\n')
            datafile.write(']}')
            datafile.write('\n')

        print "health report handled successfully and added to datafile\n"
        


        sendJSONtoServer(dataBaseJson)

        firstNotifHandled = True


def remoteLogin():

    #attempt to login
    while(1):
        username = raw_input("User name:")
        password = getpass.getpass(prompt="password:")

        # log in session
        data = {"username":username, "password":password}
        response = session.post(
            'http://dustlab-dustcloud.rhcloud.com/dustlab/remoteLogin/',
            data=data
        )

        r = response.json()
        if r["LOGIN"] == True:
            break

        else:
            print "incorrect username/password"

def loadSettings():

    with open ('Settings/settings.csv', 'r') as settings:
        reader = csv.reader(settings, delimiter=',', quotechar='"')

        for row in reader:
            settingsDict = {}
            key = "none"
    
            moteId     = row[0]
            if moteId:
                settingsDict['moteId'] = moteId
                key = moteId
            macAddress = row[1]
            macAddress = macAddress.upper()
            if macAddress:
                settingsDict['macAddress'] = macAddress
                key = macAddress

            settingsDict['x'] = row[2]
            settingsDict['y'] = row[3]
            settingsDict['z'] = row[4]

            settingsDict['substrate'] = row[5]
            settingsDict['antenna']   = row[6]

            moteDict[key] = settingsDict

            
        



def checkConnectedPorts(mymanager, ports):

    result = []
    try:
        # Checking the connected networks
        print "Found Networks At :"
        objfile = open('obj/portList', 'w')
        port_cntr = 0
        for port in ports:
            try:
                mymanager.connect({'port': port.strip()})
                res = mymanager.dn_getNetworkConfig()
                port_cntr = port_cntr + 1
                result.append(port.strip())
                networkIds.append(res.networkId)
                print " network ", port_cntr," found at ", result[port_cntr-1], " with NetId ", res.networkId

                objfile.write(port.strip()+'\n')

                mymanager.disconnect()

            except:
                print "Unable to connect to port " + str(port.strip())
                
    except:
        print "No Connected Dust Devices Found"
        os._exit(0)


    objfile.close()


    if port_cntr <= 0:
        print "No Connected Dust Devices Found"
        os._exit(0)

    return result

#repeatedly ask the user for valid input to select a port to connect to
#input of 'a' connects to all
#inpurt of 'q' quits
def getUsersSelection(port_cntr):
    while(1):
        sel = raw_input("Enter the network's number or 'a' to connect to all. Enter 'q' to quit : \n")
        if sel == 'a':
            portNum = 'a'
            break
        if sel == 'q':
            os._exit(0)
        try:
            portNum = int(sel)
            if portNum > 0 and portNum <= NUMBER_OF_NETWORKS:
                break
            else:
                print("Please select a number between 1 and " + str(port_cntr))
        except ValueError:
           print("Please select a number between 1 and " + str(port_cntr))

    return portNum

#prepare the output file, write the first line of JSON
#if it doesnt exist create it.
def prepareDataFile():
    
    with open('datafile', 'w') as datafile:
        datafile.write('{"Samples": [')
        datafile.write('\n')

#connect to the port(s) selected by the user
#and start the subscriber listening for health reports (NOTIFHEALTHREPORT)
#if portNum is 'a' connect to all available devices
def connectToPort(portNum, connectedPorts):

    port_cntr = len(connectedPorts)

    if portNum == 'a':

        subscribers = []
        for p in range(port_cntr):
            connect_manager_serial(mymanagers[p],connectedPorts[p] )

            # subscribe to data notifications
            subscriber = IpMgrSubscribe.IpMgrSubscribe(mymanagers[p])
            subscriber.start()

            subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                            ],
            fun =           data_handlers[p],
            isRlbl =        True,
            )

            subscribers.append(subscriber)

    else:
        connect_manager_serial(mymanagers[portNum-1], connectedPorts[portNum-1] )
        # subscribe to data notifications
        subscriber = IpMgrSubscribe.IpMgrSubscribe(mymanagers[portNum-1])
        subscriber.start()


        subscriber.subscribe(
            notifTypes =    [
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFHEALTHREPORT,
                                IpMgrSubscribe.IpMgrSubscribe.NOTIFEVENT,
                            ],
            fun =           data_handlers[portNum-1],
            isRlbl =        True,
        )




def testThread():
    global printflag
    global quitflag
    global askflag
    global warningflag
    
    myman = mymanagers[0]
    mac = [0, 23, 13, 0, 0, 48, 10, 185]
    mac = [0, 23, 13, 0, 0, 96, 6, 240]

    macAddress = [0,0,0,0,0,0,0,0]

    while(not quitflag):

        if askflag:
            macAddress = [0,0,0,0,0,0,0,0]
            while(1):
                try:
                    res = myman.dn_getMoteConfig(macAddress,True)
                    RC = res.RC
                    moteId = res.moteId
                    isAP   = res.isAP
                    isRouting = res.isRouting
                    state  = res.state
                    macAddress = res.macAddress

                    if not isAP and printflag:
                        print "mac", macAddress,
                        print "\t",
                        print "moteid ", moteId,
                        print "Routing",isRouting,
                        print "AP",isAP,
                        if state != 4:
                            print "state change",state,
                        else:
                            print "state",state,
                        if RC != 0:
                            print "RC change",RC
                        else:
                            print "RC",RC

                    if warningflag:
                        if state != 4:
                            print mac," state change",state
                        if RC != 0:
                            print mac," RC change",RC

                except:
                    break
                    print ""



            








#============================ main ============================================

if __name__ == "__main__":

    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))

    #athenticate user to access database
    remoteLogin()

    #load the settings file from ./Settings/settings
    loadSettings()

    #connect to the manager
    #ports: list of all found ports on this device
    ports = find_connected_devices(mymanager)
    connectedPorts = checkConnectedPorts(mymanager, ports)

    #repeatedly ask the user for valid input to select a port to connect to
    portNum = getUsersSelection(len(connectedPorts))

    #gets data file ready, prints first line of JSON to the file
    prepareDataFile()

    #connect to the port(s) selected by the user
    #and start the subscriber subcribed to 
    connectToPort(portNum, connectedPorts)

    
    '''

    quitflag = False
    printflag = False
    askflag = False
    warningflag = False

    for i in range(100):
        testthread = Thread(target = testThread)
        testthread.setDaemon(True)
        testthread.start()
        pass



    raw_input("start thread : \n")

    while(1):

        sel = raw_input("Enter to change flag : \n")

        if sel == 'q':
            quitflag = True
            break
        if sel == 'e':
            printflag = False
        if sel == 'w':
            printflag = True
        if sel == 'a':
            askflag = True
        if sel == 's':
            askflag = False
        if sel == 'p':
            warningflag = True
        if sel == 'o':
            warningflag = False

    '''

    raw_input("Enter to EXIT : \n")
    os._exit(0)




