#############################################
# SDX-Quagga Integration                    #
# author: Arpit Gupta (glex.qsd@gmail.com)  #
#############################################
import sys,os
import json


class MyDecoder(json.JSONDecoder):
    def __init__(self):
        json.JSONDecoder.__init__(self,object_hook=self.dict_to_object)

    def dict_to_object(self,d):
        if '__class__' in d:
            class_name=d.pop('__class__')
            module_name=d.pop('__module__')
            module=__import__(module_name)
            #module=importlib.import_module(module_name)
            print 'Module:',module
            class_ = getattr(module,class_name)
            print 'Class:',class_
            # decode the other params
            args=dict((key.encode('ascii'),value) for key,value in d.items())
            inst=class_(**args)
        else:
            inst=d

        return inst

def convert_to_builtin_type(obj):
    print 'default(', repr(obj), ')'
    # Convert objects to a dictionary of their representation
    d = { '__class__':obj.__class__.__name__,
        '__module__':obj.__module__,
        }
    d.update(obj.__dict__)
    return d


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj,'reprJSON'):
            return obj.reprJSON()
        else:
            return json.JSONEncoder.default(self, obj)

