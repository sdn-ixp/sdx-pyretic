#############################################
# Parse AMS-IX data                         #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

import os,sys
import json
import random
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
        if i%1000==0:
            print i
            #if i==1000000:
            #    break
            #break
        i+=1

def main():
    init=False
    nhs=[]
    getbp=False
    getBest_paths=False
    if init==True:
        rib={}
        initialize_rib(rib,dfile)
        #print rib
        with open('amsix-rib.dat', 'w') as outfile:
            json.dump(rib,outfile,ensure_ascii=True,encoding="ascii")
    elif getbp==True:
        rib = json.load(open('amsix-rib.dat', 'r'))
        print len(rib)
        announced={}
        bp={}
        i=0
        for pfx in rib:
            i+=1
            bestpath={}
            #print pfx
            for nh in rib[pfx]:
                if nh not in nhs:
                    nhs.append(nh)
                tmp=len(rib[pfx][nh])
                if tmp not in bestpath:
                    bestpath[tmp]=[]
                bestpath[tmp].append(nh)
                if nh not in announced:
                    announced[nh]=[]
                announced[nh].append(pfx)
            minl=min(bestpath.keys())
            bp[pfx]=bestpath[minl]
            if i%1000==0:
                print i
        #print bp
        with open('amsix-bp.dat', 'w') as outfile:
            json.dump(bp,outfile,ensure_ascii=True,encoding="ascii")
        with open('amsix-nhs.dat', 'w') as outfile:
            json.dump({1:nhs},outfile,ensure_ascii=True,encoding="ascii")
    elif getBest_paths==True:
        rib = json.load(open('amsix-rib.dat', 'r'))
        bp = json.load(open('amsix-bp.dat', 'r'))
        nhs = json.load(open('amsix-nhs-clubbed.dat', 'r'))
        nhs=nhs.values()
        best_paths={}
        i=1
        for plist in nhs:
            print i,plist
            participant=plist[0]
            i+=1
            best_paths[participant]={}
            for prefix in bp:
                if participant not in rib[prefix].keys():
                    selected=bp[prefix][random.randint(0, len(bp[prefix])-1)]
                    if selected not in best_paths[participant]:
                        best_paths[participant][selected]=[]
                    best_paths[participant][selected].append(prefix)
            """
            for parts in best_paths[participant]:
                print parts,len(best_paths[participant][parts])
            break
            """
        with open('amsix-best_paths.dat', 'w') as outfile:
            json.dump(best_paths,outfile,ensure_ascii=True,encoding="ascii")

    else:
         best_paths=json.load(open('amsix-best_paths.dat', 'r'))
         print len(best_paths)
if __name__ == '__main__':
    main()
