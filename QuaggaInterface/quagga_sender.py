#############################################
# SDX-Quagga Integration                    #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import socket
import sys
import json
import re
from bgp_update import *
from json_coders import *

def modify_jsonMessage(json_message):

    # Create socket to send data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to server
    s.connect(("localhost",9998)) # hard coded for now
    #bufsize = len(json_message)

    # Send data
    totalsent = 0
    dmp=json.dumps(json_message, cls=ComplexEncoder,default=convert_to_builtin_type)
    s.sendall(dmp)
    #s.sendall(json.dumps(json_message, cls=ComplexEncoder))

    # Receive return value
    recvdata=s.recv(1024)
    #while True:
    #    data = s.recv(1024)
    #    print data
    #    if not data:
    #        s.close()
    #        break
    #    recvdata=recvdata+data

    return recvdata

def update_to_json(update_message):
    return update_message
    #return dict(type='update',update=update_message.reprJSON(),rib='')

def json_to_update(json_message):
    return info()

def modify_updateMessage(update_message):

    # This function will translate an update message into JSON one.
    # Send it to SDX controller, Controller will process this message
    # and send a JSON message with modifications. This function will
    # then recreate an update message from the returned JSON message

    json_message=update_to_json(update_message)
    rjson_message=modify_jsonMessage(json_message)
    print rjson_message
    mupdate_message=json_to_update(rjson_message)

def main():

    print "Send an UPDATE Message"
    # Create an update packet
    aspath_test=aspath(0,'1000,1002,1030')
    attr_test=attr(aspath=aspath_test)
    update_object=info(peer='172.0.0.11',attr=attr_test,uptime=10)
    jmesg=jmessage(tag='sender:quagga',type='BGP_UPDATE',
            update=update_object,prefix=prefix(address='10.0.0.0',
                prefixlen=16,family='AF_INET'))
    # get modified update message from the SDX controller
    mupdate_message=modify_updateMessage(jmesg)


if __name__ == '__main__':
    main()


