
import modules
import command

def command_load(interface,command,args):
    """~load modname - Load a module."""
    try:
        modules.add_module(args)
        interface.reply("Loaded %s"%args)
    except ImportError, e:
        interface.reply(str(e))
    except modules.ModuleAlreadyLoaded, e:
        interface.reply(str(e))

def command_unload(interface,command,args):
    """~unload modname - Unload a module."""
    modules.unload_module(args)
    interface.reply("Unloaded %s"%args)

def command_reload(interface,command,args):
    command_unload(interface,command,args)
    command_load(interface,command,args)

command.ComHook('load',command_load,security=4,name='ChatBot')
command.ComHook('unload',command_unload,security=4,name='ChatBot')
command.ComHook('reload',command_reload,security=4,name='ChatBot')
