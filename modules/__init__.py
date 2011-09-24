
import inspect
import sys
import threading
import traceback

from libs import logging

modules = {}
hooks = {}

#The following hook code has been copied from http://github.com/Katharine/KathBot3/blob/master/modules/__init__.py
#After considering alternatives for a while, I decided that there was simply no better way of implimenting generic hooks.

def add_hook(hook, function):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    module = mod.__name__
    if not hooks.get(hook):
        hooks[hook] = {}
    hooks[hook][module] = function
    #logging.info("Added hook %s for module %s" % (hook, module))

def remove_hook(hook):
    frm = inspect.stack()[1]
    mod = inspect.getmodule(frm[0])
    module = mod.__name__
    if hooks.get(hook):
        del hooks[hook][module]

def call_hook(hook, *args, **kwds):
    if hooks.get(hook):
        RunHook(hook, *args, **kwds)

class RunHook(threading.Thread):
    def __init__(self, hook, *args, **kwds):
        threading.Thread.__init__(self, name=hook)
        self.hook = hook
        self.args = args
        self.kwds = kwds
        self.start()

    def run(self):
        try:
            for module in hooks[self.hook].keys():
                try:
                    hooks[self.hook][module](*self.args, **self.kwds)
                except Exception, message:
                   logging.error("Error calling hook %s on %s: %s" % (self.hook, module, traceback.format_exc()))
        except RuntimeError, message:
            logging.warn("Aborted hook %s due to looping failure: %s" % (self.hook, message))


class ModuleAlreadyLoaded(Exception): pass

def add_module(module,init=True):
    if modules.get(module):
        raise ModuleAlreadyLoaded, "%s has already been loaded."%module
    try:
        modules[module] = __import__(module,globals(),locals(),[],-1)
    except ImportError, e:
        logging.error("Error loading %s: %s" % (module, traceback.format_exc()))
        return
    except Exception, e:
        logging.error("Error loading %s: %s" % (module, traceback.format_exc()))
        return
    modules[module].add_hook = add_hook
    modules[module].remove_hook = remove_hook

    if init:
        try:
            init_module = getattr(modules[module], 'init')
        except AttributeError:
            init_module = None

    if init_module:
        try:
            init_module()
        except Exception, message:
            logging.error("Error loading %s: %s" % (module, traceback.format_exc()))
            return False
    call_hook('loaded',module)
    return True

def unload_module(module):

    if not module in modules:
        return False

    for hook in hooks:
        if hooks[hook].get(module):
            del hooks[hook][module]

    try:
        terminate_module = getattr(modules[module], 'terminate')
    except AttributeError:
        pass
    else:
        terminate_module()
    del sys.modules["modules.%s"%module]
    del modules[module]

    call_hook('unloaded',module)
    return True

def load_modules(list):
    for x in list:
        if x.strip()=="": continue
        x = x.replace('\n','')
        if x.startswith('/'): return
        try:
            if not x.startswith('#'): add_module(x)
        except ModuleAlreadyLoaded as e:
            print e

class Interface:
    
    interfaces = {}

    def reply(self, text, edit=False): pass
    def reply_to_sender(self, text):self.reply(text)
    @property
    def last_messages(self): pass
    @property
    def user_name(self): return "<user name>"
    @property
    def user_address(self): return "<user address>"
    @property
    def type(self):return 'Null'
    @property
    def is_editable(self): return False
    @property
    def chat_name(self): return "<chat name>"
    @property
    def bot_nick(self): return "<bot nick>"
    @property
    def bot_handle(self): return "<bot handle>"
    @property
    def interface_name(self): return "interfaces"
