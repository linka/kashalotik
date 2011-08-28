# -*- coding: utf-8 -*-
import gdata.docs.data
import gdata.docs.client
import gdata.spreadsheet.service
import getpass
from pprint import pprint
import re

def out(s):
    print s.encode('utf-8')

def getfeed(feed, k):
    result = dict()
    for i, entry in enumerate(feed.entry):
        row = dict()
        for key in entry.custom:
            row[key] = entry.custom[key].text
        name = row.pop(k)
        result[name] = row
    return result

def getpeople(films):
    result = dict()
    for key in films.keys():
        people = films[key]['participants']
        pl = re.findall('(.+) \((.+)\)', people, re.M)
        for item in pl:
            result[item[0]] = 0
    return result

client = gdata.spreadsheet.service.SpreadsheetsService(source='kashalotik-db-v1')
client.ssl = True
client.http_client.debug = False

p = getpass.getpass('Pass: ')
client.ClientLogin('alexey.suslov@gmail.com', p, client.source)

people = getfeed(client.GetListFeed('tYmeGmMmYNh1mqb2hvL5rzg', 'od6'), 'name')
films = getfeed(client.GetListFeed('toSpN9FJOoOIpKLqOigatnw', 'od6'), 'id')

data = getpeople(films)

for key in data.keys():
    print key.encode('utf-8')
    
print len(data)

