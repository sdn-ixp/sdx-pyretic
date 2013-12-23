#############################################
# Set Operations on IP Prefixes             #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import os,sys
from multiprocessing import Process, Queue
import cProfile
multiprocess=True

def get_pset(plist):
    pset=[]
    for elem in plist:
        pset.append(frozenset(elem))
    return set(pset)


def get_pdict(part_2_prefix):
    temp=set()
    for part in part_2_prefix:
        for plist in part_2_prefix[part]:            
            if len(plist)>1:
                temp=temp.union(set(plist))
                #print "plist: ",plist
    return dict.fromkeys(list(temp), '')

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


def decompose_set(tdict,part_2_prefix_updated,tempdict_bk):
    #print "tdict: %s" % (tdict)
    pmap=[]
    for key in tdict:
        for lst in tdict[key]:
            pmap.append(set(lst))
    #print pmap
    min_set=set.intersection(*pmap)
    #print "min_set: ",min_set
    if len(min_set)>0:
        for key in tdict:
            tlist=[min_set]
            for lst in tdict[key]:           
                temp=(set(lst).difference(min_set))   
                if len(temp)>0:
                    tlist.append(temp)
            tdict[key]=tlist
            part_2_prefix_updated[key]+=(tlist) 
            for elem in tempdict_bk[key]:
                part_2_prefix_updated[key].remove(elem)   
    return tdict

def decompose_simpler(part_2_prefix):
    part_2_prefix_updated=part_2_prefix
    pdict=get_pdict(part_2_prefix_updated)
    for key in pdict:
        print key
        tempdict={}
        tempdict_bk={}
        for part in part_2_prefix_updated:
            #tempdict[part]=[]
            tlist=[]
            for temp in part_2_prefix_updated[part]:
                if key in temp:
                    tlist.append(temp)
            """
            for elem in tlist:
                part_2_prefix_updated[part].remove(elem)
            """
            if len(tlist)>0:
                tempdict[part]=tlist
                tempdict_bk[part]=tlist
        print len(tempdict_bk),tempdict
        if (len(tempdict)==1 and len(tempdict.values()[0])==1) ==False:        
            decompose_set(tempdict,part_2_prefix_updated,tempdict_bk) 
        else:
            print "Avoided"       
        print part_2_prefix
    lcs=[]
    for part in part_2_prefix_updated:
        for temp in part_2_prefix_updated[part]:
            tset=set(temp)
            if tset not in lcs:
                lcs.append(tset)
    print "LCS: ",lcs
    return part_2_prefix_updated,lcs

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


def divide_part2prefixes(plist,part_2_prefix):
    tmp={}
    for elem in plist:
        tmp[elem]=part_2_prefix[elem]
    return tmp


def decmopose_parallel(part_2_prefix,q=None,index=0):
    part_2_prefix_updated={}
    partList=part_2_prefix.keys()
    P=len(partList)
    tmp1={}
    tmp2={}
    #print P
    if P==2:
        ndict={}
        keys=part_2_prefix.keys()
        nkey=str(keys[0])+str(keys[1])
        print nkey
        x,lcs=decompose_simpler(part_2_prefix)
        #print part_2_prefix_updated
        ndict[nkey]=lcs        
        return ndict  
    elif P==1:
        ndict={}
        print part_2_prefix.keys()[0]
        x,lcs=decompose_simpler(part_2_prefix)
        ndict[part_2_prefix.keys()[0]]=lcs
        return ndict
    else:
        tmp1=divide_part2prefixes(partList[::2],part_2_prefix)
        tmp2=divide_part2prefixes(partList[1::2],part_2_prefix)
    
        #print tmp1,tmp2
        d1=decmopose_parallel(tmp1)
        d2=decmopose_parallel(tmp2)    
        lcs=decmopose_parallel(dict(d1.items()+d2.items()))        
        return lcs


def lcs_parallel(part_2_prefix):
    lcs=decmopose_parallel(part_2_prefix)     
    print "Final LCS: ",lcs
    part_2_prefix_updated={}
    # This step can be easily parallelized
    for part in part_2_prefix:
        d1={}
        d1[part]=part_2_prefix[part]
        tmp,x=decompose_simpler(dict(d1.items()+lcs.items()))
        part_2_prefix_updated[part]=tmp[part]
    print "Final: ",part_2_prefix_updated
    return part_2_prefix,lcs.values()[0]
    
   
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


def decompose_simpler_multi(part_2_prefix,q=None):
    part_2_prefix_updated=part_2_prefix
    pdict=get_pdict(part_2_prefix_updated)
    for key in pdict:
        #print key
        tempdict={}
        tempdict_bk={}
        for part in part_2_prefix_updated:
            #tempdict[part]=[]
            tlist=[]
            for temp in part_2_prefix_updated[part]:
                if key in temp:
                    tlist.append(temp)
            if len(tlist)>0:
                tempdict[part]=tlist
                tempdict_bk[part]=tlist
        #print len(tempdict_bk),tempdict
        if (len(tempdict)==1 and len(tempdict.values()[0])==1) ==False:        
            decompose_set(tempdict,part_2_prefix_updated,tempdict_bk) 
    lcs=[]
    for part in part_2_prefix_updated:
        for temp in part_2_prefix_updated[part]:
            tset=set(temp)
            if tset not in lcs:
                lcs.append(tset)
    #print "LCS: ",lcs    
    if q!=None:
        q.put((part_2_prefix_updated,lcs))
    else:
        return part_2_prefix_updated,lcs
    
def decompose_multi(part_2_prefix,q=None,index=0):
    partList=part_2_prefix.keys()
    P=len(partList)
    if P==2:
        ndict={}
        keys=part_2_prefix.keys()
        nkey=str(keys[0])+str(keys[1])
        #print nkey
        x,lcs=decompose_simpler_multi(part_2_prefix)
        #print part_2_prefix_updated
        ndict[nkey]=lcs
        if q!=None: 
            q.put(ndict)
        else:      
            return ndict  
    elif P==1:
        ndict={}
        #print part_2_prefix.keys()[0]
        x,lcs=decompose_simpler_multi(part_2_prefix)
        ndict[part_2_prefix.keys()[0]]=lcs
        if q!=None:
            q.put(ndict)
        else:
            return ndict
    else:
        tmp=[divide_part2prefixes(partList[::2],part_2_prefix),
             divide_part2prefixes(partList[1::2],part_2_prefix)]
        process=[]
        queue=[]
        qout=[]
        for i in range(2):
            queue.append(Queue()) 
            process.append(Process(target=decompose_multi, args=(tmp[i],queue[i])))
            process[i].start()
            print "Started: ",process[i].pid
        for i in range(2):
            process[i].join()
            print "Joined: ",process[i].pid,i
            qout.append(queue[i].get())  
        lcs=decompose_multi(dict(qout[0].items()+qout[1].items()))        
        return lcs

    
def lcs_multiprocess(part_2_prefix):
    lcs=decompose_multi(part_2_prefix)     
    part_2_prefix_updated={}
    queue=[]
    process=[]
    i=0
    for part in part_2_prefix:
        d1={}
        d1[part]=part_2_prefix[part]
        tmp=dict(d1.items()+lcs.items())
        queue.append(Queue())
        process.append(Process(target=decompose_simpler_multi, args=(tmp,queue[i])))
        process[i].start()
        print "Started1: ",process[i].pid
        i+=1
    i=0
    for part in part_2_prefix:
        process[i].join()
        print "Joined1: ",process[i].pid,i
        tmp,x=queue[i].get()
        part_2_prefix_updated[part]=tmp[part]
        i+=1
    print "Final LCS: ",lcs
    print "Final P2P: ",part_2_prefix_updated
    return part_2_prefix,lcs.values()[0]




def test():
    part_2_prefix= {1: [[15, 2, 14, 13, 7, 4], [2, 12, 10, 14, 13, 11], [13, 7, 6, 1, 3, 12]], 
                    2: [[8, 13, 1, 11, 16, 10], [18, 16, 13, 17, 15, 7], [9, 14, 13, 2, 18, 17]], 
                    3: [[17, 8, 5, 13, 1, 12], [6, 14, 1, 7, 13, 17], [14, 4, 9, 10, 16, 5]], 
                    4: [[11, 4, 18, 17, 5, 2], [9, 16, 8, 13, 7, 15], [3, 15, 6, 4, 5, 10]]}
    print part_2_prefix
    #lcs=decompose_simpler(part_2_prefix)
    part_2_prefix,lcs=lcs_multiprocess(part_2_prefix)

def main():
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
    #part_2_prefix_updated,lcs=lcs_parallel(tmp)
    prefix_decompose(tmp)
    #part_2_prefix_recompute =lcs_recompute(part_2_prefix_old, part_2_prefix_new,part_2_prefix_updated,lcs)
    #print "final Recompute: ",part_2_prefix_recompute

        

if __name__ == '__main__':
    #main()  
    test()

    