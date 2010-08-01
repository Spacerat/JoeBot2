
import inspect

com_hooks = {}

class ComHook:

    def __init__(self,hook,callback,name='',hidden=False,security=1,data=None):
        frm = inspect.stack()[1]
        mod = inspect.getmodule(frm[0])
        self.name = name
        self.callback = callback
        self.hidden = hidden
        self.security=security
        self.hook = hook
        self.module = mod.__name__
        self.data=data
        com_hooks[hook]=self

    def run(self, interface, args):
        #threading.Thread(target=com_hooks[self.hook],name=self.hook,args=(interface,command,args)).start()
        self.callback(interface,self,args)

def message_hook(text,interface):
    if text!="":
        command = text.partition(" ")[0][len(interface.prefix):len(text)].lower()
        body = text.partition(" ")[2]
        
        #Command hooks
        if command in com_hooks:
            if text.startswith(interface.prefix):
                c = com_hooks[command]
                interface.name = c.name
                #if security.GetSecurityForHandle(Interface,Interface.UserAddress)<c.Security:
                #    Interface.Reply("Use of this command requires an access level of %u"%c.Security)
                #elif c.Admin == True and security.GetAdminForHandle(Interface,Interface.UserAddress)==False:
                #    Interface.Reply("You must have admin access in this conversation to use this command.")
                #else:
                c.run(interface, body)

def unload_hook(module):
    for x in com_hooks.keys():
        if com_hooks[x].module == "modules.%s"%module:
            del com_hooks[x]


def init():
    add_hook('message',message_hook)
    add_hook('unloaded',unload_hook)
