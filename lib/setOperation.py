#############################################
# Set Operations on IP Prefixes             #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import os,sys
from multiprocessing import Process, Queue

def decompose_set(tdict):
    #print "tdict: %s" % (tdict)
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

def get_set(plists):
    pset=[]
    for plist in plists:
        pset.append(set(plist))
    return pset

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

def get_prefixset(part_2_prefix):
    psetlist=[]
    for participant in part_2_prefix:
        for plist in part_2_prefix[participant]:
            if set(plist) not in psetlist:
                psetlist.append(set(plist))
    return psetlist

def lcs2(s1,s2):
    if len(s1)!=0:
        intersect=s1.intersection(s2)
        temp=[s1.difference(intersect),s2.difference(intersect),intersect]
        lcs2_out=[]
        for elem in temp:
            if len(elem)!=0:
                lcs2_out.append(elem)
    else:
        return [s2]            
    return lcs2_out


def decmopose_parallel(part_2_prefix,q=None,index=0):
    part_2_prefix_updated={}
    partList=part_2_prefix.keys()
    P=len(partList)
    tmp1={}
    tmp2={}
    if P==2:
        print "P==2 called"
        part_2_prefix_updated=prefix_decompose(part_2_prefix)
        print part_2_prefix_updated
        ndict={}
        keys=part_2_prefix.keys()
        nkey=keys[0]+keys[1]
        ndict[nkey]=part_2_prefix[keys[0]]
        for plist in part_2_prefix[keys[1]]:
            # this step can be improved and can be a possible performance bottleneck
            if set(plist) not in get_set(ndict[nkey]):
                ndict[nkey].append(plist)
        print ndict
        if q!=None:
            q.put({index:ndict})
        else:
            return ndict
        
    for i in range(1,P+1):
        print i
        if i<=float(P)/2:
            print partList[i],partList[P-i]
            tmp1[partList[i-1]]=part_2_prefix[partList[i-1]]
            tmp2[partList[P-i]]=part_2_prefix[partList[P-i]]
            i+=1
        else:
            print 'tmp1:',tmp1
            print 'tmp2:',tmp2
            #processList=[]
            #q=Queue()
            #p1=(Process(target=decmopose_parallel, args=(tmp1,q,1)))
            #p1.start
            #d1=q.get()
            #processList.append(Process(target=decmopose_parallel, args=(tmp2,q,2)))
            d1=decmopose_parallel(tmp1)
            d2=decmopose_parallel(tmp2)
            #p1.join()
            
            part_2_prefix_updated=decmopose_parallel(dict(d1.items()+d2.items()))
            break
        
    return part_2_prefix_updated
    

def lcs_parallel(part_2_prefix):
    lcs=decmopose_parallel(part_2_prefix) 
    print "LCS: ",lcs
    part_2_prefix_updated={}
    for part in part_2_prefix:
        d1={}
        d1[part]=part_2_prefix[part]
        p2p_updated=prefix_decompose(dict(d1.items()+lcs.items()))
        part_2_prefix_updated[part]=p2p_updated[part]
    return part_2_prefix
 
if __name__ == '__main__':
    
    # prefix list
    pdict={'p1':'','p2':'','p3':''}
    # prefix mapping
    #part_2_prefix={1:[['c3']],2:[['c3','c2'],['c1','c3']],3:[['c1','c2','c3']]}
    
    part_2_prefix= {'A': [['p1', 'p2', 'p3'], ['p3', 'p2'], ['p1']], 
      'C': [['p2', 'p3']], 'B': [['p2', 'p1'], ['p3']], 'D': [['p2', 'p3', 'p1']]}
    
    print "initial: ",part_2_prefix
    """
    #plist=[['c1'],['c1','c2'],['c1','c2','c3']]
    part_2_prefix_updated=prefix_decompose(part_2_prefix)
    
    print "final: ",part_2_prefix_updated
    """
    part_2_prefix_updated=lcs_parallel(part_2_prefix)
    
            
    print "final2 : ",part_2_prefix_updated
    
    #newlist=find_intersection(plist)
    #print newlist