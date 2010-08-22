
import dynamic_core
import urllib2
import json
from libs.stringsafety import *

def get_google_data(phrase):
    if phrase.strip=="":
        return {'url':'No search phrase entered.','content':'No search phrase entered.','success':False}

    url = "http://ajax.googleapis.com/ajax/services/search/web?v=1.0&gl=uk&q="+escapeurl(phrase,plus=True)
    request = urllib2.Request(url,None,{'Referer':'http://spacerat.meteornet.net'})
    response = urllib2.urlopen(request)
    results = json.load(response)
    if results["responseData"]["results"]:
        for result in results["responseData"]["results"]:
            if 'youtube' in result["url"]: continue
            result['success'] = True
            return result
    else:
        return {'url':'No result.','content':'No result.','success':False}

def tag_google(node,context):
    """[google phrase] Fetches google data for a phrase. Sets the value of variables g_succes, g_url and g_content."""
    data = get_google_data(dynamic_core.get_var(node.attribute,context))
    for x in data.keys():
        context.vars["g_%s"%x] = data[x]

def init():
    dynamic_core.register_tag('google',tag_google)