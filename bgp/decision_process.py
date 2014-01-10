#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)
#  Sean Donovan
import socket,struct

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

    # If there's only 1, it's the best route    
    if len(best_routes) == 1:
        return best_routes.pop()

    
    # Compare the MED only among routes that have been advertised by the same AS. 
    # Put it differently, you should skip this step if two routes are advertised by two different ASes. 
    
    # get all the ASes advertising the route
    as_list = None
    post_med_best_routes = None
    for route in best_routes:
        as_list.append(get_advertised_as('as-path' in route))

    # sort the advertiser's list and 
    # look at ones who's count != 1
    as_list.sort()
    i = 0
    while i < len(as_list):
        if as_list.count(as_list[i]) != 1:
            # get all that match the particular AS
            from_as_list = x for x in best_routes if get_advertised_as('as-path' in x) = as_list[i]

            # MED comparison here
            j = 0
            lowest_med = 'med' in from_as_list[j]
            j++
            while j < len(from_as_list):
                if lowest_med > 'med' in from_as_list[j]:
                    lowest_med = 'med' in from_as_list[j]
                j++
            
            # add to post-MED list - this could be more than one if MEDs match
            post_med_best_routes.append(x for x in from_as_list if
                                        'med' in x == lowest_med)
            i = i + as_list.count(as_list[i])
        else:
            post_med_best_routes.append(x for x in best_routes if get_advertised_as('as-path' in x) == as_list[i])
            i++
    
    # If there's only 1, it's the best route
    if len(post_med_best_routes) == 1:
        return post_med_best_routes.pop()


    #Lowest Router ID - Origin IP of the routers left.
    i = 0
    lowest_ip_as_long = ip_to_long('origin' in post_med_best_routes[i])
    i++
    while i < len(post_med_best_routes):
        if lowest_ip_as_long > ip_to_long('origin' in post_med_best_routes[i]):
            lowest_ip_as_long = ip_to_long('origin' in post_med_best_routes[i])
        i++

    return post_med_best_routes[get_index(post_med_best_routes, 'origin', long_to_ip(lowest_ip_as_long))]

    
def aspath_length(as_path):
    ases = as_path.split()
    return len(ases)

def get_advertised_as(as_path):
    ases = as_path.split()
    return ases[0]

def clear_list(list):
    del list[:]

def ip_to_long(ip):
    return struct.unpack('!L', inet_aton(ip))[0]

def long_to_ip(ip):
    return socket.inet_ntoa(struct.pack('!L', ip))
      

def get_index(seq, attr, value):
    return next(index for (index, d) in enumerate(seq) if d[attr] == value)
