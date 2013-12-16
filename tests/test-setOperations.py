################################################################################
#
#  <website link>
#
#  File:
#        test-setOperations.py
#        To stress test the set operation functionality with data from AMS-IX collector
#
#  Project:
#        Software Defined Exchange (SDX)
#
#  Author:
#        Arpit Gupta
#
#  Copyright notice:
#        Copyright (C) 2012, 2013 Georgia Institute of Technology
#              Network Operations and Internet Security Lab
#
#  Licence:
#        This file is part of the SDX development base package.
#
#        This file is free code: you can redistribute it and/or modify it under
#        the terms of the GNU Lesser General Public License version 2.1 as
#        published by the Free Software Foundation.
#
#        This package is distributed in the hope that it will be useful, but
#        WITHOUT ANY WARRANTY; without even the implied warranty of
#        MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#        Lesser General Public License for more details.
#
#        You should have received a copy of the GNU Lesser General Public
#        License along with the SDX source package.  If not, see
#        http://www.gnu.org/licenses/.
#


# SDX specific imports
from pyretic.sdx.lib.setOperation import *

# General imports
import os,sys
from ipaddr import IPv4Network
pfile='data/ams-ix/amsix.map.ebgp.nh.prefixes.txt'
hfile='data/ams-ix/amsix.map.ebgp.nh.nb.prefixes.txt'


def getNHs(hfile):
    NH_2_IP={}
    i=1
    for line in open(hfile,'r').readlines():
        if line!='\n':
            NH_2_IP[i]=line.split(' ')[0]
            i+=1
    return NH_2_IP

def getPrefixes(pfile,VNH_2_IP,prefixes_announced,prefixes):
    i=1
    prefixes_announced['pg1']={}
    plist=[]
    for line in open(pfile,'r').readlines():
        if line!='\n':
            temp=line.split(' ')
            neighbor=temp[0]
            prefix=temp[1].split('\n')[0]
            if prefix not in plist:
                plist.append(prefix)
                prefixes['p'+str(i)]=IPv4Network(prefix)
                i+=1
            if neighbor in prefixes_announced['pg1']:
                prefixes_announced['pg1'][neighbor].append(prefix)
            else:
                prefixes_announced['pg1'][neighbor]=[prefix]
    print "extracted data from file, prefixes: ",len(plist)
    # extract the unique prefixes announced
    plist=list(set(plist))
    for neighbor in prefixes_announced['pg1']:
        prefixes_announced['pg1'][neighbor]=list(set(prefixes_announced['pg1'][neighbor]))
    print "extracted the unique IP prefixes: ",len(plist)
    i=1
    """
    for prefix in plist:
        pname='p'+str(i)
        prefixes[pname]=IPv4Network(prefix)
        i+=1
        print i
    print prefixes
    """
    #print prefixes_announced

def initializeData():
    print "Initializing data for stress test"
    VNH_2_IP={}
    prefixes={}
    prefixes_announced={}
    VNH_2_IP=getNHs(hfile)
    print VNH_2_IP
    getPrefixes(pfile,VNH_2_IP,prefixes_announced,prefixes)
    
def main():
    print "Starting the setOperations stress test"
    initializeData()

if __name__ == '__main__':
    main()
