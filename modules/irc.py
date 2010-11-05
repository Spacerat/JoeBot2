
import sys
import socket
import string
import modules
import command
import threading
import json
import re

class IRCInterface(modules.Interface):

    def __init__(self, irc, channel, Message,nick="",host=""):
        self.irc = irc

        self.channel = channel
        self.chat_name = self.channel.name
        self.interface_name = irc.network.server+self.channel.name

        self.nick=nick
        self.user_name = self.nick

        self.host=host
        self.user_address = self.host

        self.bot_handle = irc.network.nick
        self.name='IRCRobot'
        self.type='IRC'
        self.prefix="$"
        self.is_editable = False
        self.message_status = 'RECEIVED'

    def reply(self, text, edit=False):
        for line in text.split("\n"):
            self.irc.msg(self.channel.name,line)

    def set_topic(self,topic):
        self.irc.set_topic(self.channel.name,topic)

    @property
    def last_messages(self):
        return []

    @property
    def users(self):
        r = []
        for x in self.channel.nicks:
            r.append(x)
        return r


class User():
    def __init__(self,username, address, nick, realname):
        self.username = username
        self.address = address
        self.nick = nick
        self.realname = realname

class Channel():
    def __init__(self, name, nicks=None):
        self.name = name
        self.nicks = {}

class IRC(threading.Thread):

    connected = {}

    def __init__(self,network,i=None):
        self.network = network
        self.connected = False
        self.debug = False
        self.interface = i
        self.channels = {}
        self.prefixes = ""
        IRC.connected[network.name] = self
        threading.Thread.__init__(self)

    def dprint(self, stuff):
        if self.debug:
            if self.interface:
                i.reply(stuff)
            else:
                print stuff

    def oprint(self,stuff):
        if self.interface:
            i.reply(stuff)
        else:
            print stuff

    def join(self,channel):

        self.send("JOIN %s" % channel)
        self.send("WHO %s"%channel)
        self.channels[channel] =  Channel(channel)

        if not self.network.server+channel in modules.Interface.interfaces:
            modules.Interface.interfaces[self.network.server+channel] = IRCInterface(self,self.channels[channel],"")

    def run(self):
        dprint = self.dprint
        oprint = self.oprint
        oprint("IRC Starting.")
        self.sock = socket.socket()
        self.sock.connect((self.network.server,int(self.network.port)))
        self.send("NICK %s\r\n" % self.network.nick)
        self.send("USER %s 8 *: %s" % (self.network.ident, self.network.realname))
        self.send("PONG")
        self.connected = True

        readbuffer=""
        while self.connected:
            readbuffer=readbuffer+self.sock.recv(1024)
            temp=string.split(readbuffer, "\n")
            readbuffer=temp.pop( )

            
            for line in temp:
                line=string.rstrip(line)
                dprint(line)
                cmd=''
                nick=''
                host=''
                if line[0]==":":
                    hostmask, line = line[1:].split(' ',1)
                    if "!" in hostmask:
                        nick = hostmask.split("!")[0]
                        host = hostmask.split("!")[1]
                    else:
                        host=hostmask
                else:
                    pass

                parts = line.split(' :',1)
                args = parts[0].split()
                cmd=args[0]

                if cmd=="PING":
                    self.send("PONG %s" % parts[1])
                elif cmd=="MODE":
                    oprint("Connected.")
                    for s in self.network.channels:
                        self.join(s)
                elif cmd=="005":

                    s = re.search(u'PREFIX=\(\w*?\)(.*?) ',line)
                    if s:
                        self.prefixes = s.group(1)
                elif cmd=="352":
                    dprint(parts)
                    dprint(args)
                    name = parts[1].partition(" ")[2]
                    usr = User(args[3], args[4], args[6],name)
                    self.channels[args[2]].nicks[usr.nick] = usr

                elif cmd=="NICK":

                    for c in self.channels:
                        if nick in self.channels[c].nicks:
                            usr = self.channels[c].nicks[nick]
                            del self.channels[c].nicks[nick]
                            self.channels[c].nicks[parts[0].partition(" ")[2]] = usr
                elif cmd=="PRIVMSG":
                    message=parts[1]
                    channel=args[1]
                    #print nick,host,message
                    #try:
                    modules.call_hook('message',message, interface = IRCInterface(self,self.channels[channel],message,nick=nick,host=host))
                    #RecieveMessage()
                    #except Exception as e:
                    #    print str(e)


    def send(self, str):
        #Lock is a good idea. Do that at some point.
#        print "OUTPUT:", "%s\r\n" % str
        self.sock.send(("%s\r\n" % str).encode('utf-8','ignore'))

    def msg(self,channelname,message):
        self.send("PRIVMSG "+channelname+" :"+message)

    def set_topic(self,channelname,topic):
        self.send("TOPIC "+channelname+" :"+topic)

    def disconnect(self, reason=""):
        self.send("QUIT :"+reason)

#Yoink. Thanks Katharine.
class Network:
    server = ''
    port = 6667
    nicks = ()
    realname = ''
    ident = ''
    primary_channel = None
    name = ''
    password = None

    def __init__(self, server='', port=6667, nick=None, realname='', ident='', channels=None, name='', password=None):
        self.server = server
        self.port = port
        self.nick = nick
        self.realname = realname
        self.ident = ident
        self.channels = channels
        self.name = name
        self.password = password

    def __str__(self):
        return self.name



def command_irc(i,command,args):
    global networks

    """!irc network|saved_network <channel> - Connect to an irc network/channel."""
    args=args.split()
    if len(args)==0:
        for n in networks:
            i = IRC(Network(**networks[n]))
            i.start()

    elif len(args) == 1:
        n = networks[args[0]]
        i = IRC(Network(**n))
        i.start()
    elif len(args) == 2:
        IRC(Network(server=args[0],nick='SpaceBot',ident='spacebot',realname="SpaceBot",channels=[args[1]] )).start()

def command_irc_add(i,command,args):
    global networks

    args = args.split()
    n = {}
    n['name'] = args[0]
    n['server'] = args[1]
    n['port'] = args[2]
    n['nick'] = args[3]
    n['ident'] = 'spacebot'
    n['realname'] = 'SpaceBot'
    n['channels'] = []

    networks[args[0]] = n
    
    save_networks()
    i.reply("Added %s, at %s:%s."%(args[0],args[1],args[2]))

def command_irc_join(i,command,args):
    global networks

    args = args.split()
    network = args[0]
    if not network in IRC.connected: return
    channels = args[1:]
    for c in channels:
        IRC.connected[network].join(c)
        networks[network]['channels'].append(c)
    save_networks()

def command_irc_say(i,command,args):
    global networks
    
    args = args.split(" ",2)
    network = args[0]
    channel = args[1]
    message = args[2]
    if not network in IRC.connected: return
    IRC.connected[network].msg(channel,message)

def save_networks():
    global networks
    json.dump(networks,open("data/irc.txt",'w'))



def init():
    global networks
    networks = {}
    try:
        f = open("data/irc.txt")
    except IOError:
        f = open("data/irc.txt","w")
        f.write("{}")
        f.close()
        f = open("data/irc.txt")

    networks = json.load(f)
    command_irc(None,None,"")

    command.ComHook('irc',command_irc, name='IRCBot')
    command.ComHook('irc_add',command_irc_add, name='IRCBot')
    command.ComHook('irc_join',command_irc_join, name='IRCBot')
    command.ComHook('irc_say',command_irc_say)
