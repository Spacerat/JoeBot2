
from libs import wap

import urllib2, urllib
import command
import json

appid = 'GW5TWH-TG4VQ84K64'

server = 'http://api.wolframalpha.com/v1/query.jsp'



            


def command_wolfram(i,command,args):
    """~wolfram input: query Wolfram Alpha."""
    input = urllib.quote(args)
    waeo = wap.WolframAlphaEngine(appid, server)
    query = waeo.CreateQuery(input)
    result = waeo.PerformQuery(query)
    waeqr = wap.WolframAlphaQueryResult(result)
    reply = "\n"
    if waeqr.IsSuccess()[0] == 'false':
        jsonr = waeqr.JsonResult()
        for x in json.loads(jsonr):
            if x[0] == 'tips':
                i.reply("Request failed. "+x[2][1][1]);
                return
    print waeqr.JsonResult()
    for pod in waeqr.Pods():
        p = wap.Pod(pod)
        subpods = p.Subpods()
        for subpod in subpods:
            sp = wap.Subpod(subpod)
            if sp.Plaintext()[0]:
                reply += p.Title()[0] +": "+sp.Plaintext()[0] + "\n"
    i.reply(reply)

def init():
    command.ComHook("wolfram",command_wolfram,"WolframBot")
