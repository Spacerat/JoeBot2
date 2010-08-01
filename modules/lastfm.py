
import dynamic_core
import command
from libs.stringsafety import *
from libs import data

#-------LASTFM FUNCTIONS---------#
import urllib2
import json

lastfmurl = "http://ws.audioscrobbler.com/2.0/?"
keystring=''
formatstring = "&format=json"
datafile = ''
users = {}

class LastFMException(Exception): pass
class AliasAlreadyExistsError(LastFMException): pass
class LastfmFetchFailed(LastFMException): pass

def set_api_key(key):
    global keystring
    apikey = key
    keystring = "&api_key="+apikey

def get_recent_track(User):
    url = lastfmurl+"method=user.getrecenttracks&user={0}&limit=1{1}{2}".format(escapeurl(User),formatstring,keystring)
    request = urllib2.Request(url,None,{'Referer':'http://spacerat.meteornet.net'})
    response = urllib2.urlopen(request)
    results = json.load(response)

    if "recenttracks" in results:
        if "track" in results["recenttracks"]:

            if 'name' in results["recenttracks"]["track"]:
                return results["recenttracks"]["track"]
            else:
                return results["recenttracks"]["track"][0]

def get_artist_info(Artistname):
    url = lastfmurl+"method=artist.getinfo&artist={0}{1}{2}".format(escapeurl(Artistname),formatstring,keystring)
    request = urllib2.Request(url,None,{'Referer':'http://spacerat.meteornet.net'})
    response = urllib2.urlopen(request)
    results = json.load(response)
    return results

def alias_to_lastfm(name):
    alias = data.query('SELECT username FROM lastfm_alias WHERE alias = ?',(name.lower(),))
    if alias:
        return alias[0][0]
    else:
        return name

def listening(name):
    return get_recent_track(alias_to_lastfm(name))

def add_user_alias(alias, username):
    exists = data.query('SELECT alias,username FROM lastfm_alias WHERE alias = ?',(alias.lower(),))
    if exists:
        raise AliasAlreadyExistsError, alias
    else:
        if get_recent_track(username):
            return data.query('INSERT INTO lastfm_alias VALUES (?,?)',(alias.lower(),username))
        else:
            raise LastfmFetchFailed, alias

def tag_fetchfm(node,context):
    track = listening(eval(node.attribute,context.vars))
    if not track:
        context.vars['lastfm_success']=False
        return "[Unable to fetch Last.fm data for %s]"%node.attribute
    context.vars['lastfm_success']=True
    context.vars['lastfm_album']=track['album']['#text']
    context.vars['lastfm_track']=track['name']
    context.vars['lastfm_playing']= ('@attr' in track)
    context.vars['lastfm_artist']=track['artist']['#text']
    context.vars['lastfm_url']=track['url']

def command_addfm(interface,hook,args):
    if len(args.split())==2:
        args = args.split()
        try:
            result = add_user_alias(args[0],args[1])
        except AliasAlreadyExistsError:
            interface.reply("Cannot overwrite %s."%(args[0]))
        except LastfmFetchFailed:
            interface.reply("%s does not seem to be a valid Last.fm username."%args[1])
        else:
            if result:
                interface.reply("Alias successfully added.")
            else:
                interface.reply("The Alias was not added for an unknown reason.")

def init():
    data.query('''CREATE TABLE IF NOT EXISTS lastfm_alias
    (alias TEXT, username TEXT,
    PRIMARY KEY (alias))''')
    set_api_key(open("data/lastFMAPIKey.txt").readline())
    dynamic_core.register_tag('lastfm',tag_fetchfm)
    command.ComHook('addfm',command_addfm,name='fmBot')


#-----------------------------------#
'''
def ListeningHandle(interface,command,args,messagetype):
    """!listening [names] - Let everyone know what the people in a space separated list of names are listening to.
    If no names are given, !listening lets everyone know what you are listening to. The names can be lastfm usernames, or aliases added with !addfm"""
    edit = False
    names = args.split()
    if not names:
        names = [interface.UserAddress]
    if len(names)==1:
        edit=True

    for usr in names:
        try:
            if usr.lower() in users: usr = users[usr.lower()]
        except Exception as e:
            print repr(e)
            return
        track = GetRecentTrack(usr)
        if track:
            str = track["artist"]["#text"]+" - "+track["name"]
            current = ""
            if "@attr" in track:
                current = " is currently playing: "
            else:
                current = " last played: "

            interface.Reply(usr+current +str)#,edit=edit)
        else:
            interface.Reply(usr+" has never listened to anything. Ever. :(",edit=edit)

def ArtistHandle(interface,command,args,messagetype):
    """!artist name - Get information about a particular band/musician/artist."""
    info = GetArtistInfo(args)
    if info:
        content = info['artist']['bio']['content']
        artisturl = info['artist']['url']
        interface.Reply(artisturl)
        interface.Reply(FormatHTML(content)[0:400]+" ...")

def AddUsrHandle(interface,command,args,messagetype):
    """!addfm alias username - Adds alias as an alias for a lastfm username, to be used with !listening."""
    if len(args.split())==2:
        if args.split()[0].lower() in users:
            interface.Reply('Cannot overwrite existing user '+args.split()[0])
            return
        User = args.split()[1]
        url = lastfmurl+"method=user.getinfo&user={0}{1}{2}".format(escapeurl(User),formatstring,keystring)
        request = urllib2.Request(url,None)
        response = urllib2.urlopen(request)
        results = json.load(response)
        if 'user' in results:
            users[args.split()[0].lower()] = User
            ExportUserAliases()
            Handle(interface,'listening',User,messagetype)
    else:
        interface.Reply('use %saddfm Alias Username' % interface.GetPrefix())

def ListFMHandle(interface,command,args,messagetype):
    """!listfm - Retrieve the list of lastfm aliases."""
    interface.ReplyToSender(", ".join(users))

'''