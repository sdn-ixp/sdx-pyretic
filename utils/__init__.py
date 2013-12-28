from pyretic.lib.corelib import *
from pyretic.lib.std import *

def get_ip_mac_list(ip_list,mac_list):
    
    # TODO: why we have this extra value in the header, i.e., VNH, that needs to ignored.

    ip_mac_list={}
    
    for key in ip_list:
        
        if (key=='VNH'): # Ignoring VNH key (not sure why)
            continue
        
        ip_mac_list[IPAddr(ip_list[key])]=EthAddr(mac_list[key])
        
    return ip_mac_list

