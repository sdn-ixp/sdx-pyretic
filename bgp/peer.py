#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import json
from rib import rib

class peer():
    
    def __init__(self,ip):
        
        self.ip = ip
        
        self.rib = rib()
         
    def add_route(self,route):
        
        route = json.loads(route)
        
        origin = None
        as_path = None
        med = None
        atomic_aggregate = None
        
        if ('neighbor' in route):
            if ('ip' in route['neighbor']):
                if (route['neighbor']['ip'] == self.ip):
                    if ('update' in route['neighbor']):
                        if ('attribute' in route['neighbor']['update']):
                            attribute = route['neighbor']['update']['attribute']
                            origin = attribute['origin']
                            as_path = attribute['as-path']
                            med = attribute['med']
                            atomic_aggregate = attribute['atomic-aggregate']
                        if ('announce' in route['neighbor']['update']):
                            announce = route['neighbor']['update']['announce']
                            if ('ipv4 unicast' in announce):
                                for prefix in announce['ipv4 unicast'].keys():
                                    self.rib[prefix] = (announce['ipv4 unicast'][prefix]['next-hop'],origin,','.join(map(str,as_path)),med,atomic_aggregate)
                                    self.rib.commit()
                        elif ('withdraw' in route['neighbor']['update']):
                            withdraw = route['neighbor']['update']['withdraw']
                            if ('ipv4 unicast' in withdraw):
                                for prefix in withdraw['ipv4 unicast'].keys():
                                    self.rib.delete(prefix)
                                    self.rib.commit()
        elif ('notification' in route):
            if ('shutdown' == route['notification']):
                self.rib.delete_all
                self.rib.commit()
                                    
    def get_route(self,prefix):
        
        return self.rib.get(prefix)
    
    def get_all_routes(self):
        
        return self.rib.get_all()
    
    def del_route(self,prefix):
        
        self.rib.delete(prefix)
    
    def filter_route(self,item,value):
        
        return self.rib.filter(item,value)
    
    def announce_route(self):
        
        #TODO: add logic for announcing routes
        
        pass
    
''' main '''    
if __name__ == '__main__':
    
    mypeer = peer('172.0.0.22')
    
    route = '''{ "exabgp": "2.0", "time": 1387421714, "neighbor": { "ip": "172.0.0.22", "update": { "attribute": { "origin": "igp", "as-path": [ [ 300 ], [ ] ], "med": 0, "atomic-aggregate": false }, "announce": { "ipv4 unicast": { "140.0.0.0/16": { "next-hop": "172.0.0.22" }, "150.0.0.0/16": { "next-hop": "172.0.0.22" } } } } } }'''
    
    mypeer.add_route(route)
    
    print mypeer.filter_route('as_path', '300')
    

