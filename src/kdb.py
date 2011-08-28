# -*- coding: utf-8 -*-
import yaml
import models
import utils
from google.appengine.ext import db
from datetime import datetime

def reset():
    for model in models.__all__:
        db.delete(model.all(keys_only=True))

def upload():
    def get_workers(people, title):
        result = [x['name'] for x in people if x['title'] == title]
        return result

    bio_data = yaml.load(open('authors.yaml', 'r').read())
    film_data = yaml.load(open('slides.yaml', 'r').read())
    studio_data = yaml.load(open('studios.yaml', 'r').read())
    char_data = yaml.load(open('chars.yaml', 'r').read())

    # studios
    for k in studio_data.keys():
        item = studio_data[k]
        studio = models.StudioModel(name = k, url = utils.urlify(k),
                                    info = item['info'], logo=item['logo']).put()

    # bio
    for k in bio_data.keys():
        item = bio_data[k]
        names = k.split('.')
        fstname = '%s.' % '.'.join(names[:-1])
        author = models.AuthorModel(name = k, fstname = fstname.strip(), 
                                    sndname = names[-1].strip(), url = utils.urlify(k),
                                    info = item['info']).put()
        for l in item['links']:
            models.LinkModel(author=author, name=l['name'], link=l['link']).put()
        for p in item['pics']:
            models.BioPicModel(author=author, link=p['link'], origin=p['origin']).put()

    # chars
    for k in char_data.keys():
        item = char_data[k]
        char = models.CharModel(name = k, url = utils.urlify(k),
                                    info = item['info']).put()
        for p in item['pics']:
            models.CharPicModel(char=char, link=p).put()

    # films
    for k in film_data.keys():
        item = film_data[k]
        url = models.FilmModel.gen_unique_url(item['title'])
        authors = get_workers(item['authors'], u'автор')
        artists = get_workers(item['authors'], u'художник')
        dt = datetime.strptime(item['added'], '%d-%m-%Y').date()
        film = models.FilmModel(id=k, title=item['title'], url=url,
            info=item['info'], year=item['year'], studio=item['studio'],
            language=item['language'], labels=item['labels'], 
            chars=item['chars'], authors=authors, artists=artists, added=dt)
        film.put()

        for f in item['files']:
            models.FileModel(film=film, name=f['name'], type=f['type']).put()
        for a in item['authors']:
            author = models.AuthorModel.get_or_insert(a['name'])
            models.WorkModel(film=film, author=author, title=a['title']).put()
        for c in item['chars']:
            char = models.CharModel.get_or_insert(c)
        for la in item['labels']:
            label = models.LabelModel.get_or_insert(la)
    
    # author work titles
    for author in models.AuthorModel.all():
        author.worktitles = list(set([x.title for x in author.works]))
        
        works = models.WorkModel.gql('WHERE author = :1', author.key())
        worksli = []
        for x in works:
            worksli.append(x.film.to_dict())
            
        author.workscount = len(utils.rem_dict_duplicates(worksli, 'id'))
        author.put() 