#############################################
# SDX-Quagga Integration                    #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import os,sys

def find_intersection(plist):
    print "Starting set operations"
    pmap=map(set,plist)
    min_set=set.intersection(*pmap)
    print 'Minimum_Set: ',min_set
    newlist={}
    i=0
    for set_entry in pmap:
        newlist[i]=[]
        newlist[i].append(list(min_set))
        diff= list(set_entry.difference(min_set))
        if len(diff)>0:
            newlist[i].append(diff)
        i+=1
    return newlist

def decompose_set(tdict):
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
    
if __name__ == '__main__':
    
    pdict={'c1':'','c2':'','c3':''}
    part_2_prefix={1:[['c3']],2:[['c3','c2'],['c1','c3']],3:[['c1','c2','c3']]}
    print "initial: ",part_2_prefix
    #plist=[['c1'],['c1','c2'],['c1','c2','c3']]

    for key in pdict:
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
    print "final: ",part_2_prefix
        
            
        
    
    #newlist=find_intersection(plist)
    #print newlist