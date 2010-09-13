
import dynamic_core
from BeautifulSoup import BeautifulSoup
from libs import stringsafety
import urllib2

def parseargs(args,context):
    args+=" "
    ret={}
    attrib=''
    is_attrib=True
    word=''
    in_quote=0
    quoted=False
    for char in args:
        if char=='"':
            if in_quote==0:
                in_quote=2
                quoted=True
            elif in_quote==2:
                in_quote = 0
            else:
                word+=char
        elif char=="'":
            if in_quote==0:
                in_quote = 1
                quoted=True
            elif in_quote==1:
                in_quote = 0
            else:
                word+=char
        elif char=="=":
            if in_quote==0:
                if is_attrib:
                    
                    attrib = word
                    is_attrib=False
                    word=''
                else:
                    word+=char
            else:
                word+=char
        elif char==" ":
            if in_quote==0:
                if quoted==False:
                    ret[attrib]=dynamic_core.get_var(word,context)
                else:
                    ret[attrib]=word
                is_attrib=True
                quoted=False
                word=''
            else:
                word+=char
        else:
            word+=char

    return ret

def tag_format_html(node,context):
    """[html] - Formats HTML for display in skype."""
    s=''
    if node.type=='tag':
        s = stringsafety.FormatHTML(dynamic_core.get_var(node.attribute,context))
    elif node.type=='cont':
        s= stringsafety.FormatHTML(node.process_children(context))

    if len(s)>550:
        return s[0:447]+"..."
    else:
        return s

def tag_urlsafe(node,context):
    """<urlsafe>string</urlsafe> - Format a string for inclusion in a URL."""
    return stringsafety.escapeurl(node.process_children(context))

def dosoup(page,node,context,sibling=False):

    if (sibling):
        doc = page
    else:
        doc = BeautifulSoup(page)

    soupargs = {}
    args = node.attribute.partition(" ")[2]
    n=0
    if (args):
        soupargs = parseargs(args,context)
        for k in soupargs:
            soupargs[k] = dynamic_core.get_var(soupargs[k],context)
        if 'n' in soupargs.keys():
            n=int(soupargs.get('n',0))
            del soupargs['n']
    name = node.attribute.partition(" ")[0]
    if sibling == False:
        if n==0:
            return doc.find(name,soupargs)
        else:
            
            return doc.findAll(name,soupargs)[n]
    else:
        return doc.findNextSiblings(name,soupargs)[n]


def tag_soupurl(node,context):
    """<soup name attribute=value attribute=value...>url</soup> - Fetch a web page from the internet, and return the contents of the first tag with the name and attributes given."""
    url = node.process_children(context)
    if not url.startswith("http://"): url="http://"+url
    response = urllib2.urlopen(url)

    return dosoup(response,node,context)

def tag_soupstring(node,context):
    """<soupstring name attribute=value attribute=value...>string</soup> - Return the contents of the first tag with the name and attributes given, found in the given string."""
    return dosoup(node.process_children(context),node,context)

def tag_soupsibling(node,context):
    return dosoup(node.children[0].process(context),node,context,sibling=True)
def init():
    dynamic_core.register_tag('html',tag_format_html)
    dynamic_core.register_tag('soup',tag_soupurl)
    dynamic_core.register_tag('soupsibling',tag_soupsibling)
    dynamic_core.register_tag('soupstring',tag_soupstring)
    dynamic_core.register_tag('urlsafe',tag_urlsafe)
