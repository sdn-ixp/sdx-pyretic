
#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import json
from peer import peer as Peer
from server import server as Server
#from decision_process_simple import decision_process_simple as decision_process
from decision_process import decision_process

from pyretic.sdx.utils import get_participants_ports_list
from pyretic.sdx.lib.bgp_interface import *
from pyretic.sdx.bgp.peer import *

class route_server():
    
    def __init__(self,event_queue,ready_queue,sdx):
        
        self.event_queue = event_queue
        self.ready_queue = ready_queue
        self.server = Server()
        
        self.sdx = sdx
        self.sdx.server = self.server
        
        participants_ports_list = get_participants_ports_list(sdx.participants)
        
        ''' Create and assign participant RIBs '''
        for participant_name in sdx.participants:
            self.sdx.participants[participant_name].rs_client = Peer(participants_ports_list[participant_name])
        
    def start(self):
        
        self.server.start()
    
        while True:
            route = self.server.receiver_queue.get()
            route = json.loads(route)
                
            # TODO: check the RIB update flow with others ...
            # At the moment, I am updating the RIB and will attach next-hop to the announcement at the end
                
            updates = []
            
            # Update RIBs
            for participant_name in self.sdx.participants:
                route_list = self.sdx.participants[participant_name].rs_client.update(route)
                for route_item in route_list:
                    updates.extend(decision_process(self.sdx.participants,route_item))
                    
            # Check for withdraw routes
            for update in updates:
                if (update is None):
                    continue
                elif 'withdraw' in update:
                    for VNH in self.sdx.VNH_2_pfx:
                        if(update['withdraw']['prefix'] in list(self.sdx.VNH_2_pfx[VNH])):
                            self.server.sender_queue.put(withdraw_route(update['withdraw'],self.sdx.VNH_2_IP[VNH]))
                            break
           
            # Trigger policy updates
            bgp_trigger_update(self.event_queue,self.ready_queue)
           
            # Check for announced routes         
            if (updates):
                # TODO: need to correct this glue logic
                for VNH in self.sdx.VNH_2_pfx:
                    for prefix in list(self.sdx.VNH_2_pfx[VNH]):
                        for paticipant_name in self.sdx.participants:
                            route = self.sdx.participants[paticipant_name].rs_client.get_route('local',prefix)
                            if route:
                                self.server.sender_queue.put(announce_route(route,self.sdx.VNH_2_IP[VNH]))
                                break

''' main '''    
if __name__ == '__main__':
    
    participants_list = {'A': ['172.0.0.1', '172.0.0.11'], 'B': ['172.0.0.21', '172.0.0.22']}
    
    my_rs = route_server(participants_list)
    my_rs.start(None,None)
    
