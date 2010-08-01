
import random
import os
from dynamic_core import register_tag

#Almost entirely by Katharine (a modifcation or two by me):
#http://github.com/Katharine/KathBot3/blob/master/modules/dynamic.py#L710

def word_from_file(path):
    #This makes longer words slightly more likely, which I'm sure you know, but I suppose you've done it like this for the speed.
    size = os.stat(path).st_size
    pos = random.randint(0, size - 1)
    f = open(path)
    f.seek(pos)
    while f.read(1) != "\n":
        f.seek(-2, os.SEEK_CUR)
    word = ''
    while True:
        char = f.read(1)
        if char == "\n" or char == "":
            break
        word += char
    return word.strip()

def tag_noun(node, context):
    word = word_from_file('data/nouns')
    attribs = node.attribute.split()
    if 'plural' in attribs:
        vowels = 'aeiou'
        if word[-1] == 'y' and word[-2] not in vowels:
            word = "%sies" % word[0:-1]
        elif word[-1] == 's':
            word = "%ses" % word
        else:
            word = "%ss" % word
    if 'a' in attribs:
        if word[0] in 'aeiou':
            return "an "+word
        else:
            return "a "+word
    else:
        return word


def tag_verb(node, context):
    verb = word_from_file('data/verbs')
    tense = node.attribute or 'root'
    if tense == 'root':
        return verb
    elif tense == 'first' or tense == 'second':
        return verb
    elif tense == 'third':
        if verb[-1] in 'szx' or verb[-2:] in ('ch', 'sh'):
            return '%ses' % verb
        elif verb[-1] == 'y' and verb[-2] not in 'aeiou':
            return '%sies' % verb[:-1]
        else:
            return '%ss' % verb
    else:
        if verb[-1] not in 'aeiouy' and verb[-2] in 'aeiou':
            # This check sucks.
            if (len(verb) == 3 or (len(verb) == 4 and verb[-1] == 'p')):
                verb += verb[-1]

        if tense == 'pastpart' or tense == 'past':
            if verb[-1] == 'e':
                return '%sd' % verb
            elif verb[-1] == 'y' and verb[-2] not in 'aeiou':
                return '%sied' % verb[:-1]
            else:
                return '%sed' % verb
        elif tense == 'presentpart' or tense == 'gerund':
            if verb[-1] == 'e':
                return '%sing' % verb[:-1]
            else:
                return '%sing' % verb
        else:
            return '[unknown tense "%s"]' % tense

def tag_adjective(node, context):
    if node.attribute=="a":
        word = word_from_file('data/adjectives')
        if word[0] in 'aeiou':
            return "an "+word
        else:
            return "a "+word
    else:
        return word_from_file('data/adjectives')

def tag_adverb(node, context):
    return word_from_file('data/adverbs')

def tag_interjection(node, context):
    return word_from_file('data/interjections')

def tag_place(node, context):
        return word_from_file('data/places')

register_tag('noun',tag_noun)
register_tag('verb',tag_verb)
register_tag('adjective',tag_adjective)
register_tag('adverb',tag_adverb)
register_tag('interjection',tag_interjection)
register_tag('place',tag_place)