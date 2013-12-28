
#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

from peer import peer
from bgp_server import bgp_server

class route_server():
    
    def __init__(self, peers_list):
        
        self.peers = {}
        
        for peer_item in peers_list:
            if (peer_item not in self.peers.keys()):
                self.peers[peer_item]  = peer(peer_item)
        
        self.server = None
        
    def start(self):
        self.server = bgp_server()
    
        while True:
            try:
                route = self.server.receiver_queue.get()
                
                for peer in self.peers:
                    self.peers[peer].update(route,self.server.sender_queue)
            except:
                print 'route_serer_error: thread ended'
                break
    
''' main '''    
if __name__ == '__main__':
    
    peers_list = ['172.0.0.1', '172.0.0.11', '172.0.0.21', '172.0.0.22']
    
    my_rs = route_server(peers_list)
    my_rs.start()
    
