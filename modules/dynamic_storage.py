
import command
import json
from libs import logging, data
import dynamic_core

class CannotModifyStdFuncsError(Exception): pass
class InvalidFuncNameError(Exception): pass

def get_datasource(flag=''):
    url = "data/commands.txt"
    try:
        f = open(url)
    except:
        dict={}
        f = open(url,'w')
        json.dump(dict,f)
        f.close()
    f = open(url,'r')
    data = json.load(f)
    f.close()
    if flag: f = open(url,flag)
    return {'file':f,'data':data}

def load_commands():
    data = get_datasource()['data']
    for c in data:
        logging.info("Adding command %s as %s"%(c,data[c]))
        command.ComHook(c,command_runfunc,name="%sBot"%c,data=data[c])


def add_command(name, line):
    data = get_datasource('w')
    logging.info("Attempt to add function %s"%name)
    if "!" in name:
        raise InvalidFuncNameError, name
    if name in data['data']:
        logging.warn("Dynamic command %s already exists!"%name)
    elif name in command.com_hooks:
        raise CannotModifyStdFuncsError, name
    data['data'][name] = line
    json.dump(data['data'],data['file'])
    command.ComHook(name,command_runfunc,name='%sBot'%name,data=line)
    data['file'].close()
    return True

def find_command(name):
    commands = get_datasource()
    return commands['data'].get('name')

def command_addfunc(interface,hook,args):
    func = args.partition(":")
    name = func[0].strip()
    line = func[2].strip()
    if add_command(name,line):
        interface.reply("Command %s added successfully."%name)

def command_runfunc(interface,hook,args):
    logging.info("Running dynamic function %s"%hook.hook)
    context = dynamic_core.TagContext(i=interface,args=args)
    interface.reply(dynamic_core.parse_markup(hook.data).process(context))

def init():
    load_commands()

command.ComHook('addfunc',command_addfunc,security=2)
