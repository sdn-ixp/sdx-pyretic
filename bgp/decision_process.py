#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)
#  Sean Donovan

''' BGP decision process '''
def decision_process(rib,prefix):
    # TODO: add the actual best-path selection algorithm.
    
    routes = rib.get_all(prefix)
        
    for route in routes:
        # Trivial implementation returns the first route it encounters.
        return route
    
    return None
        
    
    