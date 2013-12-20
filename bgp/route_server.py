
#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

from peer import peer
from bgp_server import bgp_server

class route_server():
    
    def __init__(self):
        
        self.peers = {}
        
        self.peers['172.0.0.1']  = peer('172.0.0.1')
        self.peers['172.0.0.11'] = peer('172.0.0.11')
        self.peers['172.0.0.21'] = peer('172.0.0.21')
        self.peers['172.0.0.22'] = peer('172.0.0.22')
        
        self.server = None
        
    def start(self):
        
        while True:
            self.server = bgp_server()
    
            while True:
                try:
                    route = self.server.recv()
                    for peer in self.peers:
                        self.peers[peer].add_route(route)
                except:
                    print 'route_serer_error: thread ended'
                    break
    
''' main '''    
if __name__ == '__main__':
    
    my_rs = route_server()
    my_rs.start()
    
