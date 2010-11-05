
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
    if modules.unload_module(args):
        interface.reply("Unloaded %s"%args)
    else:
        interface.reply("No module called "+args)

def command_reload(interface,command,args):
    """~reload modname - Reload a module."""
    command_unload(interface,command,args)
    command_load(interface,command,args)

def get_connections(interface,command,args):
    print modules.Interface.interfaces

command.ComHook('load',command_load,security=4,name='ChatBot',prefix="~")
command.ComHook('unload',command_unload,security=4,name='ChatBot',prefix="~")
command.ComHook('reload',command_reload,security=4,name='ChatBot',prefix="~")
command.ComHook('getconns',get_connections,security=4,name='ChatBot',prefix="~")
