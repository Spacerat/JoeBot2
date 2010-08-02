
from dynamic_core import register_tag
import command
import random

#A collection of miscillaneous tags

def tag_rnick(node,context):
    users = context.vars['users']
    return users[random.randint(0,len(users)-1)]

def tag_help(node,context):
    return command.get_command(dynamic_core.get_var(node.attribute,context)).help(context.interface.prefix)

def context_hook(context):
    context.vars['commands']=command.com_hooks.keys()

def init():
    register_tag('rnick',tag_rnick)
    register_tag('help',tag_help)
    add_hook('context',context_hook)