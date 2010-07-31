import command

def command_echo(interface,hook,args):
    interface.reply(args)

command.ComHook('echo',command_echo)