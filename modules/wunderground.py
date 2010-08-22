
from xml.dom import minidom
from libs.stringsafety import *
import urllib2
import command
import dynamic_core
from BeautifulSoup import BeautifulSoup

def get_wunderground_text(location):
    url=r'http://api.wunderground.com/auto/wui/geo/ForecastXML/index.xml?query='+escapeurl(location)
    request = urllib2.Request(url,None,{'Referer':'http://spacerat.meteornet.net'})
    response = urllib2.urlopen(request)

    data = minidom.parse(response)
    d = {}

    
    try:
        d = data.getElementsByTagName("txt_forecast")[0].getElementsByTagName("fcttext")[0].firstChild.data
        return d
    except IndexError:
        return "No data for %s"%location

    return d

def get_wunderground_data(location):

    url = r'http://mobile.wunderground.com/cgi-bin/findweather/getForecast?brand=mobile&query='+escapeurl(location)
    request = urllib2.Request(url,None,{'Referer':'http://spacerat.meteornet.net'})
    response = urllib2.urlopen(request)
    doc = BeautifulSoup(response)
    data = {}
    if doc.b.string=='Search not found:':
        data['weather_success']=False
        data['weather_info']="Search failed"
        return data
    if doc.findAll(text='Place: Temperature'):
        data['weather_success']=False
        data['weather_info']="Please be more specific"
        return data
    tags = doc.findAll(name='td')
    data['weather_success']=True
    data['weather_info']=doc.findAll('b')[1].string
    for x in tags:
        if x.string=='Humidity':
            data['humidity'] = int(x.parent.b.string[:-1])
        elif x.string=='Temperature':
            f = x.parent.findAll('b')
            data['celcius'] = float(f[1].string)
            data['farenheight'] = float(f[0].string)
        elif x.string=="Conditions":
            data['conditions']=x.parent.b.string

    return data

def tag_weather_text(node,context):
    """[weather_text location] - Get a nice description of the weather in a location."""
    return get_wunderground_text(dynamic_core.get_var(node.attribute,context))

def tag_weather_data(node,context):
    """[weather_data location] - Get data for the weather at a location. Returns nothing, but sets the values of [weather_success], [weather_info] and possibly [humidity], [celcius], [farenheight], and [conditions]."""
    data = get_wunderground_data(dynamic_core.get_var(node.attribute,context))
    for x in data:
        if not x in context.vars:
            context.vars[x]=data[x]

def init():
    dynamic_core.register_tag('weather_text',tag_weather_text)
    dynamic_core.register_tag('weather_data',tag_weather_data)