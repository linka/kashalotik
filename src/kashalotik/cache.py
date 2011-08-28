# -*- coding: utf-8 -*-

from google.appengine.ext import db
from werkzeug.contrib.cache import GAEMemcachedCache
from utils import try_nested
import models

DATA_STRUCT = {'films': {'model': models.FilmModel,
                         'order': 'title',
                         'refprops': [{'name': 'files',
                                     'datakey': 'files', 
                                     'refkey': 'film'},
                                     {'name': 'works',
                                     'datakey': 'works', 
                                     'refkey': 'film'}]},
               'files': {'model': models.FileModel,
                         'order': 'name'},
               'works': {'model': models.WorkModel,
                         'order': 'title'},
               'labels': {'model': models.LabelModel,
                          'order': 'name'},
               'studios': {'model': models.StudioModel,
                          'order': 'name',
                          'props': [{'name': 'films',
                                    'datakey': 'films',
                                    'refkey': 'studio',
                                    'refsubkey': 'name'}]},
               'authors': {'model': models.AuthorModel,
                           'order': 'sndname',
                           'refprops': [{'name': 'works',
                                      'datakey': 'works',
                                      'refkey': 'author'}]},
               'chars': {'model': models.CharModel,
                           'order': 'name',
                           'refprops': [{'name': 'pics',
                                      'datakey': 'charpics',
                                      'refkey': 'char'}]}
               }

# create cache
cache = GAEMemcachedCache()

def get_data(datakey, attr=None, value=None):
    '''Gets the data by the given datakey. If cache is empty, 
    fills it from database.'''
    data = cache.get(datakey)
    ds = DATA_STRUCT[datakey]
    if data is None:
        data = [m.to_dict() for m in ds['model'].all().order(ds['order'])]
        cache.set(datakey, data)
    
    if attr and value:
        data = [x for x in data if try_nested(x[attr], value)]
    return data

def get_data_item(datakey, attr, value):
    '''Gets data item by given attr/value pair from the collection, 
    identified by datakey.'''
    data = cache.get(datakey)
    ds = DATA_STRUCT[datakey]
    item = None
    if data is None:
        tmp = ds['model'].gql('WHERE %s = :1' % attr, value).get()
        item = tmp and tmp.to_dict()
    else:
        for e in data:
            if e[attr] == value:
                item = e

    #get reference properties
    if ds.get('refprops'):
        for prop in ds['refprops']:
            if item and not getattr(item, prop['name'], None):
                dbitem = db.get(item['key'])
                item[prop['name']] = [p.to_dict() for p in getattr(dbitem, prop['name'])]

    #get properties defined by @property tag
    if ds.get('props'):
        for prop in ds['props']:
            if item and not getattr(item, prop['name'], None):
                if DATA_STRUCT[prop['datakey']]:
                    pk = prop.get('refsubkey')
                    val = pk and (pk, item[pk]) or item[pk]
                        
                    item[prop['name']] = get_data(prop['datakey'],
                                                  prop['refkey'],
                                                  val)
                else:    
                    dbitem = db.get(item['key'])
                    item[prop['name']] = [p.to_dict() for p in getattr(dbitem, prop['name'])]

    return item

def sample_data(datakey, attr):
    '''Gets the sample of the data possible attribute values. Then data is 
    stored in cache under the complex name 'datakey-attr'.'''
    sample_datakey = '%s-%s' % (datakey, attr)
    
    def makesample():
        'Creates sample by given attribute.'
        sd = {}
        data = get_data(datakey)
        
        for x in data:
            if x[attr]:
                sd[x[attr]] = x
        
        tmp = sorted(sd.keys())
        cache.set(sample_datakey, tmp)
        return tmp
    
    sample = cache.get(sample_datakey)
    if sample is None:
        sample = makesample()
    
    return sample
    