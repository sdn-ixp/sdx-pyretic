from pyretic.lib.corelib import *
from pyretic.lib.std import *

''' Get IP to MAC list '''
def get_ip_mac_list(ip_list,mac_list):
    
    # TODO: why we have this extra value in the header, i.e., VNH, that needs to ignored.

    ip_mac_list={}
    
    for key in ip_list:
        
        if (key=='VNH'): # Ignoring VNH key (not sure why)
            continue
        
        ip_mac_list[IPAddr(ip_list[key])]=EthAddr(mac_list[key])
        
    return ip_mac_list

''' Get participant to ports list '''
def get_participants_ports_list(participants):
    participants_list = {}
    
    for participant_name in participants:
        participants_list[participant_name] = []
                            
        for port in participants[participant_name].phys_ports:
            participants_list[participant_name].append(str(port.ip))
            
    return participants_list
        

