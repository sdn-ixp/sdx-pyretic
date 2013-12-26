#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import sqlite3

class rib():
    
    def __init__(self, name):
        
        # Create a database in RAM
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        self.name = name
        
        # Get a cursor object
        cursor = self.db.cursor()
        cursor.execute('''
                        create table ''' + self.name + ''' (prefix text, next_hop text,
                               origin text, as_path text, med integer, atomic_aggregate boolean)
        ''')
       
        self.db.commit()
    
    def __del__(self):
            
        self.db.close()
        
    def __setitem__(self,key,item): 
        
        self.add(key,item)
        
    def __getitem__(self,key): 
            
        return self.get(key)
        
    def add(self,key,item):
        
        cursor = self.db.cursor()
        
        if (isinstance(item,tuple) or isinstance(item,list)):
            cursor.execute('''insert into ''' + self.name + ''' (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', 
                        (key,item[0],item[1],item[2],item[3],item[4]))
        elif (isinstance(item,dict) or isinstance(item,sqlite3.Row)):
            cursor.execute('''insert into ''' + self.name + ''' (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', 
                        (key,item['next_hop'],item['origin'],item['as_path'],item['med'],
                         item['atomic_aggregate']))
            
        #TODO: Add support for selective update
            
    def add_many(self,items):
        
        cursor = self.db.cursor()
        
        if (isinstance(items,list)):
            cursor.execute('''insert into ''' + self.name + ''' (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', items)
            
    def get(self,key): 
            
        cursor = self.db.cursor()
        cursor.execute('''select * from ''' + self.name + ''' where prefix = ?''', (key,))
        
        return cursor.fetchone()
    
    def get_all(self,key=None): 
            
        cursor = self.db.cursor()
        
        if (key is not None):
            cursor.execute('''select * from ''' + self.name + ''' where prefix = ?''', (key,))
        else:
            cursor.execute('''select * from ''' + self.name)
        
        return cursor.fetchall()
    
    def filter(self,item,value): 
            
        cursor = self.db.cursor()
        
        script = "select * from " + self.name + " where " + item + " like '%" + value + "%'"
        
        cursor.execute(script)
        
        return cursor.fetchall()
    
    def update(self,key,item,value):
        
        cursor = self.db.cursor()
        
        script = "update " + self.name + " set " + item + " = '" + value + "' where prefix = '" + key + "'"
        
        cursor.execute(script)
            
    def update_many(self,key,item):
        
        cursor = self.db.cursor()
        
        if (isinstance(item,tuple) or isinstance(item,list)):
            cursor.execute('''update ''' + self.name + ''' set next_hop = ?, origin = ?, as_path = ?,
                            med = ?, atomic_aggregate = ? where prefix = ?''',
                            (item[0],item[1],item[2],item[3],item[4],key))
        elif (isinstance(item,dict) or isinstance(item,sqlite3.Row)):
            cursor.execute('''update ''' + self.name + ''' set next_hop = ?, origin = ?, as_path = ?,
                            med = ?, atomic_aggregate = ? where prefix = ?''', 
                            (item['next_hop'],item['origin'],item['as_path'],item['med'],
                             item['atomic_aggregate'],key))
        
    def delete(self,key):
        
        cursor = self.db.cursor()
        
        cursor.execute('''delete from ''' + self.name + ''' where prefix = ?''', (key,))
        
    def delete_all(self):
        
        cursor = self.db.cursor()
        
        cursor.execute('''delete from ''' + self.name)
    
    def commit(self):
        
        self.db.commit()
        
    def rollback(self):
        
        self.db.rollback()

''' main '''     
if __name__ == '__main__':
    
    myrib = rib()
    
    myrib['100.0.0.1/16'] = ('172.0.0.2', 'igp', '100, 200, 300', '0', 'false')
    #myrib['100.0.0.1/16'] = ['172.0.0.2', 'igp', '100, 200, 300', '0', 'false']
    #myrib['100.0.0.1/16'] = {'next_hop':'172.0.0.2', 'origin':'igp', 'as_path':'100, 200, 300',
    #                          'med':'0', 'atomic_aggregate':'false'}
    myrib.commit()
    
    myrib.update('100.0.0.1/16', 'next_hop', '190.0.0.2')
    myrib.commit()
    
    val = myrib.filter('as_path', '300')
    
    print val[0]['next_hop']
