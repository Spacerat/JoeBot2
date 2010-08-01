
#This is an adaption/rewrite of http://github.com/Katharine/KathBot3/blob/master/modules/dynamic.py
#You will likely notice lots of identical code, but there are a number of fundamental differences between this and that.

import inspect
import os
import re
import modules
import command

registered_tags={}
module_registrations={}

class ParseError(Exception): pass
class TagTypeError(Exception): pass
class TagAlreadyExists(Exception): pass


class Parser:
    ltag='['
    rtag=']'
    lcont='<'
    rcont='>'

class TagContext():
    def __init__(self, args='', command='', strict=True,i=None):
        self.strict = strict
        self.args = args
        self.command = command
        self.vars = {
            'args': args,
            'arglist': args.split(),
            'command': command,
            '__builtins__': None
        }
        if i:
            self.vars['sender']=i.user_name
            self.vars['users']=i.users.keys()
        for x, arg in enumerate(args.split()):
            self.vars["arg%s"%x]=arg

class Node:

    treestring_depth=' '

    def treestring(self,depth=0): pass
    def process(self,context): pass

    @property
    def type(self):
        return 'base'

class StringNode(Node):
    def __init__(self,tag):
        self.tag = tag
        self.name = ''
    def treestring(self,depth=0):
        return "\n"+Node.treestring_depth*depth+self.tag
    def __str__(self):
        return self.tag
    def process(self,context):
        return self.tag

    @property
    def type(self):
        return 'string'

class TagNode(Node):
    def __init__(self, tag):
        self.tag = tag
        self.name = tag.partition(' ')[0]
        self.attribute = tag.partition(' ')[2]
    def treestring(self,depth=0):
        return "\n"+Node.treestring_depth*depth + Parser.ltag + self.tag + Parser.rtag
    def process(self,context):
        if self.name in context.vars:
            return context.vars[self.name]
        elif self.name in registered_tags:
            return registered_tags[self.name](self,context)
        else:
            if context.strict == True:
                return "[%s is not a registered tag name.]"%self.name
            else:
                return self.tag

    @property
    def type(self):
        return 'tag'

class ContainerNode(Node):
    def __init__(self, tag):
        self.tag = tag
        self.name = tag.partition(' ')[0]
        self.attribute = tag.partition(' ')[2]
        if self.name[0]=='/':
            self.name=self.name[1:]
            self.closing = True
        else:
            self.closing = False

        self.children=[]

    def add_child(self,child):
        if child is None or child==None or child=='': return
        if isinstance(child,basestring):
            child = StringNode(str(child))

        child.parent_node=self
        self.children.append(child)

    def treestring(self,depth=0):
        r="\n"+Node.treestring_depth*depth+Parser.lcont + self.tag + Parser.rcont#+str(len(self.children))
        for c in self.children:
            try:
                r+=c.treestring(depth+2)
            except AttributeError:
                r+="\n"+Node.treestring_depth*(depth+2)+str(c)
        r+="\n"+Node.treestring_depth*depth+Parser.lcont +"/"+self.tag + Parser.rcont
        return r

    def process(self,context=TagContext()):
        if self.name in registered_tags:
            return registered_tags[self.name](self,context)
        else:
            if context.strict == True:
                raise ParseError, "%s is not a registered tag name."%self.name
            else:
                return self.process_children(context)

    def process_children(self,context):
        value=''
        for child in self.children:
            value += stringify(child.process(context))
        return value

    @property
    def type(self):
        return 'cont'

def stringify(string):
    if string is None:
        return ''
    elif isinstance(string, basestring):
        return string
    else:
        return str(string)

#The next two functions were essentially copy/pasted :3
def get_calling_module():
    record = inspect.stack()[2][1]
    filename = os.path.split(record)
    if filename[1].startswith('__init__.py'):
        filename = os.path.split(filename[0])

    module = filename[1].split('.')[0]

    return module

def register_tag(name,callback):
    if name in registered_tags:
        raise TagAlreadyExists, name
    module = get_calling_module()
    registered_tags[name] = callback
    if module not in module_registrations:
        module_registrations[module]=[]
    module_registrations[module].append(name)


def parse_markup(line):
    root = ContainerNode('root')
    current_node = root
    text = ''
    in_tag=0

    for c in line:
        #tags []
        if c==(Parser.ltag or c==Parser.lcont) and in_tag>0:
            in_tag+=1
        if c==Parser.ltag and in_tag==False:
            current_node.add_child(text)
            in_tag+=1
            text=''
        elif c==Parser.rtag:
            in_tag-=1
            if in_tag>0: continue
            current_node.add_child(TagNode(text))
            text=''
        #containers <>
        elif c==Parser.lcont and in_tag==False:
            current_node.add_child(text)
            in_tag+=1
            text=''
        elif c==Parser.rcont:
            in_tag-=1
            if in_tag>0: continue
            node = ContainerNode(text)
            if node.closing:
                if node.name == current_node.name:
                    current_node = current_node.parent_node
                else:
                    raise ParseError, "Mismatched closing %s/%s%s; expecting %s/%s%s." % (Parser.lcont,node.name,Parser.rcont,Parser.lcont,current_node.name,Parser.rcont)
            else:
                current_node.add_child(node)
                current_node = node
            text=''

        else:
            text+=c

    current_node.add_child(text)

    return root

#certain modules may want to reserve tags which do nothing.
def tag_null(node,context):
    pass

def tag_root(node,context):
    return node.process_children(context)

def command_eval(interface,hook,args):
    """!eval expression - Evaluate an expression."""
    context = TagContext(i=interface)
    interface.reply(parse_markup(args).process(context))

def hook_unloaded(module):
    if module in module_registrations:
        for tag in module_registrations[module]:
            del registered_tags[tag]
        del module_registrations[module]


def init():
    modules.add_hook('unloaded',hook_unloaded)
    register_tag('root',tag_root)
    command.ComHook('eval',command_eval,name='EvalBot')
