#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)
#  Sean Donovan

''' BGP decision process '''
def decision_process(rib,prefix):
    # TODO: add the actual best-path selection algorithm.
    routes = rib.get_all(prefix)

# Priority of rules to make decision:
# ---- 0. [Vendor Specific - Cisco has a "Weight"]
# ---- 1. Highest Local Preference
# 2. Lowest AS Path Length
# ---- 3. Lowest Origin type - Internal preferred over external
# 4. Lowest  MED
# ---- 5. eBGP learned over iBGP learned - so if the above's equal, and you're at a border router, send it out to the next AS rather than transiting 
# ---- 6. Lowest IGP cost to border routes
# 7. Lowest Router ID (tie breaker!)
#
# I believe that steps 0, 1, 3, 5, and 6 are out
    best_routes = None
    for route in routes:
        #find ones with smallest AS Path Length
        if best_routes is None:
            #prime the pump
            min_route_len = aspath_len('as-path' in route)
            best_routes.append(route)
        elif min_route_len == aspath_len('as-path' in route):
            best_routes.append(route)
        elif min_route_len > aspath_len('as-path' in route):
            clear_list(best_routes)
            min_route_len = aspath_len('as-path' in route)
            best_routes.append(route)

    #If there's only 1, it's the best route    
    if len(best_routes) == 1:
        return best_routes.pop()

    
    # Compare the MED only among routes that have been advertised by the same AS. 
    # Put it differently, you should skip this step if two routes are advertised by two different ASes. 

    

        #next
            #Lowest Router ID - what is this? Random?


    return None
        
    
def aspath_length(as_path)
    ases = as_path.split()
    return len(ases)

def clear_list(list)
    del list[:]
