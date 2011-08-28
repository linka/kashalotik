# -*- coding: utf-8 -*-
from datetime import date

from google.appengine.ext import db

import utils

WORK_TITLES = [u'автор', u'сценарист', u'переводчик', u'художник', u'редактор',
u'художественный редактор', u'руководитель', u'кукловод', u'художник-оформитель',
u'художник-постановщик', u'оператор', u'составитель', u'актер']

def to_dict(model):
    simpletypes = (int, long, float, bool, dict, basestring, list, date)
    out = {}
    
    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, simpletypes):
            out[key] = value
        elif isinstance(value, db.Model):
            out[key] = value.to_dict()
        else:
            raise ValueError('cannot encode ' + repr(prop))
    
    out['key'] = str(model.key())
    return out

class FilmModel(db.Model):
    id = db.StringProperty(required = True)
    title = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    info = db.TextProperty(required = True)
    year = db.StringProperty(required = True)
    studio = db.StringProperty(required = True)
    language = db.StringProperty(required = True)
    labels = db.StringListProperty()
    added = db.DateProperty()

    authors = db.StringListProperty()
    artists = db.StringListProperty()
    chars = db.StringListProperty()

    @classmethod
    def gen_unique_url(self, title):
        unique = utils.urlify(title)
        film = FilmModel.gql("WHERE url = :1", unique).get()
        if film:
            unique = '%s-%s' % (film.url, film.year)
        return unique
    
    def to_dict(self):
        film = to_dict(self)
        film['id'] = int(film['id'])
        film['info'] = utils.htmlify(film['info'])
        film['year'] = film['year'] != '-1' and film['year'] or ''
        film['studio'] = {'name': film['studio'], 
                          'url': utils.urlify(film['studio'])}
        film['labels'] = [utils.anchor(x) for x in film['labels']]
        film['authors'] = [utils.anchor(x) for x in film['authors']]
        film['artists'] = [utils.anchor(x) for x in film['artists']]
        return film
        

class StudioModel(db.Model):
    name = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    info = db.TextProperty(required = True)
    logo = db.StringProperty(required = True)

    @property
    def films(self):
        return FilmModel.gql("WHERE studio = :1", self.name)
    
    def to_dict(self):
        return to_dict(self)

class FileModel(db.Model):
    film = db.ReferenceProperty(FilmModel, collection_name='files')
    name = db.StringProperty(required = True)
    type = db.StringProperty(required = True)

    def to_dict(self):
        return to_dict(self)
    
class SourceModel(db.Model):
    film = db.ReferenceProperty(FilmModel, collection_name='source')
    name = db.StringProperty(required = True)
    info = db.StringProperty(multiline = True)
    
    def to_dict(self):
        return to_dict(self)

class AuthorModel(db.Model):
    name = db.StringProperty(required = True)
    fstname = db.StringProperty(required = True)
    sndname = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    info = db.TextProperty()
    worktitles = db.StringListProperty()
    workscount = db.IntegerProperty()
    
    @property
    def works(self):
        a = WorkModel.gql("WHERE author = :1", self.key())
        return a

    @classmethod
    def get_or_insert(self, name):
        author = AuthorModel.gql("WHERE name = :1", name).get()
        if not author:
            names = name.split('.')
            fstname = '%s.' % '.'.join(names[:-1])
            author = AuthorModel(name = name, fstname = fstname.strip(), 
                                    sndname = names[-1].strip(), url = utils.urlify(name),
                                    info = '').put()
        return author

    def to_dict(self):
        return to_dict(self)

class CharModel(db.Model):
    name = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    info = db.TextProperty()

    @classmethod
    def get_or_insert(self, name):
        char = CharModel.gql("WHERE name = :1", name).get()
        if not char:
            char = CharModel(name = name, url = utils.urlify(name), info = '')
            char.put()
        return char

    def to_dict(self):
        return to_dict(self)

class CharPicModel(db.Model):
    char = db.ReferenceProperty(CharModel, collection_name='pics')
    link = db.StringProperty(required = True)

    def to_dict(self):
        return to_dict(self)

class LinkModel(db.Model):
    author = db.ReferenceProperty(AuthorModel, collection_name='links')
    name = db.StringProperty(required = True)
    link = db.LinkProperty(required = True)

    def to_dict(self):
        return to_dict(self)

class BioPicModel(db.Model):
    author = db.ReferenceProperty(AuthorModel, collection_name='pics')
    link = db.LinkProperty(required = True)
    origin = db.StringProperty(required = True)

    def to_dict(self):
        return to_dict(self)

class WorkModel(db.Model):
    film = db.ReferenceProperty(FilmModel, collection_name='works')
    author = db.ReferenceProperty(AuthorModel, collection_name='author')
    title = db.StringProperty(required = True, choices=WORK_TITLES)
    
    def to_dict(self):
        return to_dict(self)
    '''
    @classmethod
    def get_authors(self, film):
        r = WorkModel.gql("WHERE film = :1 AND title = :2", film, u'Автор').get()
        if r:
            return r.author.name
        else:
            return ''

    @classmethod
    def get_artists(self, film):
        r = WorkModel.gql("WHERE film = :1 AND title = :2", film, u'Художник').get()
        if r:
            return r.author.name
        else:
            return ''
    '''

class LabelModel(db.Model):
    name = db.StringProperty(required = True)
    url = db.StringProperty(required = True)
    
    @classmethod
    def get_or_insert(self, name):
        label = LabelModel.gql("WHERE name = :1", name).get()
        if not label:
            label = LabelModel(name = name, url = utils.urlify(name), info = '')
            label.put()
        return label
    
    def to_dict(self):
        return to_dict(self)

__all__ = (FilmModel, StudioModel, FileModel, SourceModel, AuthorModel, 
           LinkModel, WorkModel, CharModel, BioPicModel, CharPicModel)
