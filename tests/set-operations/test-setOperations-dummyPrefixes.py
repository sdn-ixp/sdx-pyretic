#############################################
# Set Operations on IP Prefixes             #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

from pyretic.sdx.lib.setOperation import *

# General imports
import os,sys,random
from ipaddr import IPv4Network
import cProfile
import pstats

def generate_part_2_prefix(npart,npfx,ntot):
    part_2_prefix={}
    for part in range(1,npart+1):        
        part_2_prefix[part]=[]
        for peer in range(1,npart):
            tmp1=[]
            while len(tmp1)<npfx:
                tmp2=random.randint(1,ntot)
                if tmp2 not in tmp1:                    
                    tmp1.append(tmp2)
            
            part_2_prefix[part].append(tmp1)
    return part_2_prefix
                
            

def main():
    print "Starting the test with dummy prefixes"
    nParticipant=32
    nPrefix_per_set=1000
    total_prefixes=(nParticipant-1)*nPrefix_per_set
    part_2_prefix=generate_part_2_prefix(nParticipant,nPrefix_per_set,total_prefixes)
    #print part_2_prefix
    print "started"
    #prefix_decompose(part_2_prefix)
    #lcs_parallel(part_2_prefix)
    lcs_multiprocess(part_2_prefix)
    print "Completed"
    #print part_2_prefix
    
if __name__ == '__main__':
    
    cProfile.run('main()', 'restats')

    p = pstats.Stats('restats')
    p.strip_dirs().sort_stats(-1).print_stats()
    