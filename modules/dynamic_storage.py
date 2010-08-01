
import command
from libs import logging, data
import dynamic_core
from datetime import datetime

class CannotModifyStdFuncsError(Exception): pass
class InvalidFuncNameError(Exception): pass
class DynamicMetadataTagError(Exception): pass

def load_commands():
    #numcommands = data.query("SELECT COUNT(DISTINCT name) FROM dynamic")[0][0]
    #results = data.query("SELECT DISTINCT name, version, source FROM dynamic ORDER BY name, version DESC LIMIT %u"%numcommands)
    results = data.query("SELECT version,name, source FROM dynamic GROUP BY name")
    for result in results:
        command.ComHook(result[1],command_runfunc,name="%sBot"%result[1],data=result[2])
        logging.info(result[0],result[1])

def add_command(name, line, author):
    logging.info("Attempt to add function %s"%name)

    version = 0
    if "!" in name:
        raise InvalidFuncNameError, name
    if find_command(name):
        #logging.warn("Dynamic command %s already exists!"%name)
        version=find_command(name)[0][0]
    elif name in command.com_hooks:
        raise CannotModifyStdFuncsError, name


    data.query("INSERT INTO dynamic VALUES (?,?,?,?,'',?)",(version+1,name,line,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),author))
    command.ComHook(name,command_runfunc,name='%sBot'%name,data=line)
    
    return version+1

def find_command(name):
    result = data.query("SELECT * FROM dynamic WHERE name = ? ORDER BY version DESC",(name,))
    return result

def command_from_node(node,context):
    name=node.attribute
    if node.attribute=="":
        name = context.command
    if name=="": return "Specify a tag name."

    com = find_command(name)
    if not com:
        name = eval(name,context.vars)
        com = find_command(name)
    if com:
        return com
    else:
        return "Invalid tag name %s."%name

def command_addfunc(interface,hook,args):
    """!addfunc name:code - Adds or updates a dynamic function"""
    func = args.partition(":")
    name = func[0].strip()
    line = func[2].strip()
    version = add_command(name,line,interface.user_address)
    if version==0:
        interface.reply("Failed to add command %s"%name)
    elif version==1:
        interface.reply("Command %s added successfully."%name)
    else:
        interface.reply("Command %s updated to version %u"%(name,version))

def command_documentfunc(interface,hook,args):
    #todo
    pass

def command_runfunc(interface,hook,args):
    logging.info("Running dynamic function %s"%hook.hook)
    context = dynamic_core.TagContext(i=interface,args=args,command=hook.hook)
    interface.reply(dynamic_core.parse_markup(hook.data).process(context))


def tag_source(node,context):
    com = command_from_node(node,context)
    return com[0][2]

def tag_version(node,context):
    com = command_from_node(node,context)
    return com[0][0]

def tag_author(node,context):
    com = command_from_node(node,context)
    return com[-1][5]

def tag_updater(node,context):
    com = command_from_node(node,context)
    return com[0][5]

def init():
    data.query('''CREATE TABLE IF NOT EXISTS dynamic
    (version INTEGER, name TEXT, source TEXT, timestamp DATE, help TEXT, author TEXT,
    PRIMARY KEY (version, name))''')

    load_commands()

command.ComHook('addfunc',command_addfunc,security=2)
#command.ComHook('documentfunc',command_documentfunc,security=2)
dynamic_core.register_tag('dyn_source',tag_source)
dynamic_core.register_tag('dyn_version',tag_version)
dynamic_core.register_tag('dyn_author',tag_author)
dynamic_core.register_tag('dyn_updater',tag_updater)