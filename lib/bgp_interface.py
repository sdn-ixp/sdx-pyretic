#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

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

    while (ready_queue.get() != 'bgp'):
        pass

    