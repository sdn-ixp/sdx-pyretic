#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import json
import sqlite3
from rib import rib

class peer():
    
    def __init__(self,ips):
        
        self.ips = ips
        self.rib = {"input": rib("-".join(ips),"input"),
                    "local": rib("-".join(ips),"local")}
         
    def update(self,route):

        origin = None
        as_path = None
        med = None
        atomic_aggregate = None
        route_list = []
        
        if ('neighbor' in route):
            if ('ip' in route['neighbor']):
                # Only add to the RIB if it's for myself.
                if (route['neighbor']['ip'] in self.ips):
                    if ('update' in route['neighbor']):
                        if ('attribute' in route['neighbor']['update']):
                            attribute = route['neighbor']['update']['attribute']
                            origin = attribute['origin'] if 'origin' in attribute else ''
                            as_path = attribute['as-path'] if 'as-path' in attribute else ''
                            med = attribute['med'] if 'med' in attribute else ''
                            atomic_aggregate = attribute['atomic-aggregate'] if 'atomic-aggregate' in attribute else ''
                            
                        if ('announce' in route['neighbor']['update']):
                            announce = route['neighbor']['update']['announce']
                            if ('ipv4 unicast' in announce):
                                for prefix in announce['ipv4 unicast'].keys():
                                    self.rib["input"][prefix] = (announce['ipv4 unicast'][prefix]['next-hop'],
                                                                 origin,
                                                                 ' '.join(map(str,as_path)).replace('[','').replace(']','').replace(',',''),
                                                                 med,
                                                                 atomic_aggregate)
                                    self.rib["input"].commit()
                                    announce_route = self.rib["input"][prefix]
                                    
                                    route_list.append({'announce': announce_route})

                        elif ('withdraw' in route['neighbor']['update']):
                            withdraw = route['neighbor']['update']['withdraw']
                            if ('ipv4 unicast' in withdraw):
                                for prefix in withdraw['ipv4 unicast'].keys():
                                    deleted_route = self.rib["input"][prefix]
                                    self.rib["input"].delete(prefix)
                                    self.rib["input"].commit()
                                    
                                    route_list.append({'withdraw': deleted_route})
                                    # TODO: clarify how the route withdrawal will work i.e., do we have to run the decision process again
                                    
        elif ('notification' in route):
            
            #return
            
            if ('shutdown' == route['notification']):
                self.rib["input"].delete_all()
                self.rib["input"].commit()
                self.rib["local"].delete_all()
                self.rib["local"].commit()
                # TODO: send shutdown notification to participants 
        
        return route_list
    
    def add_route(self,rib_name,prefix,attributes):
        self.rib[rib_name][prefix] = attributes
        self.rib[rib_name].commit()
    
    def add_many_routes(self,rib_name,routes):
        self.rib[rib_name].add_many(routes)
        self.rib[rib_name].commit()
                                    
    def get_route(self,rib_name,prefix):
        
        return self.rib[rib_name][prefix]
    
    def get_routes(self,rib_name,prefix):
        
        return self.rib[rib_name].get_all(prefix)
    
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
    
def announce_route(route,next_hop=None):
       
    if (isinstance(route,tuple) or isinstance(route,list)):
        if next_hop:
            inext_hop = next_hop
        else:
            inext_hop = route[1]
            
        value = "announce route " + route[0] + " next-hop " + inext_hop
            
        if ('as_path' in route):
            value += " as-path [ " + route[3] + " ]"
                
        return value
        
    elif (isinstance(route,dict) or isinstance(route,sqlite3.Row)):
        if next_hop:
            inext_hop = next_hop
        else:
            inext_hop = route['next_hop'] 
            
        value = "announce route " + route['prefix'] + " next-hop " + inext_hop
        
        if ('as_path' in route.keys()):
            value += " as-path [ " + route['as_path'] + " ]"
            
        return value
    else:
        return None
    
def withdraw_route(route,next_hop=None):
        
    if (isinstance(route,tuple) or isinstance(route,list)):
        if next_hop:
            inext_hop = next_hop
        else:
            inext_hop = route[1]
                
        value = "withdraw route " + route[0] + " next-hop " + inext_hop
            
        if ('as-path' in route):
            value += " as-path [ " + route[3] + " ]"
                
        return value
    
    elif (isinstance(route,dict) or isinstance(route,sqlite3.Row)):
        if next_hop:
            inext_hop = next_hop
        else:
            inext_hop = route['next_hop'] 
            
        value = "withdraw route " + route['prefix'] + " next-hop " + inext_hop
        
        if ('as_path' in route.keys()):
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
    

