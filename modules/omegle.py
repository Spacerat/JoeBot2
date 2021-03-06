
import modules
import command
from libs import omeglelib
import threading
import urllib2
from time import sleep

inpr = "+"
outpr = "&"

class Omg(threading.Thread):
    chats = {}

    def __init__(self,interface,named):
        threading.Thread.__init__(self)
        self.i = interface
        self.named = named
    def run(self):
        if self.i.chat_name in Omg.chats.keys():
            self.i.reply("An Omegle chat is already going on in this conversation!")
            return

        c = omeglelib.OmegleChat()
        self.chat=c
        self.chat.named = self.named
        Omg.chats[self.i.chat_name] = self
        c.connect_events(SkypeMeggleEvents(self.i))
        #c.debug=True
        try:
            c.connect(False)
        except urllib2.URLError, e:
            self.i.reply("Error while connecting!")
            self.i.reply("%s"%str(e))
            c.disconnect()


    def say(self,text,name):
        try:
            if self.named == True:
                self.chat.say("%s: %s"%(name[:3],text))
            else:
                self.chat.say(text)
        except urllib2.HTTPError, e:
            self.i.reply("%u Error while sending %s" %(e.code,text))


class SkypeMeggleEvents(omeglelib.EventHandler):

    def __init__(self,interface):
        self.i = interface

    def connected(self,chat,var):
        self.i.reply("OmegleBot: New chat started!")
        self.i.reply("Prefix messages with %s to send them to omegle."%inpr)

        if chat.named:
            sleep(1)
            chat.say("Hi there! You're currently talking to a room full of different people.")
        chat.in_chat = True
        #chat.say("Hello!")

    def gotMessage(self,chat,message):
        message = message[0]
        self.i.reply("%sStranger: %s"%(outpr, message))

    def typing(self,chat,var):
        print "Stranger is typing..."

    def stoppedTyping(self,chat,var):
        print "Stranger stopped typing!"

    def strangerDisconnected(self,chat,var):

        self.i.reply("OmegleBot: Stranger left.")
        del Omg.chats[self.i.chat_name]

    def terminate(self,chat,var):
        self.i.reply("Terminating OmegleBot.")
        del Omg.chats[self.i.chat_name]

def start_omegle(i,command,args):
    """~omegle <anon|named> - Starts an omegle session. You must specify either anonymous or named mode.
    In anon, Stranger cannot distinguish between skype users. In named mode, The first three letters of your nickname are prepended to your message.
    Use ~endomegle to end the session."""
    if args=='anon':
        Omg(i,False).start()
    elif args=='named':
        o = Omg(i,True)
        o.start()
    else:
        i.name = "Help"
        #interface.HelpHandle(i,'help',command)


def end_omegle(i,command,args):
    """!endomegle - Ends an omegle session running in this channel."""
    try:
        c = Omg.chats[i.chat_name]
        c.chat.disconnect()
    except Exception as e:
        print e
        i.reply("There is no omegle session currently running in this conversation.")

def message_hook(text,interface):
    if not hasattr(Omg,'chats'):
        Omg.Chats = {}
    c = Omg.chats.get(interface.chat_name,None)
    if not c: return
    if c.chat.terminated: return

    if text[0] == inpr:
        text = text[1:]
    elif text[0:2] == inpr+outpr or text[0:2] == outpr+inpr:
        text = text[2:]
    else:
        return

    if text.startswith("Stranger:"):
        text = text[9:]
    print "Sending "+text
    c.say(text,interface.user_name)

def terminate():
    print "Terminating chats."
    for c in Omg.chats.itervalues():
        c.chat.disconnect()
    Omg.chats={}

def init():

    command.ComHook('omegle',start_omegle)
    command.ComHook('endomegle',end_omegle)
    modules.add_hook('message',message_hook)