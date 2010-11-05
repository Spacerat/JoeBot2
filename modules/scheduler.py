
import modules
import command
from libs import data
import getopt
from datetime import datetime, timedelta
import dynamic_core
from sqlite3 import IntegrityError
import threading

class SchedulerException(Exception): pass
class InvalidRecurException(SchedulerException): pass

def AdvSplit(s):
    split = s.split()
    result = []
    inquote=False
    i=-1
    for x in split:
        if inquote == False:
            result.append(x)
            i+=1
        else:
            result[i] = result[i] + " " + x
        if x.count('"')%2 != 0:
            if inquote == False:
                inquote = True
            else:
                inquote = False

    return result

def increment_datetime(dt,recur):
    if recur == 'year':
        dt = dt.replace(year=dt.year+1)
    elif recur == 'week':
        dt+=timedelta(weeks=1)
    elif recur=='month':
        if dt.month==12:
            dt = dt.replace(year=dt.year+1,month=0)
        else:
            dt = dt.replace(month=dt.month+1)
    elif recur=='hour':
        dt+=timedelta(hours=1)
    elif recur=='day' or recur=='':
        dt+=timedelta(days=1)
    else:
        raise InvalidRecurException, "Invalid value %s for recurrence."%recur
    return dt

def do_event(interfacename,eventname,dt):
    d = data.query('SELECT text, recurrence, datetime FROM schedule WHERE interface = ? AND name = ?',(interfacename,eventname))[0]
    dt = datetime.strptime(d[2],'%Y-%m-%d %H:%M:%S')
    rec = d[1]
    if rec=='':
        data.query('DELETE FROM schedule WHERE interface = ? and name = ?',(interfacename,eventname))
    else:
        dt = increment_datetime(dt,rec)
        data.query('UPDATE schedule SET datetime = ? WHERE interface = ? and name = ?',(dt.isoformat(' '),interfacename,eventname))
    
    try:
        i = modules.Interface.interfaces[interfacename]
    except:
        print "Alarm triggered for non-existing interface %s."%interfacename
        return

    context = dynamic_core.TagContext(i=i,args=d[2])
    message = dynamic_core.parse_markup(d[0]).process(context)
    i.reply("AlarmBot: "+message)
def queue_event(interfacename,eventname,dt):
    delta = (dt-datetime.now())
    secs = delta.seconds + delta.days*86400
    threading.Timer(secs,do_event,[interfacename,eventname,dt]).start()

def add_event(dt,message,recur,eventname, username, interfacename):

    now = datetime.now().replace(microsecond=0)
    dt = dt.replace(microsecond=0)
    while dt < now:
        dt = increment_datetime(dt,recur)

    nowstr = now.isoformat(' ')
    datestr = dt.isoformat(' ')

    data.query('INSERT INTO schedule VALUES (?,?,?,?,?,?,?)',(interfacename,eventname,nowstr,username,message,datestr,recur))
    queue_event(interfacename,eventname,dt)

def command_schedule(i,command,args):
    l = AdvSplit(args)

    fail = lambda x: x.reply("Incorrect usage. Use %sschedule [-r year/week/month/day/hour] [-d dd/mm/yyyy] event_name MM:HH \"Message\""%x.prefix)

    try:
        optlist, args = getopt.getopt(l,'r:d:')
    except getopt.GetoptError, err:
        interface.reply(str(err))
        fail(i)
        return
    if len(args)!=3:
        i.reply("Wrong number of arguments.")
        fail(i)
        return
    recur = ''
    datestr = ''
    for o, a in optlist:
        if o=='-r': recur = a
        if o=='-d': datestr = a
    name =args[0]
    timestr=args[1]
    message=args[2]
    if message[0]=='"' and message[-1]=='"': message = message[1:-1]
    
    if datestr!="":
        try:
            sdate = datetime.strptime(datestr,"%d/%m/%Y")
        except ValueError, err:
            interface.reply(str(err))
    else:
        sdate = datetime.today()
    try:
        stime = datetime.strptime(timestr,"%H:%M")
    except Exception as e:
        i.reply(e)
    sdatetime = datetime(sdate.year,sdate.month,sdate.day,stime.hour,stime.minute)

    try:
        add_event(sdatetime, message,recur,name, i.user_name,i.interface_name)
    except SchedulerException as e:
        i.reply(e)
    except IntegrityError as e:
        i.reply("An alarm named %s has already been created in this chatroom."%name)
    else:
        i.reply("Event %s added!"%name)

def command_unschedule(i,command,args):
    
    try:
        data.query("DELETE FROM schedule WHERE interface = ? AND name = ?", (i.interface_name,args))
    except Exception as e:
        i.reply(e)
    else:
        i.reply("Event deleted.")

def load_events():
    d = data.query('SELECT interface, name, datetime FROM schedule')
    for e in d:
        dt = datetime.strptime(e[2],'%Y-%m-%d %H:%M:%S')
        if dt < datetime.now(): dt = datetime.now()
        queue_event(e[0],e[1],dt)

def init():
    data.query('''CREATE TABLE IF NOT EXISTS schedule
    (interface TEXT, name TEXT, datetime_added TEXT, user TEXT, text TEXT, datetime DATETIME,  recurrence TEXT,
    PRIMARY KEY (interface, name))''')

    command.ComHook('schedule',command_schedule,name='AlarmBot')
    command.ComHook('unschedule',command_unschedule,name='AlarmBot')
    load_events()
