
import re
from BeautifulSoup import BeautifulStoneSoup

# Courtasy of Katharine :3

def escapeurl(url,plus=False):
    safe = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-'
    output = ''
    for char in url:
        if char in safe:
            output += char
        elif char==' ' and plus==True:
            output += '+'
        else:
            code = hex(ord(char))[2:]
            while len(code) > 0:
                if len(code) == 1:
                    code = '0' + code
                output += '%' + code[0:2]
                code = code[2:]
    return output

def FormatHTML(data):
    data=unicode(BeautifulStoneSoup(data,convertEntities=BeautifulStoneSoup.HTML_ENTITIES ))
    data = re.compile(r'<br.*?>').sub('\n',data)
    data = re.compile(r'<.*?>').sub('', data)
    return data
