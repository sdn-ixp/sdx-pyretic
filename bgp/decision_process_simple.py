#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)
#  Sean Donovan

''' BGP decision process '''
def decision_process_simple(participants,route):
    
    # TODO: add the actual best-path selection algorithm (using other peers)
    # At the moment always picking ... the peer itself as best route
    
    if ('announce' in route):
        best_route = route['announce']
        
        if (best_route is not None):
            for participant_name in participants:
                participants[participant_name].rs_client.rib["local"].delete(best_route['prefix'])
                participants[participant_name].rs_client.rib["local"][best_route['prefix']] = best_route
                participants[participant_name].rs_client.rib["local"].commit()
        
            return route
        
    # TODO: delete on more specific attributes then just the prefix
    elif('withdraw' in route):
        deleted_route = route['withdraw']
        
        if (deleted_route is not None):
        
            for participant_name in participants:
                participants[participant_name].rs_client.rib["local"].delete(deleted_route['prefix'])
                participants[participant_name].rs_client.rib["local"].commit()
        
        return route
    
    
    