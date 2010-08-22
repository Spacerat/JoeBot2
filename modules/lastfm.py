
import dynamic_core
import command
from sqlite3 import IntegrityError
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

    if get_recent_track(username):
        return data.query('INSERT INTO lastfm_alias VALUES (?,?)',(alias.lower(),username))
    else:
        raise LastfmFetchFailed, alias

def tag_fetchfm(node,context):
    """[lastfm name] - Fetch lastfm data for name. Returns nothing, but sets the value of [lastfm_success], and possibly [lastfm_album], [lastfm_track], [lastfm_playing], [lastfm_artist] and [lastfm_url]."""
    track = listening(dynamic_core.get_var(node.attribute,context))
    if not track:
        context.vars['lastfm_success']=False
        return ""#[Unable to fetch Last.fm data for %s]"%node.attribute
    context.vars['lastfm_success']=True
    context.vars['lastfm_album']=track['album']['#text']
    context.vars['lastfm_track']=track['name']
    context.vars['lastfm_playing']= ('@attr' in track)
    context.vars['lastfm_artist']=track['artist']['#text']
    context.vars['lastfm_url']=track['url']

def command_addfm(interface,hook,args):
    """~addfm alias lastfm_username - Adds a new alias for the given username"""
    if len(args.split())==2:
        args = args.split()
        try:
            result = add_user_alias(args[0],args[1])
        except IntegrityError:
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
