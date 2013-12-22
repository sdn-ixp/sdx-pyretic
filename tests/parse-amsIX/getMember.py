#############################################
# Parse AMS-IX Member                       #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

import os,sys
import json
from netaddr import *   

mfile='../data/ams-ix/member-list.txt'
nfile='../data/ams-ix/amsix.map.ebgp.nh.nb.prefixes.txt'
i=0
attributes=[]
member_list={}
mem_ip={}
init=False
if init==True:
    for line in open(mfile,'r').readlines():
        if i==0:
            attributes=line.split('\n')[0].split('\t')
            print attributes
        else:
            tmp=line.split('\n')[0].split('\t')
            print tmp[0]
            if tmp[0] not in member_list:                
                member_list[tmp[0]]=[]
                mem_ip[tmp[0]]=[]
            mem_info={}
            ip=tmp[5].split('/')[0]
            if ip not in mem_ip[tmp[0]]:
                mem_ip[tmp[0]].append(ip)
            for j in range(0,len(tmp)):
                mem_info[attributes[j]]=str(tmp[j])
            member_list[tmp[0]].append(mem_info)
        i+=1
    with open('amsix-member.dat', 'w') as outfile:
        json.dump(member_list,outfile,ensure_ascii=True)
    print mem_ip
    with open('amsix-memberIP.dat', 'w') as outfile:
        json.dump(mem_ip,outfile,ensure_ascii=True)

member_info=json.load(open('amsix-member.dat', 'r'))  
member_ip=json.load(open('amsix-memberIP.dat', 'r')) 
#nhs=(json.load(open('amsix-nhs.dat', 'r'))).values()[0]

nhs=[]
for line in open(nfile,'r').readlines():
    nhs.append(str(line.split('\n')[0].split(' ')[0]))
#print nhs

counter=0
lenth=0
for member in member_ip:
    if len(member_ip[member])>1:
        counter+=1
        lenth+=len(member_ip[member])
print float(lenth)/counter

nhs_clubbed={}
for member in member_ip:
    for ip in member_ip[member]:
        if ip in nhs:
            if member not in nhs_clubbed:
                nhs_clubbed[member]=[]
            nhs_clubbed[member].append(ip)
            """
            if len(nhs_clubbed[member])>1:
                print member,nhs_clubbed[member]
            """
with open('amsix-nhs-clubbed.dat', 'w') as outfile:
    json.dump(nhs_clubbed,outfile,ensure_ascii=True)
print nhs_clubbed

    
                    

