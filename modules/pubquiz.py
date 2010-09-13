
import urllib2
import command
import random
import os

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

class Question:
    def __init__(self,text,answer,choices=None,type="",comment="",commas=False,correctnum=0):
        self.text=text
        self.answer=answer
        self.choices=choices
        self.type=type
        self.comment=comment
        self.commas = commas
        self.correctnum = correctnum

    def __str__(self):
        s = self.text
        if self.type=='multi':
            s+="\n"
            if not self.commas:
                s+= "\n".join(["- "+x for x in self.choices])
            else:
                s+=", ".join(self.choices)
        return s

    def check_answer(self,ans):

                
        if self.type=='multi':
            if len(ans)==1:
                try:
                    x = int(ans)
                except ValueError:
                    pass
                else:
                    if x == self.correctnum:
                        return True
                    else:
                        return False
            check = ans.strip().lower()
            if check!=self.answer:
                correct = False
                ambig = 0
                for x in self.choices:
                    if check in x.strip().lower():
                        ambig+=1
                        if x == self.answer:
                            correct = True
            else:
                return True

            if ambig==0: return -2
            if ambig>1: return -1
            if correct == True: return 1
            return 0
        else:
            if ans.strip().lower()==self.answer.strip().lower():
                return 1
            else:
                return 0

def command_pubquiz(i,command,args):
    """!randomtopic - Sets a random conversation topic. Can only be used once every 20 seconds."""
    global current_question
    global categories
    global current_category
    global current_category_type
    
    if current_question:
        if args:
            try:
                a = current_question.check_answer(args)
            except:
                i.reply("Error. Abandoning question.")
                current_question = None
                return
            if a==1:
                i.reply("Correct! "+current_question.comment)
                current_question=None
            elif a==0:
                i.reply("Incorrect.")
            elif a==-1:
                i.reply("Ambiguous answer.")
            elif a==-2:
                i.reply("Not an option.")
                
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
                n = PubQuiz('data/pubquiz/'+i+'/'+q)
                categories['all'][q.lower()[:-4]] = n
                categories[i.lower()][q.lower()[:-4]] = n
    current_category='all'