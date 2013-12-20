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

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

# SDX specific imports
from pyretic.sdx.lib.setOperation import *

# General imports
import os,sys
from redis import Redis
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
                if i%1000==0:
                    print '...'

            if neighbor in prefixes_announced['pg1']:
                prefixes_announced['pg1'][neighbor].append(prefix)
            else:
                prefixes_announced['pg1'][neighbor]=[prefix]
            if i%10000==0:
                    break
    print "extracted data from file, prefixes: ",len(plist)
    # extract the unique prefixes announced
    plist=list(set(plist))
    for neighbor in prefixes_announced['pg1']:
        prefixes_announced['pg1'][neighbor]=list(set(prefixes_announced['pg1'][neighbor]))
    print "extracted the unique IP prefixes: ",len(plist)
    return plist


def get_part_2_prefix(prefixes_announced):
    part_2_prefix={}
    for participant in prefixes_announced['pg1']:
        part_2_prefix[participant]=[]
        for prefix in prefixes_announced['pg1'][participant]:
            part_2_prefix[participant].append([prefix])
    return part_2_prefix

def initializeData():
    print "Initializing data for stress test"
    VNH_2_IP={}
    prefixes={}
    prefixes_announced={}
    VNH_2_IP=getNHs(hfile)
    #print VNH_2_IP
    plist=getPrefixes(pfile,VNH_2_IP,prefixes_announced,prefixes)
    part_2_prefix=get_part_2_prefix(prefixes_announced)
    return plist,prefixes,VNH_2_IP,prefixes_announced,part_2_prefix
    
def main():
    print "Starting the setOperations stress test"
    plist,prefixes,VNH_2_IP,prefixes_announced,part_2_prefix=initializeData()
    
    print part_2_prefix.keys()
    r0=Redis(db=0)
    for participant in part_2_prefix:
        r0.set(participant,part_2_prefix[participant])
    r0.bgsave()
    print "Starting the set operation with following parameters:"
    print "# participants:",len(prefixes_announced['pg1'].keys()),", # prefixes:",len(plist)
    start_setops=time.time()
    #part_2_prefix_updated=prefix_decompose(part_2_prefix)
    print "Execution Time: ",time.time()-start_setops,' seconds'
    
    
    
    

if __name__ == '__main__':
    main()
