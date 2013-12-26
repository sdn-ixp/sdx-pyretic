#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import json
import sqlite3
from rib import rib
from decision_process import decision_process

class peer():
    
    def __init__(self,ip):
        
        self.ip = ip
        self.rib = {"input": rib("input"),
                    "local": rib("local")}
         
    def update(self,route,queue):
        
        route = json.loads(route)

        origin = None
        as_path = None
        med = None
        atomic_aggregate = None
        
        if ('neighbor' in route):
            if ('ip' in route['neighbor']):
                # Only add to the RIB if it's from a participant who other than myself.
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
                                    self.rib["input"][prefix] = (announce['ipv4 unicast'][prefix]['next-hop'],
                                                                 origin,
                                                                 ' '.join(map(str,as_path)).replace('[','').replace(']',''),
                                                                 med,
                                                                 atomic_aggregate)
                                    self.rib["input"].commit()
                                    best_route = decision_process(self.rib["input"],prefix)
                                    
                                    if (best_route is not None):
                                        self.rib["local"].delete(prefix)
                                        self.rib["local"][prefix] = best_route
                                        self.rib["local"].commit()
                                        queue.put(self.announce_route(best_route))

                        elif ('withdraw' in route['neighbor']['update']):
                            withdraw = route['neighbor']['update']['withdraw']
                            if ('ipv4 unicast' in withdraw):
                                for prefix in withdraw['ipv4 unicast'].keys():
                                    deleted_route = self.rib["input"][prefix]
                                    self.rib["input"].delete(prefix)
                                    self.rib["input"].commit()
                                    self.rib["local"].delete(prefix)
                                    self.rib["local"].commit()
                                    queue.put(self.withdraw_route(deleted_route))   
                                    # TODO: clarify how the route withdrawal will work i.e., do we have to run the decision process again

        elif ('notification' in route):
            if ('shutdown' == route['notification']):
                self.rib["input"].delete_all()
                self.rib["input"].commit()
                self.rib["local"].delete_all()
                self.rib["local"].commit()
    
    def add_route(self,rib_name,prefix,attributes):
        self.rib[rib_name][prefix] = attributes
        self.rib[rib_name].commit()
    
    def add_many_routes(self,rib_name,routes):
        self.rib[rib_name].add_many(routes)
        self.rib[rib_name].commit()
                                    
    def get_route(self,rib_name,prefix):
        
        return self.rib[rib_name][prefix]
    
    def get_all_routes(self, rib_name):
        
        return self.rib[rib_name].get_all()
    
    def delete_route(self,rib_name,prefix):
        
        self.rib[rib_name].delete(prefix)
        self.rib[rib_name].commit()
        
    def delete_all_routes(self,rib_name):
        
        self.rib[rib_name].delete_all()
        self.rib[rib_name].commit()
    
    def filter_route(self,rib_name,item,value):
        
        return self.rib[rib_name].filter(item,value)
    
    def announce_route(self,route):
       
        if (isinstance(route,tuple) or isinstance(route,list)):
            value = "announce route " + route[0] + " next-hop " + route[1]
            
            if ('as_path' in route):
                value += " as-path [ " + route[3] + " ]"
                
            return value
        elif (isinstance(route,dict) or isinstance(route,sqlite3.Row)):
            value = "announce route " + route['prefix'] + " next-hop " + route['next_hop'] 
        
            if ('as_path' in route.keys()):
                value += " as-path [ " + route['as_path'] + " ]"
            
            return value
        else:
            return None
    
    def withdraw_route(self,route):
        
        if (isinstance(route,tuple) or isinstance(route,list)):
            value = "withdraw route " + route[0] + " next-hop " + route[1]
            
            if ('as-path' in route):
                value += " as-path [ " + route[3] + " ]"
                
            return value
        elif (isinstance(route,dict) or isinstance(route,sqlite3.Row)):
            value = "withdraw route " + route['prefix'] + " next-hop " + route['next_hop'] 
        
            if ('as-path' in route):
                value += " as-path [ " + route['as_path'] + " ]"
            
            return value
        else:
            return None

''' main '''    
if __name__ == '__main__':
    
    mypeer = peer('172.0.0.22')
    
    route = '''{ "exabgp": "2.0", "time": 1387421714, "neighbor": { "ip": "172.0.0.21", "update": { "attribute": { "origin": "igp", "as-path": [ [ 300 ], [ ] ], "med": 0, "atomic-aggregate": false }, "announce": { "ipv4 unicast": { "140.0.0.0/16": { "next-hop": "172.0.0.22" }, "150.0.0.0/16": { "next-hop": "172.0.0.22" } } } } } }'''
    
    mypeer.udpate(route)
    
    print mypeer.filter_route('input', 'as_path', '300')
    

