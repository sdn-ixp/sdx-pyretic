
#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import json
from peer import peer as Peer
from server import server as Server
from pyretic.sdx.lib.core import sdx_update_route

class route_server():
    
    def __init__(self, peers_list):
        
        self.peers = {}
        self.peers_list = peers_list
        
        self.server = None
        
    def start(self,event_queue,sdx):
        
        # TODO: resolve sql-lite multi-threading issue - MS
        for peer_item in self.peers_list:
            if (peer_item not in self.peers.keys()):
                self.peers[peer_item] = Peer(peer_item)
                
        self.server = Server()
    
        while True:
            try:
                route = self.server.receiver_queue.get()
                route = json.loads(route)
                
                updated_route = sdx_update_route(sdx,route,event_queue)
                
                for peer in self.peers:
                    self.peers[peer].update(updated_route,self.server.sender_queue)
            except:
                print 'route_sever_error: thread ended'
                break
    
''' main '''    
if __name__ == '__main__':
    
    peers_list = ['172.0.0.1', '172.0.0.11', '172.0.0.21', '172.0.0.22']
    
    my_rs = route_server(peers_list)
    my_rs.start(None,None)
    
