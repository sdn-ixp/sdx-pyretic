#!/usr/bin/env python
#  Author:
#  Muhammad Shahbaz (muhammad.shahbaz@gatech.edu)

import sqlite3

class rib():
    
    def __init__(self):
        
        # Create a database in RAM
        self.db = sqlite3.connect(':memory:')
        self.db.row_factory = sqlite3.Row
        
        # Get a cursor object
        cursor = self.db.cursor()
        cursor.execute('''
                        create table rib (prefix text primary key, next_hop text,
                               origin text, as_path text, med integer, atomic_aggregate boolean)
        ''')
       
        self.db.commit()
    
    def __del__(self):
            
        self.db.close()
        
    def __setitem__(self,key,item): 
        
        cursor = self.db.cursor()
        
        if (isinstance(item,tuple)):
            cursor.execute('''insert into rib (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', 
                        (key,item[0],item[1],item[2],item[3],item[4]))
        elif (isinstance(item,list)):
            cursor.execute('''insert into rib (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', 
                        (key,item[0],item[1],item[2],item[3],item[4]))
        elif (isinstance(item,dict)):
            cursor.execute('''insert into rib (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', 
                        (key,item['next_hop'],item['origin'],item['as_path'],item['med'],
                         item['atomic_aggregate']))
            
            #TODO: Add support for selective update
        
    def __getitem__(self,key): 
            
        cursor = self.db.cursor()
        cursor.execute('''select next_hop, origin, as_path, med, atomic_aggregate 
                        from rib where prefix = ?''', (key,))
        
        return cursor.fetchone()
        
    def add(self,key,item):
        
        cursor = self.db.cursor()
        
        if (isinstance(item,tuple) or isinstance(item,list)):
            cursor.execute('''insert into rib (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', 
                        (key,item[0],item[1],item[2],item[3],item[4]))
        elif (isinstance(item,dict)):
            cursor.execute('''insert into rib (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', 
                        (key,item['next_hop'],item['origin'],item['as_path'],item['med'],
                         item['atomic_aggregate']))
            
    def add_many(self,items):
        
        cursor = self.db.cursor()
        
        if (isinstance(items,list)):
            cursor.execute('''insert into rib (prefix, next_hop, origin, as_path, med,
                        atomic_aggregate) values(?,?,?,?,?,?)''', items)
            
    def get(self,key): 
            
        cursor = self.db.cursor()
        cursor.execute('''select next_hop, origin, as_path, med, atomic_aggregate 
                        from rib where prefix = ?''', (key,))
        
        return cursor.fetchone()
    
    def get_all(self): 
            
        cursor = self.db.cursor()
        cursor.execute('''select * from rib''')
        
        return cursor.fetchall()
    
    def filter(self,item,value): 
            
        cursor = self.db.cursor()
        
        script = "select * from rib where " + item + " like '%" + value + "%'"
        
        cursor.execute(script)
        
        return cursor.fetchall()
    
    def update(self,key,item,value):
        
        cursor = self.db.cursor()
        
        script = "update rib set " + item + " = '" + value + "' where prefix = '" + key + "'"
        
        cursor.execute(script)
            
    def update_many(self,key,item):
        
        cursor = self.db.cursor()
        
        if (isinstance(item,tuple) or isinstance(item,list)):
            cursor.execute('''update rib set next_hop = ?, origin = ?, as_path = ?,
                            med = ?, atomic_aggregate = ? where prefix = ?''',
                            (item[0],item[1],item[2],item[3],item[4],key))
        elif (isinstance(item,dict)):
            cursor.execute('''update rib set next_hop = ?, origin = ?, as_path = ?,
                            med = ?, atomic_aggregate = ? where prefix = ?''', 
                            (item['next_hop'],item['origin'],item['as_path'],item['med'],
                             item['atomic_aggregate'],key))
        
    def delete(self,key):
        
        cursor = self.db.cursor()
        
        cursor.execute('''delete from rib where prefix = ?''', (key,))
        
    def delete_all(self):
        
        cursor = self.db.cursor()
        
        cursor.execute('''delete from rib''')
    
    def commit(self):
        
        self.db.commit()
        
    def rollback(self):
        
        self.db.rollback()

    def decision_process(self,prefix):
        # TODO: Proper Best Path Selection algorithm. This is the trivial version
        routes = self.get(prefix)
        
        if (NULL != routes)
            for route in routes
                #TRIVIAL IMPLEMENTATION - returns the first route it encounters. 
                #Where BPS magic should happen.
                return route;
        else
            return NULL
        
    


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
