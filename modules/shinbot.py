
import modules
import command
import random

nouns = [x[:-1] for x in open("data/nouns","r").readlines()]

def shuffle_hook(text,interface):

    r=[]

    for x in text.split():
        inner = x[1:-1]
        l = list(inner)
        random.shuffle(l)
        r.append(x[0]+''.join(l)+x[-1])

    newm = ' '.join(r)
    if newm!=text:
        if interface.is_editable:
            interface.reply(newm,edit=True)


def shinbro_hook(text,interface):
    newm=text
    keyboard=["qwertyuiop","asdfghjkl","zxcvbnm,."]
    for pos, char in enumerate(text):
        if random.randint(0,350)==1:
            dir = random.randint(0,10)
            y = 0
            x = 0
            for y, c in enumerate(keyboard):
                if char in c:
                    x = c.find(char)
                    if dir==0:
                        y=max(y-1,0)
                    elif dir==1:
                        y=min(y+1,2)
                    elif dir>1 and dir<7:
                        x=min(x+1,len(c)-1)
                    elif dir>=7 and dir <=10:
                        x=max(x-1,0)
                    newm = newm[:pos]+ keyboard[y][x] + newm[pos+1:]
    if newm!=text:
        if interface.is_editable:
            interface.reply(newm,edit=True)


def nouns_hook(text,interface):
    if random.randint(0,100)!=1: return
    new = text
    for x in text.split():
        if x.lower() in nouns:
            new = new.replace(x,random.choice(nouns),1 )

    if new!=text:
        if interface.is_editable:
            interface.reply(new,edit=True)

def hookhook(text,interface):
    if 'Joe' in interface.user_name and not 'spacerat' in interface.user_address:
        interface.reply(interface.user_address+ " is a silly.")

def init():

    modules.add_hook('message',nouns_hook)
    modules.add_hook('message',shinbro_hook)
    #modules.add_hook('message',hookhook)
    #modules.add_hook('message',shuffle_hook)

