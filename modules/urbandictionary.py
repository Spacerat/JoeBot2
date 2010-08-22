
import command
from BeautifulSoup import BeautifulSoup
from libs.stringsafety import *
import urllib2

def command_ud(interface,command,args):
    """!ud phrase - Look up a phrase on urban dictionary."""
    url = "http://www.urbandictionary.com/"+escapeurl(args)
    response = urllib2.urlopen(url)
    doc = BeautifulSoup(response)
    defin = doc.find("div",{"class":"definition"})
    interface.reply(args+" - "+FormatHTML(defin.renderContents()))

def init():
    command.ComHook('ud',command_ud,name='UrbanBot')
