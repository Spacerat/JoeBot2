
from dynamic_core import register_tag, registered_tags, get_var, stringify, get_tag_help
import command
import random

#A collection of miscillaneous tags

def tag_rnick(node,context):
    """[rnick] - Returns a random user nickname."""
    users = context.vars['users']
    return users[random.randint(0,len(users)-1)]

def tag_help(node,context):
    """[help command] - Returns the documentation for command."""
    return command.get_command(get_var(node.attribute,context)).help(context.interface.prefix)

def tag_taghelp(node,context):
    """[taghelp tag] - Returns the documentation for a tag."""
    return get_tag_help(get_var(node.attribute,context))
def tag_newline(node,context):
    """[nl] - Returns a new line."""
    return "\n"
def tag_lower(node,context):
    """<lower>string</lower> - Returns the tag children in lowercase."""
    return node.process_children(context).lower()
def tag_upper(node,context):
    """<upper>string</upper> - Returns the tag children in lowercase."""
    return node.process_children(context).upper()
def tag_nospaces(node,context):
    """<nospaces>string</upper> - Removes whitespace from the string."""
    return node.process_children(context).replace(" ","")
def tag_str(node,context):
    v = ""
    for child in node.children:
        v+=stringify(child.process(context))
    return v
def tag_stripstr(node,context):
    v = tag_str(node,context)
    return v.strip()

def context_hook(context):
    context.vars['commands']=command.com_hooks.keys()
    context.vars['tags']=registered_tags.keys()


def init():
    register_tag('rnick',tag_rnick)
    register_tag('help',tag_help)
    register_tag('taghelp',tag_taghelp)
    register_tag('nl',tag_newline)
    register_tag('upper',tag_upper)
    register_tag('lower',tag_lower)
    register_tag('nospaces',tag_nospaces)
    register_tag('str',tag_str)
    register_tag('stripstr',tag_stripstr)
    add_hook('context',context_hook)