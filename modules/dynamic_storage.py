
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
    results = data.query("SELECT version,name,source,help FROM dynamic GROUP BY name")
    for result in results:
        hook = command.ComHook(result[1],command_runfunc,name="%sBot"%result[1],data=result[2])
        hook.set_help(result[3])

def add_command(name, line, author):
    logging.info("Attempt to add function %s"%name)

    version = 0
    help=''
    if "!" in name:
        raise InvalidFuncNameError, name
    if find_command(name):
        #logging.warn("Dynamic command %s already exists!"%name)
        version=find_command(name)[0]['version']
        help=find_command(name)[0]['help']
    elif name in command.com_hooks:
        raise CannotModifyStdFuncsError, name


    data.query("INSERT INTO dynamic VALUES (?,?,?,?,?,?)",(version+1,name,line,datetime.now().strftime('%Y-%m-%d %H:%M:%S'),help,author))
    command.ComHook(name,command_runfunc,name='%sBot'%name,data=line)
    
    return version+1

def dictify_result(result):
    d = {}
    d['version'] = result[0]
    d['name'] = result[1]
    d['source'] = result[2]
    d['timestamp'] = result[3]
    d['help'] = result[4]
    d['author'] = result[5]
    for i, v in enumerate(result):
        d[i] = v
    return d

def find_command(name):
    result = data.query("SELECT * FROM dynamic WHERE name = ? ORDER BY version DESC",(name,))
    r = []
    for x in result:
        r.append(dictify_result(x))
    return r

def document_func(funcname,doc):
    com = find_command(funcname)[0]
    if com:
        result = data.query("UPDATE dynamic SET help=? WHERE version=? AND name=?",(doc,com['version'],funcname))
        command.get_command(funcname).set_help(doc)
        return result
    else:
        raise InvalidFuncNameError,funcname

def get_command_from_node(node,context):
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
    """~addfunc name:code - Adds or updates a dynamic function"""
    func = args.partition(":")
    name = func[0].strip()
    line = func[2].strip()
    try:
        dynamic_core.parse_markup(line)
    except dynamic_core.ParseError as e:
        interface.reply(str(e))
        return
    
    version = add_command(name,line,interface.user_address)
    if version==0:
        interface.reply("Failed to add command %s"%name)
    elif version==1:
        interface.reply("Command %s added successfully."%name)
    else:
        interface.reply("Command %s updated to version %u"%(name,version))

def command_document_func(interface,hook,args):
    """~docfunc name help - Add help for a dynamic function. Any instances of ~ will be replaced with the current prefix."""
    p = args.partition(" ")

    name = p[0].strip()
    help = p[2].strip()
    if not (name and help):
        interface.reply(hook.help(interface.prefix))
        return
    try:
        document_func(name,help)
    except InvalidFuncNameError:
        interface.reply("%s does not exist!"%name)
    else:
        interface.reply("Documentation successful.")



def command_runfunc(interface,hook,args):
    #logging.info("Running dynamic function %s"%hook.hook)
    context = dynamic_core.TagContext(i=interface,args=args,command=hook.hook)
    interface.reply(dynamic_core.parse_markup(hook.data).process(context))


def tag_source(node,context):
    com = get_command_from_node(node,context)
    return com[0][2]

def tag_version(node,context):
    com = get_command_from_node(node,context)
    return com[0][0]

def tag_author(node,context):
    com = get_command_from_node(node,context)
    return com[-1][5]

def tag_updater(node,context):
    com = get_command_from_node(node,context)
    return com[0][5]

def init():
    data.query('''CREATE TABLE IF NOT EXISTS dynamic
    (version INTEGER, name TEXT, source TEXT, timestamp DATE, help TEXT, author TEXT,
    PRIMARY KEY (version, name))''')

    load_commands()

    command.ComHook('addfunc',command_addfunc,security=2)
    command.ComHook('docfunc',command_document_func,security=2)
    #command.ComHook('documentfunc',command_documentfunc,security=2)
    dynamic_core.register_tag('dyn_source',tag_source)
    dynamic_core.register_tag('dyn_version',tag_version)
    dynamic_core.register_tag('dyn_author',tag_author)
    dynamic_core.register_tag('dyn_updater',tag_updater)
