import sys
import os
import re
import serial
import glob
import time



def find_connected_devices():
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

    print "Scanning for avaible networks ..."
    result = []
    port_cntr = 0
    
    # This part needs to be changed
    # At this point I will hard code the port name
    # and will not scan com ports
    for port in ports:
        print (port)
        try:
            s = serial.Serial(port,
                baudrate = 115200,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=3)

            
            s.flushOutput()
            mes = s.read(10)

            #s.write('r')

            if mes:
                print("message recieved from port")
                print(mes.decode('unicode-escape').encode('utf8'))
                print(mes.decode('unicode-escape'))
                print(mes)

                ss=":".join("{:02x}".format(ord(c)) for c in mes)
                
                print(ss)
                result.append(port)
            s.close()
        except serial.SerialException as e:
            pass
        except OSError as e:
            pass
    return result

if __name__ == "__main__":
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..', '..'))

    res = find_connected_devices()

    print(res)