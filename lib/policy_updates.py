#############################################
# Handling Participant's policy Changes     #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################

###
###

from multiprocessing.connection import Listener
import json

class PolicyHandler():
  
    def __init__(self,event_queue,ready_queue,sdx):
        self.event_queue = event_queue
        self.ready_queue = ready_queue
        self.sdx = sdx
        self.listener = Listener(('localhost', 6999), authkey=None)

        
    def start(self):
        while True:
            self.conn = self.listener.accept()
            print 'Policy Handler: Connection accepted from', self.listener.last_accepted
    
            tmp = self.conn.recv()
            data = json.loads(tmp)
            print data, type(data)
            print data.keys()
            print self.sdx.policy_status.keys()
            for pname in data:
                
                self.sdx.policy_status[pname] = int(data[pname])
            print data, self.sdx.policy_status
            self.conn.send('Policy Handler: Hello World')
            self.conn.close()
            self.event_queue.put('Policy Handler: Policy Status changed for ')

if __name__ == '__main__':
	server = PolicyHandler(('localhost', 6999), PolicyEventHandler)
	server.serve_forever()
