
import modules

class ConsoleInterface(modules.Interface):

    def __init__(self):
        self.name="Console"
        self.prefix="!"
        self.user_name="Console"
        self.user_address="Console"
        self.type="Console"
        self.chat_name="Console"
        self.bot_nick="Console"
        self.bot_handle="Console"
        self.users={self.bot_nick:self.bot_handle}

    def reply(self, text,edit=False):
        outp = text
        if not text: return
        if self.name<>"": outp=self.name+": "+outp
        #outp = unicode(outp,errors='ignore')
        print outp.encode('ascii','ignore')
