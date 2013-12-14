#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import sys
import os
import getopt

'''Function for parsing arguments'''
def getArgs():
    logfile = '';
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h",["help", "logfile="])
    except getopt.GetoptError:
        print 'rs.py [--logfile <file name>]'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print 'rs.py [--logfile <file name>]'
            sys.exit()
        elif opt == '--logfile':
            logfile = arg
    
    if(logfile==''):
        print 'rs.py [--logfile <file name>]'
        sys.exit()
    
    return logfile

'''Write output to stdout'''
def write (data):
    sys.stdout.write(data + '\n')
    sys.stdout.flush()