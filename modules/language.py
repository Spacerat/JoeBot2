
import modules
import command
import random
import re
import json


word_dict = {}
active = 0

def add_possibility(word,following):
    if not word in word_dict:
        word_dict[word] = []
    word_dict[word].append(following)

def alphabetise(word):
    return re.sub(r'\W+', '', word).lower()

def learn(words):

    for n, word in enumerate(words):
        if n == len(words)-1:
            add_possibility(alphabetise(word),".")
            break
        if word.endswith("."):
            add_possibility(alphabetise(word[:-1]),".")


        word = alphabetise(word)
        following = alphabetise(words[n+1])
        add_possibility(word,following)

    json.dump(word_dict,open("data/language.txt","w"))

def respond_hook(text,interface):
    global word_dict
    global active
    if not active: return
    if interface.message_status!="RECEIVED": return

    words = text.split()
    learn(words)

    first = alphabetise(random.choice(words))

    f = first.capitalize()
    response = [f]
    next = first
    while next!='.':
        next = random.choice(word_dict.get(next,["."]))
        if not "." in next: next = alphabetise(next)
        response.append(next)

    interface.reply(" ".join(response))
    
def command_lolbot(i,command,args):
    global active

    active = 1-active


def init():
    global word_dict

    try:
        word_dict = json.load(open("data/language.txt"))
    except (IOError, ValueError):
        f = open("data/language.txt","w")
        f.write("{}")
        f.close()
        worword_dictds = json.load(open("data/language.txt"))

    modules.add_hook('message',respond_hook)
    command.ComHook("lolbot",command_lolbot)