
from dynamic_core import *
from random import randint, seed

def tag_chose(node,context):
    seed()
    choices = []
    choice = []
    for child in node.children:
        if child.name=='or' or child.name=='|':
            choices.append(choice)
            if child.type=='cont':
                choices.append(child.children)
            choice=[]
            continue
        choice.append(child)
    choices.append(choice)

    choice = choices[randint(0,len(choices)-1)]
    r=''
    for child in choice:
        r+=child.process(context)
    return r

def tag_if(node,context):
    test = eval(node.attribute, context.vars)
    if test:
        value=''
        for child in node.children:
            if child.name=='else':
                break
            value+=stringify(child.process(context))
        return value
    else:
        startprocess=False
        value=''
        for child in node.children:
            if startprocess:
                if child.name=='else' or child.name=='elif':
                    break
                value+=stringify(child.process(context))
            elif child.name=='else':
                startprocess=True
            elif child.name=='elif':
                test = eval(child.attribute,context.vars)
                if test: startprocess=True
        return value

def tag_for(node,context):
    com = node.attribute.partition('in')
    if not (com[0].strip() and com[2].strip()):
        return "[use for x in list]"

    varname = com[0].strip()
    listname = com[2].strip()

    list = eval(listname,context.vars)
    if len(list)>50:
        return "[List is too large.]"

    prev_value = context.vars.get(varname,None)
    r=''
    for x in list:
        context.vars[varname] = x
        r+=node.process_children(context)
    if prev_value:
        context.vars[varname]=prev_value
    else:
        del context.vars[varname]
    return r


def tag_random(node,context):
    article=None
    seed()
    if node.attribute in context.vars:
        article=context.vars[node.attribute]
    elif ":" in node.attribute:
        s = node.attribute.partition(":")
        article = range(int(s[0]),int(s[2]))
    else:
        article = eval(node.attribute,context.vars)
    if article:
        return article[randint(0,len(article)-1)]

def tag_try(node,context):
    if node.attribute in context.vars:
        if context.vars[node.attribute]:
            return context.vars[node.attribute]
    '''
        try:
            e = eval(node.attribute,context.vars)
        except AttributeError:
            pass
        else:
            if e != None:
                return e
    '''
    return node.process_children(context)

def init():
    register_tag('choose',tag_chose)
    register_tag('if',tag_if)
    register_tag('random',tag_random)
    register_tag('for',tag_for)
    register_tag('try',tag_try)