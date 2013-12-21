#############################################
# Set Operations on IP Prefixes             #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import os,sys
from multiprocessing import Process, Queue


def get_pset(plist):
    pset=[]
    for elem in plist:
        pset.append(frozenset(elem))
    return set(pset)


def get_pdict(part_2_prefix):
    temp=set()
    for part in part_2_prefix:
        for plist in part_2_prefix[part]:
            temp=temp.union(set(plist))
    return dict.fromkeys(list(temp), '')


def decompose_set(tdict):
    #print "tdict: %s" % (tdict)
    pmap=[]
    for key in tdict:
        for lst in tdict[key]:
            pmap.append(set(lst))
    min_set=set.intersection(*pmap)
    if len(min_set)>0:
        for key in tdict:
            tlist=[list(min_set)]
            for lst in tdict[key]:           
                temp=list(set(lst).difference(min_set))   
                if len(temp)>0:
                    tlist.append(temp)
            tdict[key]=tlist    
    return tdict


def prefix_decompose(part_2_prefix):
    part_2_prefix_updated=part_2_prefix
    pdict=get_pdict(part_2_prefix_updated)
    for key in pdict:
        #print key
        tempdict={}
        for part in part_2_prefix_updated:
            #tempdict[part]=[]
            tlist=[]
            for temp in part_2_prefix_updated[part]:
                if key in temp:
                    tlist.append(temp)
            for elem in tlist:
                part_2_prefix_updated[part].remove(elem)
            if len(tlist)>0:
                tempdict[part]=tlist
        decomposed_tempdict=decompose_set(tempdict)
        for part in decomposed_tempdict:
            for elem in decomposed_tempdict[part]:
                part_2_prefix_updated[part].append(elem)
    return part_2_prefix_updated


def decmopose_parallel(part_2_prefix,q=None,index=0):
    part_2_prefix_updated={}
    partList=part_2_prefix.keys()
    P=len(partList)
    tmp1={}
    tmp2={}
    if P==2:
        #print "P==2 called"
        prefix_decompose(part_2_prefix)
        #print part_2_prefix_updated
        ndict={}
        keys=part_2_prefix.keys()
        nkey=keys[0]+keys[1]
        ndict[nkey]=part_2_prefix[keys[0]]
        for plist in part_2_prefix[keys[1]]:
            # TODO: this step can be improved and can be a possible performance bottleneck
            if set(plist) not in get_pset(ndict[nkey]):
                ndict[nkey].append(plist)
        #print ndict
        return ndict        
    for i in range(1,P+1):
        if i<=float(P)/2:
            tmp1[partList[i-1]]=part_2_prefix[partList[i-1]]
            tmp2[partList[P-i]]=part_2_prefix[partList[P-i]]
            i+=1
        else:
            d1=decmopose_parallel(tmp1)
            d2=decmopose_parallel(tmp2)    
            part_2_prefix_updated=decmopose_parallel(dict(d1.items()+d2.items()))
            break        
    return part_2_prefix_updated
    

def lcs_parallel(part_2_prefix):
    # This step can be easily parallelized
    for participant in part_2_prefix:
        tmp={}
        tmp[participant]=part_2_prefix[participant]
        prefix_decompose(tmp)
        part_2_prefix[participant]=tmp[participant]
    print "After Participant Decompose: ",part_2_prefix
    lcs=decmopose_parallel(part_2_prefix)     
    print "LCS: ",lcs
    part_2_prefix_updated={}
    # This step can be easily parallelized
    for part in part_2_prefix:
        d1={}
        d1[part]=part_2_prefix[part]
        p2p_updated=prefix_decompose(dict(d1.items()+lcs.items()))
        part_2_prefix_updated[part]=p2p_updated[part]
    return part_2_prefix,lcs.values()[0]

def getLCS(part_2_prefix):
    lcs_out=[]
    for participant in part_2_prefix:
        plist=part_2_prefix[participant]
        for elem in plist:
            lcs_out.append(frozenset(elem))
    lcs_out=set(lcs_out)
    lcs=[]
    for elem in lcs_out:
        lcs.append(list(elem))    
    print 'lcs_out: ',lcs  
    return lcs
    
   
def lcs_recompute(p2p_old, p2p_new,part_2_prefix_updated,lcs_old=[]):
    p2p_updated={}
    if len(lcs_old)==0:
        lcs_old=getLCS(part_2_prefix_updated)
    p2p_updated['old']=lcs_old
    affected_participants=[]
    for participant in p2p_new:
        pset_new=get_pset(p2p_new[participant])
        pset_old=get_pset(p2p_old[participant])
        pset_new=(pset_new.union(pset_old).difference(pset_old))
        if len(pset_new)!=0:
            print "Re-computation required for: ",participant
            affected_participants.append(participant)
            plist=[]
            for elem in pset_new:
                plist.append(list(elem))
            p2p_updated[participant]=plist        
        print participant,pset_new
    print p2p_updated
    prefix_decompose(p2p_updated)
    for participant in part_2_prefix_updated:
        tmp={}
        if participant in affected_participants:
            tmp['new']=p2p_updated['old']
            tmp[participant]=part_2_prefix_updated[participant]
            prefix_decompose(tmp)
            p2p_updated[participant]=tmp[participant]
        else:
            p2p_updated[participant]=part_2_prefix_updated[participant]
    p2p_updated.pop('old')
    return p2p_updated
        

if __name__ == '__main__':
    
    # prefix list
    pdict={'p1':'','p2':'','p3':''}
    # prefix mapping
    #part_2_prefix={1:[['c3']],2:[['c3','c2'],['c1','c3']],3:[['c1','c2','c3']]}
    
    part_2_prefix= {'A': [['p1', 'p2', 'p3'], ['p3', 'p2'], ['p1']], 
      'C': [['p2', 'p3']], 'B': [['p2', 'p1'], ['p3']], 'D': [['p2', 'p3', 'p1']]}
    part_2_prefix_old= {'A': [['p1', 'p2', 'p3', 'p4', 'p6'], ['p3', 'p4', 'p5', 'p6'], ['p6', 'p4', 'p5'], ['p2', 'p3', 'p1']], 
                        'C': [['p3', 'p6', 'p4', 'p5']],
                        'B': [['p1', 'p2', 'p3', 'p4', 'p6'], ['p1', 'p2', 'p3', 'p4', 'p6'], ['p1'], ['p4'], ['p2', 'p3', 'p6']], 
                        'D': [['p2', 'p3', 'p1', 'p6', 'p4', 'p5']]}
    tmp= {'A': [['p1', 'p2', 'p3', 'p4', 'p6'], ['p3', 'p4', 'p5', 'p6'], ['p6', 'p4', 'p5'], ['p2', 'p3', 'p1']], 
                        'C': [['p3', 'p6', 'p4', 'p5']],
                        'B': [['p1', 'p2', 'p3', 'p4', 'p6'], ['p1', 'p2', 'p3', 'p4', 'p6'], ['p1'], ['p4'], ['p2', 'p3', 'p6']], 
                        'D': [['p2', 'p3', 'p1', 'p6', 'p4', 'p5']]}
    part_2_prefix_new= {'A': [['p1', 'p2', 'p3', 'p4', 'p6'], ['p3', 'p4', 'p5', 'p6'], ['p6', 'p5'], ['p4'], ['p2', 'p3', 'p1']], 
                        'C': [['p3', 'p6', 'p5']], 
                        'B': [['p1', 'p2', 'p3', 'p4', 'p6'], ['p1', 'p2', 'p3', 'p4', 'p6'], ['p1'], ['p4'], ['p2', 'p3', 'p6']], 
                        'D': [['p2', 'p3', 'p1', 'p6', 'p4', 'p5']]}


    print "old: ",part_2_prefix_old
    print "new: ",part_2_prefix_new
    part_2_prefix_updated,lcs=lcs_parallel(tmp)
    part_2_prefix_recompute =lcs_recompute(part_2_prefix_old, part_2_prefix_new,part_2_prefix_updated,lcs)
    print "final Recompute: ",part_2_prefix_recompute


    