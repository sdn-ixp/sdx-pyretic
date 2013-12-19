#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import json
from rib import rib

class peer():
    
    def __init__(self,ip):
        
        self.ip = ip
        self.input_rib = rib()
        self.local_rib = rib()
         
    def add_route(self,route):
        
        route = json.loads(route)

        origin = None
        as_path = None
        med = None
        atomic_aggregate = None
        
        if ('neighbor' in route):
            if ('ip' in route['neighbor']):
                # Only add to the RIB if it's from a participant who is not ourselves.
                if (route['neighbor']['ip'] != self.ip):
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
                                    self.input_rib[prefix] = (announce['ipv4 unicast'][prefix]['next-hop'],origin,','.join(map(str,as_path)),med,atomic_aggregate)
                                    self.input_rib.commit()
                                    bp = self.input_rib.decision_process(prefix)
                                    if (NULL != bp)
                                        self.local_rib.del_route(prefix)
                                        self.local_rib[prefix] = bp
                                        self.local_rib.commit()
                                        self.announce_route(bp)

                        elif ('withdraw' in route['neighbor']['update']):
                            withdraw = route['neighbor']['update']['withdraw']
                            if ('ipv4 unicast' in withdraw):
                                for prefix in withdraw['ipv4 unicast'].keys():
                                    self.input_rib.delete(prefix,route['neighbor']['ip])
                                    self.input_rib.commit()
                                    #TODO: need to deal with the local_rib's side of things and reannouncements

        elif ('notification' in route):
            if ('shutdown' == route['notification']):
                self.input_rib.delete_all()
                self.input_rib.commit()
                                    
    def get_route(self,prefix):
        
        return self.input_rib.get(prefix)
    
    def get_all_routes(self):
        
        return self.input_rib.get_all()
    
    def del_route(self,prefix):
        
        self.input_rib.delete(prefix)
        self.input_rib.commit()
    
    def filter_route(self,item,value):
        
        return self.input_rib.filter(item,value)
    
    def announce_route(self,route):
        
        #TODO: add logic for announcing routes
        #build up route to send

        
        pass

''' main '''    
if __name__ == '__main__':
    
    mypeer = peer('172.0.0.22')
    
    route = '''{ "exabgp": "2.0", "time": 1387421714, "neighbor": { "ip": "172.0.0.22", "update": { "attribute": { "origin": "igp", "as-path": [ [ 300 ], [ ] ], "med": 0, "atomic-aggregate": false }, "announce": { "ipv4 unicast": { "140.0.0.0/16": { "next-hop": "172.0.0.22" }, "150.0.0.0/16": { "next-hop": "172.0.0.22" } } } } } }'''
    
    mypeer.add_route(route)
    
    print mypeer.filter_route('as_path', '300')
    

