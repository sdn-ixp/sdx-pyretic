
#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import json
from peer import peer as Peer
from server import server as Server

from pyretic.sdx.utils import get_participants_ports_list
from pyretic.sdx.lib.bgp_interface import *
from pyretic.sdx.bgp.peer import *

class route_server():
    
    def __init__(self,event_queue,ready_queue,sdx):
        
        self.event_queue = event_queue
        self.ready_queue = ready_queue
        self.sdx = sdx
        
        participants_ports_list = get_participants_ports_list(sdx.participants)
        
        ''' Create and assign participant RIBs '''
        for participant_name in sdx.participants:
            self.sdx.participants[participant_name].rs_client = Peer(participants_ports_list[participant_name])
            
        self.server = None
        
    def start(self):
        
        self.server = Server()
    
        while True:
            route = self.server.receiver_queue.get()
            route = json.loads(route)
                
            # TODO: check the RIB update flow with others ...
            # At the moment, I am updating the RIB and will attach next-hop to the announcement at the end
                
            updates = []
                
            for participant_name in self.sdx.participants:
                updates.append(self.sdx.participants[participant_name].rs_client.update(route))
           
            bgp_trigger_update(self.event_queue,self.ready_queue)
           
            # TODO: Need to perform some testing to verify performance affect due to updates
            
            for update in updates:
                if (update is None):
                    continue
                if ('announce' in update):
                    for VNH in self.sdx.VNH_2_pfx:
                        if(update['announce']['prefix'] in list(self.sdx.VNH_2_pfx[VNH])):
                            self.server.sender_queue.put(announce_route(update['announce'],self.sdx.VNH_2_IP[VNH]))
                            break
                elif ('withdraw' in update):
                    for VNH in self.sdx.VNH_2_pfx:
                        if(update['withdraw']['prefix'] in list(self.sdx.VNH_2_pfx[VNH])):
                            self.server.sender_queue.put(withdraw_route(update['withdraw'],self.sdx.VNH_2_IP[VNH]))
                            break
            
''' main '''    
if __name__ == '__main__':
    
    participants_list = {'A': ['172.0.0.1', '172.0.0.11'], 'B': ['172.0.0.21', '172.0.0.22']}
    
    my_rs = route_server(participants_list)
    my_rs.start(None,None)
    
