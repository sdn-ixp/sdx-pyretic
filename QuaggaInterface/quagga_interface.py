#############################################
# SDX-Quagga Integration                    #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

import socket
import threading
import SocketServer
import json
from bgp_update import*
from json_coders import*


def process_update(bgp_update):
    return 'OK'

def process_json(message):
    print message
    jmesg=MyDecoder().decode(message)
    #print 'Decoded Update Object: ',update_msg
    # Apply the logic to analyse this BGP Update and

    print jmesg.prefix.address,jmesg.prefix.prefixlen

    return json.dumps(jmesg,cls=ComplexEncoder,
            default=convert_to_builtin_type)

def main():
    message = ''
    print "Quagga Interface Started"
    # Set up the Server
    HOST,port="localhost",9998
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST,port))
    s.listen(1)

    while True:
        message=''

        conn,addr = s.accept()
        print 'Received connection from ',addr

        while True:
            data = conn.recv(1024)

            if not data:
                conn.close()
                break

            message = message + data
            return_value = process_json(message)
            #return_value = "OK"
            #print return_value
            conn.sendall(return_value)
            print "Sent the message back"
            #parse_message(message)



if __name__ == "__main__":
    main()

