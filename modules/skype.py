
import modules
import command
import Skype4Py
from libs import logging

class SkypeInterface(modules.Interface):

    def __init__(self, Message, MessageStatus, Skype):
        self.message = Message
        self.message_status = MessageStatus
        self.skype = Skype
        self.bot_handle = Skype.CurrentUser.Handle
        self.prefix="!"
        self.name=''
        self.type="Skype"

    def _sanitisetext(self,text):
        outp=text
        if not isinstance(text,unicode):
            try:
                outp = unicode(text,errors='ignore')
            except:
                outp = str(text)
        if self.name<>"": outp=unicode(self.name)+": "+outp
        return outp

    def reply(self, text,edit=False):
        outp=self._sanitisetext(text)

        if edit and self.message.IsEditable:
            self.message.Body=outp
        else:
            self.message.Chat.SendMessage(outp)

    def reply_to_sender(self,text):
        if self.message_status=="SENT":
            self.reply(text)
            return
        outp=self._sanitisetext(text)

        self.skype.send_message(self.user_address,outp)


    def set_topic(self,topic):
        try:
            self.message.Chat.Topic=topic
        except:
            pass

    @property
    def is_editable(self):
        return self.message.IsEditable

    @property
    def last_messages(self):
        messages = self.message.Chat.RecentMessages
        ret = []
        try:
            for x in range(0,20):
                ret.append(messages[len(messages)-2-x])
        except IndexError:
            pass

        return ret
    @property
    def user_address(self):
        return self.message.FromHandle

    @property
    def user_name(self):
        return self.message.FromDisplayName

    @property
    def users(self):
        r = {}
        for u in self.message.Chat.Members:
            if u.FullName.strip()=='': continue
            r[u.FullName]= u.Handle

        return r

    @property
    def chat_name(self):
        return self.message.ChatName

skype = Skype4Py.Skype()

# ----------------------------------------------------------------------------------------------------
# Fired on attachment status change. Here used to re-attach this script to Skype in case attachment is lost. Just in case.
def OnAttach(status):
    logging.info('API attachment status: ' + skype.Convert.AttachmentStatusToText(status))
    if status == Skype4Py.apiAttachAvailable:
        skype.Attach();

    if status == Skype4Py.apiAttachSuccess:
       logging.info('Connected to skype!')

# ----------------------------------------------------------------------------------------------------
# Fired on chat message status change.
# Statuses can be: 'UNKNOWN' 'SENDING' 'SENT' 'RECEIVED' 'READ'

def OnMessageStatus(Message, Status):
    if Status=='SENT' or Status=='RECEIVED':
        modules.call_hook('message',Message.Body,interface=SkypeInterface(Message,Status,skype))

def start():

    skype.OnAttachmentStatus = OnAttach;
    skype.OnMessageStatus = OnMessageStatus;

    logging.info('Connecting to Skype')
    skype.Attach()

def command_skype(interface,hook,args):
    """~skype - Starts the skype client."""
    start()

def init():
    start()

command.ComHook('skype',command_skype,name="EchoBot",security=4)