#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

''' Announce route '''
def bgp_announce_route(sdx,route):
    if isinstance(route,dict):
        route_json = '''{ "neighbor": { 
                         "ip": "'''+route["ip"]+'''",
                         "update": { 
                             "attribute": { 
                                 "origin": "'''+route["origin"]+'''", 
                                 "as-path": ['''+route["as-path"]+'''], 
                                 "atomic-aggregate": '''+route["atomic-aggregate"]+''', 
                                 "med": '''+route["med"]+''' 
                             }, 
                             "announce": { 
                                 "ipv4 unicast": { 
                                     "'''+route["prefix"]+'''": { 
                                         "next-hop": "'''+route["next-hop"]+'''" 
                                     } 
                                 } 
                             } 
                         } 
                     } 
                }'''
        sdx.server.receiver_queue.put(route_json)

''' Get best routes for a participant '''
def bgp_get_best_routes(sdx,participant_name):    
    
    # TODO: should avoid this translation and use prefixes directly for performance gain.
    
    best_routes = {}
    
    peers = sdx.participants[participant_name].peers
    for peer_name in peers:
        
        ports = sdx.sdx_ports[peer_name]
        for port in ports:

            routes = sdx.participants[participant_name].rs_client.filter_route('local','next_hop',str(port.ip))
            
            if routes:
                if (peer_name not in best_routes):
                    best_routes[peer_name] = []
            
                for route in routes:
                    best_routes[peer_name].append(route['prefix'])
    
    return best_routes

''' Get announced routes for a participant '''
def bgp_get_announced_routes(sdx,participant_name):    
    
    # TODO: should avoid this translation and use prefixes directly for performance gain.
    
    announced_routes = []
    
    routes = sdx.participants[participant_name].rs_client.get_all_routes('input')
    
    for route in routes:
        announced_routes.append(route['prefix'])
        
    return announced_routes
        
''' Update route with new next-hop after VNH processing '''
def bgp_trigger_update(event_queue,ready_queue):
    
    event_queue.put("bgp")
    
    ''' Wait for the policies to get updated ''' 
    
    #TODO: optimize the above logic for ready_queue - MS
    while (ready_queue.get() != 'bgp'):
        pass


''' main '''    
if __name__ == '__main__':
    route = {'prefix': '100.0.0.0/24',
             'origin': 'igp',
             'med': '0',
             'as_path': "100",
             'next_hop': "172.0.3.1"}
    
    bgp_announce_route(None,route)
    