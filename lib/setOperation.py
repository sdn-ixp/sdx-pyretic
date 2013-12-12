#############################################
# Set Operations on IP Prefixes             #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import os,sys

def decompose_set(tdict):
    print "tdict: %s" % (tdict)
    pmap=[]
    for key in tdict:
        for lst in tdict[key]:
            pmap.append(set(lst))
    min_set=set.intersection(*pmap)
    if len(list(min_set))>0:
        for key in tdict:
            tlist=[list(min_set)]
            for lst in tdict[key]:           
                temp=list(set(lst).difference(min_set))   
                if len(temp)>0:
                    tlist.append(temp)
            tdict[key]=tlist    
    return tdict

def get_pdict(part_2_prefix):
    temp=set()
    for part in part_2_prefix:
        for plist in part_2_prefix[part]:
            temp=temp.union(set(plist))
    return dict.fromkeys(list(temp), '')

def prefix_decompose(part_2_prefix):
    pdict=get_pdict(part_2_prefix)
    for key in pdict:
        #print key
        tempdict={}
        for part in part_2_prefix:
            #tempdict[part]=[]
            tlist=[]
            for temp in part_2_prefix[part]:
                if key in temp:
                    tlist.append(temp)
            for elem in tlist:
                part_2_prefix[part].remove(elem)
            if len(tlist)>0:
                tempdict[part]=tlist
        decomposed_tempdict=decompose_set(tempdict)
        for part in decomposed_tempdict:
            for elem in decomposed_tempdict[part]:
                part_2_prefix[part].append(elem)
    return part_2_prefix
 
if __name__ == '__main__':
    
    # prefix list
    pdict={'p1':'','p2':'','p3':''}
    # prefix mapping
    #part_2_prefix={1:[['c3']],2:[['c3','c2'],['c1','c3']],3:[['c1','c2','c3']]}
    
    part_2_prefix= {'A': [['p1', 'p2', 'p3'], ['p2', 'p3'], ['p1']], 
      'C': [['p2', 'p3']], 'B': [['p2', 'p1'], ['p3']], 'D': [['p2', 'p3', 'p1']]}
    print "initial: ",part_2_prefix
    #plist=[['c1'],['c1','c2'],['c1','c2','c3']]
    part_2_prefix_updated=prefix_decompose(pdict,part_2_prefix)
    
    print "final: ",part_2_prefix_updated
        
            
        
    
    #newlist=find_intersection(plist)
    #print newlist