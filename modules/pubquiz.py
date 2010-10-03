
import urllib2
import command
import random
import os
from libs import data

categories={}
current_question=None
current_category=None
current_category_type='super'

class QuizParseError(Exception): pass

class PubQuestionTemplate:
    def __init__(self,flags,question,comment):
        self.commas = False
        for flag in flags.split(","):
            if flag[0]=='m':
                self.type = 'multi'
                self.choices = int(flag[1])
            elif flag[0]=='s':
                self.type = 'single'
                self.choices = 1
            elif flag[0]=='a':
                self.column = int(flag[1])
            elif flag=='commas':
                self.commas = True
        self.question = question
        self.comment = comment


class PubQuiz:
    def __init__(self,filename):
        f = open(filename)
        nlnum=0
        readdata=False
        self.data=[]
        self.questions = []
        line = f.readline()
        while line:
            if line=="\n":
                nextline=f.readline()
                if nextline=="\n":
                    for l in f.readlines():
                        d = l[:-1].split("\t")
                        for i, v in enumerate(d):
                            d[i] = v.strip()
                        self.data.append(d)

                else:
                    flags=nextline[:-1]
                    question = f.readline()[:-1]
                    comment = f.readline()[:-1]
                    self.questions.append(PubQuestionTemplate(flags,question,comment))
            line = f.readline()
        if len(self.data)==0 or len(self.questions)==0:
            raise QuizParseError, filename


    def get_question(self):
        q = random.choice(self.questions)
        answer = random.choice(self.data)
        text = q.question
        comment = q.comment
        for n,d in enumerate(answer):
            text = text.replace('{'+str(n)+'}',d)
            comment = comment.replace('{'+str(n)+'}',d)
            try:
                i = int(d)
            except ValueError:
                comment = comment.replace('|'+str(n)+'|',d.capitalize())
                text = text.replace('|'+str(n)+'|',d.capitalize())
            else:
                if len(d)>1 and int(d[-2:])<20 and int(d[-2:])>9:
                    d=d+"th"
                elif d[-1]=="1":
                    d=d+"st"
                elif d[-1]=="2":
                    d=d+"nd"
                elif d[-1]=="3":
                    d=d+"rd"
                else:
                    d=d+"th"
                comment = comment.replace('|'+str(n)+'|',d)
                text = text.replace('|'+str(n)+'|',d)

        answerstr = answer[q.column]
        choices=[]
        num = 0
        if q.type=='multi':
            for i in range(q.choices):
                c = answer[q.column]
                while c in choices:
                    c = random.choice(self.data)[q.column]
                choices.append(c)
            random.shuffle(choices)
            for i,v in enumerate(choices):
                if v == answerstr: num = i+1
        question = Question(text,answerstr,choices,q.type,comment,q.commas, num)
        return question

def AddUserIfNotExists(user):
    data.query("INSERT OR IGNORE INTO pubquiz_stats (handle) VALUES (?)", (user,))

class Question:
    def __init__(self,text,answer,choices=None,type="",comment="",commas=False,correctnum=0):
        self.text=text
        self.answer=answer
        self.choices=choices
        self.type=type
        self.comment=comment
        self.commas = commas
        self.correctnum = correctnum
        self.attempted = []
        self.attemptors = {}

    def __str__(self):
        s = self.text
        if self.type=='multi':
            s+="\n"
            if not self.commas:
                s+= "\n".join(["- "+x for x in self.choices])
            else:
                s+=", ".join(self.choices)
        return s

    def check_answer(self,ans,user):
        AddUserIfNotExists(user)
        self.attemptors[user] = True

        if self.type=='multi':
            if len(ans)==1:
                try:
                    x = int(ans)
                except ValueError:
                    pass
                else:
                    if x == self.correctnum:
                        self.attempted.append(x)
                        return True
                    else:
                        if not x in self.attempted:
                            self.attempted.append(x)
                            return 0
                        else:
                            return -3

            check = ans.strip().lower()
            tried = 0
            if check!=self.answer:
                correct = False
                ambig = 0
                for n, x in enumerate(self.choices):
                    if check in x.strip().lower():
                        tried = n+1
                        ambig+=1
                        if x == self.answer:
                            correct = True
            else:
                self.attempted.append(check)
                return True

            if ambig==0: return -2
            if ambig>1: return -1
            if correct == True:
                self.attempted.append(tried)
                return 1
            if not tried in self.attempted:
                self.attempted.append(tried)
                return 0
            else:
                return -3
        else:
            a = ans.strip().lower()
            if a in self.attempted:
                return -3
            elif a == self.answer.strip().lower():
                self.attempted.append(a)
                return 1
            else:
                self.attempted.append(a)
                return 0

def command_pubquiz(i,command,args):
    """!randomtopic - Sets a random conversation topic. Can only be used once every 20 seconds."""
    global current_question
    global categories
    global current_category
    global current_category_type
    
    if current_question:
        if args:
            pq = current_question
            try:
                a = current_question.check_answer(args,i.user_address)
            except UnicodeError:
                i.reply("Unicode Error. Abandoning question.")
                current_question = None
                return
            if a==1:
                if current_question.type=='multi':
                    points = len(current_question.choices)-len(current_question.attempted)
                else:
                    points=3

                data.query("UPDATE pubquiz_stats SET attempts=attempts+1,score=score+?,correct=correct+1 WHERE handle=?",(points,i.user_address))
                stats = data.query("SELECT * FROM pubquiz_stats WHERE handle=?",(i.user_address,))[0]

                i.reply("Correct, +%d points! %s"%(points,current_question.comment))
                c = float(stats[1])
                a = float(stats[2])
                p = (c/a)*100
                i.reply("%s now has %d points and %d%% correct attempts."%(i.user_name,stats[3],p))
                

                current_question=None
            elif a==0:
                i.reply("Incorrect.")
                data.query("UPDATE pubquiz_stats SET attempts=attempts+1 WHERE handle=?",(i.user_address,))
            elif a==-1:
                i.reply("Ambiguous answer.")
            elif a==-2:
                i.reply("Not an option.")
            elif a==-3:
                i.reply("Someone already tried that!")


            if current_question:
                if (len(current_question.attempted) == len(current_question.choices)-1) and current_question.type=="multi":
                    i.reply("You all fail! "+current_question.comment)
                    current_question=None

            if not current_question:
                for u in pq.attemptors.keys():
                    data.query("UPDATE pubquiz_stats SET questions=questions+1 WHERE handle=?",(u,))


                
        else:
            i.reply(str(current_question))
    else:
        if args:
            args = args.strip().lower()

            if args in categories:
                current_category = args
                i.reply("Category is now %s." % args)
                current_category_type='super'
                current_question = random.choice(categories[args].values()).get_question()
            elif args in categories['all']:
                i.reply("Category is now %s." % args)
                current_category = args
                current_category_type='sub'
                current_question = categories['all'][args].get_question()
            else:
                i.reply("No category found for "+args+".")
                return
        else:
            if current_category_type=='sub':
                current_question = categories['all'][current_category].get_question()
            elif current_category_type=='super':
                current_question = random.choice(categories[current_category].values()).get_question()
        i.reply(str(current_question))

def command_listquizzes(i,command,args):
    global categories
    rep="\n"
    for c in categories:
        if c!='all':
            rep+="-"+c+"\n"+", ".join(categories[c])+"\n"
    i.reply(rep)
    
def init():
    global categories
    global current_category
    categories = {}
    
    command.ComHook('quiz',command_pubquiz,name="Quiz")
    command.ComHook('listquizzes',command_listquizzes,name="Quiz")
    categories['all'] = {}
    for i in os.listdir('data/pubquiz'):
        if i[-4:]!=".txt":
            if not i.lower() in categories: categories[i.lower()] = {}
            for q in os.listdir('data/pubquiz/'+i):
                if q[-4:]==".txt":
                    n = PubQuiz('data/pubquiz/'+i+'/'+q)
                    categories['all'][q.lower()[:-4]] = n
                    categories[i.lower()][q.lower()[:-4]] = n
    current_category='all'

    data.query('''CREATE TABLE IF NOT EXISTS pubquiz_stats
    (handle TEXT NOT NULL , correct INTEGER DEFAULT 0, attempts INTEGER DEFAULT 0, score INTEGER DEFAULT 0, questions INTEGER DEFAULT 0, record_time INTEGER DEFAULT 0,
    PRIMARY KEY (handle))''')
