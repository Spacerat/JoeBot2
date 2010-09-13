
import modules
import command
import re

from libs import data
autoreplace = True

def command_toggle_autoreplace(i,command,args):
    global autoreplace
    """~autoreplace - Toggles the autoreplace bot."""
    if autoreplace == True:
        autoreplace = False
        i.reply("Disabled.")
    else:
        autoreplace = True
        i.reply("Enabled.")

def find_replacement(text):
    q = data.query("SELECT * FROM replacebot_subs WHERE find = ?",(text,))
    if q:
        return q[0]

def add_replacement(find,replace,regex,setby):
    exists = find_replacement(find)
    if exists:
        data.query('''UPDATE replacebot_subs SET replace=?,is_regex=?,setby=? WHERE find=? ''',(replace,regex,setby,find))
    else:
        data.query('''INSERT INTO replacebot_subs VALUES (?,?,?,?)''',(find,replace,regex,setby))

def get_all_replacements():
    return data.query('''SELECT * FROM replacebot_subs''')

def command_replace(i,command,args):
    args=args.rpartition("->")
    find=args[0].strip().lower()
    replace=args[2].strip().lower()
    if find=="" or replace=="":
        i.reply("Use !replace find->replace.")
        return
    add_replacement(find,replace,False,i.user_name)
    i.reply("Replacing %s with %s."%(find,replace))

def command_rxreplace(i,command,args):
    args=args.rpartition("->")
    find=args[0].strip()
    replace=args[2].strip()
    if find=="" or replace=="":
        i.reply("Use !rxreplace regex->replace.")
        return
    add_replacement(find,replace,True,i.user_name)
    i.reply("Regex subbing %s with %s."%(find,replace))

def command_unreplace(i,command,args):

    find = args
    r = find_replacement(find)
    if not r:
        find = args.lower()
        r = find_replacement(find)
    if r:
        data.query('''DELETE FROM replacebot_subs WHERE find=?''',(find,))
        i.reply("%s no longer replaces to %s."%(args,r[1]))
    else:
        i.reply("%s is not currently being replaced."%args)

def command_getreplacements(i,command,args):
    reply = "\n"
    for r in get_all_replacements():
        find = r[0]
        replace = r[1]
        is_regex = r[2]
        by = r[3]
        if is_regex:
            reply+="%s -> %s regex by %s\n"%(find,replace,by)
        else:
            reply+="%s -> %s by %s\n"%(find,replace,by)
    i.reply(reply)
            

def message_hook(text,interface):
    global autoreplace
    if not autoreplace: return
    if text.startswith("ReplaceBot:"): return
    i = interface
    if not i.is_editable: return
    if text.strip()=="": return

    old_text = text
    new_text = text

    quote = re.search(r'\[\d\d:\d\d:\d\d\](.*?)<<<',old_text,re.DOTALL)
    if quote: old_text = old_text.replace(quote.group(0)," "*len(quote.group(0)))

    for replacement in get_all_replacements():
        find = replacement[0]
        replace = replacement[1]
        is_regex = replacement[2]
        if not is_regex:

            pos = old_text.lower().find(find.lower())
            while pos>=0:
                cword = old_text[pos:pos+len(find)]
                rword=""
                if cword.isupper():
                    rword = replace.upper()
                elif cword.islower():
                    rword = replace.lower()
                elif cword.istitle():
                    rword = replace.capitalize()
                else:
                    rword = replace

                old_text = old_text.replace(cword," "*len(rword),1)
                new_text = new_text.replace(cword,rword,1)

                pos = old_text.lower().find(find.lower())
        else:
            matches = re.finditer(find,old_text,re.I)
            for match in matches:
                found = match.group(0)
                substitute = match.expand(replace)
                old_text = old_text.replace(found," "*len(substitute))
                new_text = new_text.replace(found,substitute,1)

    if new_text!= text: i.reply(new_text,edit=True)



def init():

    command.ComHook('autoreplace',command_toggle_autoreplace)
    command.ComHook('replace',command_replace,"ReplaceBot")
    command.ComHook('rxreplace',command_rxreplace,"ReplaceBot")
    command.ComHook('unreplace',command_unreplace,"ReplaceBot")
    command.ComHook('getreplacements',command_getreplacements,"ReplaceBot")
    modules.add_hook('message',message_hook)

    data.query('''CREATE TABLE IF NOT EXISTS replacebot_subs
    (find TEXT, replace TEXT, is_regex INTEGER,  setby TEXT,
    PRIMARY KEY (find))''')
