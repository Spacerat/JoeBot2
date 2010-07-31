
from dynamic_core import *
from random import randint, seed

def tag_chose(node,context):
    seed()
    choices = []
    choice = []
    for child in node.children:
        if child.name=='or':
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
            value+=child.process(context)
        return value
    else:
        startprocess=False
        value=''
        for child in node.children:
            if startprocess:
                if child.name=='else' or child.name=='elif':
                    break
                value+=child.process(context)
            elif child.name=='else':
                startprocess=True
            elif child.name=='elif':
                test = eval(child.attribute,context.vars)
                if test: startprocess=True
        return value

def tag_random(node,context):
    article=None
    seed()
    if node.attribute in context.vars:
        article=context.vars[node.attribute]
    if article:
        return article[randint(0,len(article)-1)]

def init():
    register_tag('choose',tag_chose)
    register_tag('if',tag_if)
    register_tag('random',tag_random)
