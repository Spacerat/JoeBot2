
from dynamic_core import *
from random import randint, seed
import gc


def tag_choose(node,context):
    """<choose>stuff[or]stuff[|]stuff</choose> - Pick a random item from a list separated by [or] or [|] tags."""
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
    """<if expression>stuff[elif another_expression]other_stuff[else]stuff3</if> - Display stuff if expression is true. Optionally do other_stuff if another_expression is true, or do stuff3 if no expressions are true."""
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
    """<for varname in list>Do stuff with [varname]</for> - Loop through list, setting varname to each value in the list in turn."""
    com = node.attribute.partition('in')
    if not (com[0].strip() and com[2].strip()):
        return "[use for x in list]"

    varname = com[0].strip()
    listname = com[2].strip()

    if listname in context.vars:
        list=context.vars[listname]
    else:
        list = eval(listname,context.vars)

    if len(list)>200:
        return "[List is too large.]"

    prev_value = context.vars.get(varname,None)
    r=''
    for x in list:
        context.vars[varname] = x
        r+=node.process_children(context)
    if prev_value:
        context.vars[varname]=prev_value
    else:
        pass
        #del context.vars[varname]
    return r


def tag_random(node,context):
    """[random list] OR [random x:y] - Either pick a random value from a list, or a random number between x and y."""
    article=None
    seed()
    if node.attribute in context.vars:
        article=context.vars[node.attribute]
    elif ":" in node.attribute:
        s = node.attribute.partition(":")
        return randint(int(s[0]), int(s[2]))
        #article = range(int(s[0]),int(s[2]))
    else:
        article = eval(node.attribute,context.vars)
    if article:
        ret = article[randint(0,len(article)-1)]
        article = None
        gc.collect()
        return ret

def tag_try(node,context):
    """<try expression>fallback</try> OR <try>expression[else]fallback</try> - Return expression if it has a value, else return fallback."""
    if node.attribute:
        if node.attribute in context.vars:
            if context.vars[node.attribute]:
                return context.vars[node.attribute]
        return node.process_children(context)
    else:
        test=''
        testing=False
        resnodes=[]
        oldstrict=context.strict
        context.strict=False
        for child in node.children:
            if child.name=='else':
                testing=True
                continue
            if testing==False:
                test+=stringify(child.process(context))
            else:
                resnodes.append(child)
        if test=='':
            value=''
            context.strict=oldstrict
            for child in resnodes:
                value+=stringify(child.process(context))
            return value
        else:
            return test

def init():
    register_tag('choose',tag_choose)
    register_tag('if',tag_if)
    register_tag('random',tag_random)
    register_tag('for',tag_for)
    register_tag('try',tag_try)