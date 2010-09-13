
import urllib2
import command

def command_randomtopic(i,command,args):
    """!randomtopic - Sets a random conversation topic. Can only be used once every 20 seconds."""

    url = "http://www.iheartquotes.com/api/v1/random?source=oneliners+why+sex+misc+technology"
    request = urllib2.Request(url,None,{})
    response = urllib2.urlopen(request)
    r = " ".join(response.readlines())

    text = unicode(r.rpartition('\n \n')[0].replace("\n",''),errors='ignore')

    i.set_topic(text)

def init():
    command.ComHook("randomtopic",command_randomtopic,"TopicBot")
