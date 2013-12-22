#############################################
# Parse AMS-IX data                         #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

import os,sys
import json
dfile='../data/ams-ix/pfxv4_nh_aspath.amsix.txt'

class rc_rib():
    def __init__(self,prefixes={}):
        self.prefixes=prefixes

def initialize_rib(rib,dfile):
    i=0
    for line in open(dfile,'r').readlines():
        tmp=line.split('|')
        pfx,nh,aspath=(tmp[0],tmp[1],tmp[2].split('\n')[0].split(' '))
        if pfx not in rib:
            rib[pfx]={}
        rib[pfx][nh]=aspath
            
        #print pfx,nh,aspath
        if i==1000:
            print i
            #break
        i+=1

def main():
    rib={}
    initialize_rib(rib,dfile)
    #print rib
    with open('amsix-rib.dat', 'w') as outfile:
        json.dump(rib,outfile,ensure_ascii=True,encoding="ascii")
    #ribn = json.load(open('amsix-rib.dat', 'r'))
    #print ribn
    
if __name__ == '__main__':
    main()