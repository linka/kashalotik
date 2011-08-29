# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import re

from copy import deepcopy
from datetime import datetime
from random import sample, choice
import yaml

from flask import Flask, request, redirect, url_for, \
     abort, render_template
from google.appengine.ext.webapp import util
from google.appengine.api import mail

from kashalotik import get_data, get_data_item, sample_data
from utils import urlify, get_valid_option, rem_dict_duplicates
from models import WORK_TITLES
import kdb


# configuration
SECRET_KEY = "development key"
DEBUG = True

# create and application
app = Flask(__name__)
app.config.from_object(__name__)

# constants
TEMPLATES_FOLDER = 'templates'
DEFAULT_VIEWMODE = 'grid'
VIEWMODES = ['grid', 'list']
MAILTO = 'lista.anta@gmail.com'

# Template constants for different UI blocks
TPL_ENTITY = {'sortbyyear': True,
              'comments': True,
              'infoblock': True}

# mapping labels on model properties
def label_name_func(value):
    return get_data_item('labels', 'url', value)['name']

def render(tpl, **values):
    if tpl is None:
        return abort(404)
    
    return render_template(tpl, **values)

# general functions
def baseurl():
    '''Returns the base url for Simple Viewer, which indicates the site 
    with films data.'''
    return "" if "localhost" in request.url_root else \
            "http://dl.dropbox.com/u/1463784/Kashalotik"

def backurl():
    urlroot = lambda x: '/'.join(x.split('/')[:-1])
    
    ref = request.referrer
    path = request.path
    pathroot = urlroot(path)
    
    if ref is None or path in ref or pathroot in urlroot(ref):
        ref = pathroot
    return ref

def viewmode():
    'Returns viewmode otherwise from request arguments or the default one.'
    mode = request.args.get('mode') or request.cookies.get('mode')
    return get_valid_option(mode, 
                            VIEWMODES, 
                            DEFAULT_VIEWMODE)

def get_entity(cachekey, entity_films, id, listtitle, titleparamkey=None):
    'Creates dictionary of template values for entity.'
    entity = get_data_item(cachekey, 'url', id)
    if not entity: abort(404)
    
    if titleparamkey:
        listtitle = listtitle % entity[titleparamkey]
    
    tmp = dict(entity=entity, films=entity_films(entity), listtitle=listtitle)
    tmp.update(TPL_ENTITY)
    return tmp

# 404 error handling
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

# template context processors
@app.context_processor
def inject_mailto():
    return dict(mailto=MAILTO)

@app.context_processor
def inject_base_values():
    return dict(labels=get_data('labels'),
                path=request.path,
                viewmode=viewmode(),
                backurl=backurl())

# route handlers
@app.route('/')
def main_page():
    return redirect(url_for('slides'))

@app.route('/diafilms/')
@app.route('/diafilms/<op>/')
def diafilms(op='view', value=None):
    return slides(op, value)

@app.route('/slides/')
@app.route('/slides/<op>/')
@app.route('/slides/<op>/<value>')
def slides(op='view', value=None):
    # media = ['read', 'download', 'view', 'listen']
    random_num = 10
    
    films = get_data('films')
    
    tdict = dict(sortbyyear=True)
    tpl = None
    if op == 'view':
        if value == 'random':
            tdict['films'] = sample(films, random_num)
            tdict['listtitle'] = u'%s случайных диафильмов:' % random_num
            tpl = 'listview.html'
            
        elif value == 'recent':
            def recent():
                keyfunc = lambda x: x['added']
                recent = max(films, key=keyfunc)
                return [x for x in films if x['added'] == recent['added']]
            
            tdict['films'] = recent()
            tdict['listtitle'] = u'Последние добавленные диафильмы:'
            tpl = 'listview.html'
            
        elif value:
            film = get_data_item('films', 'url', value)
            if not film: abort(404)
            
            'Temporary solution'
            film['chars'] = [{'name': x, 
                              'url': urlify(x)} for x in film['chars']]
            
            nextrandom = choice(films)
            
            tdict.update(film=film, backbtn=True, nextrandom=nextrandom)
            tpl = 'filmview.html'
        else:
            tdict.update(films=films)
            tpl = 'listview.html'
    
    return render(tpl, **tdict)

@app.route('/slides/year/<value>')
def year(value=None):
    years = sample_data('films', 'year')
    
    def environs(val, s):
        '''Returns a tuple of left and right values from environs of val 
        in sequence s.'''
        idx = s.index(val)
        left = idx > 0 and s[idx-1] or None
        right = idx < len(s)-1 and s[idx+1] or None
        return (left, right)
    
    tdict = dict(films=get_data('films', 'year', value),
                 listtitle=u'Диафильмы с меткой <em>«%s»</em>:' % value,
                 environs=environs(value, years),
                 environsurlbase='/slides/year/')
    tpl = 'listview.html'
    return render(tpl, **tdict)

@app.route('/slides/label/<value>')
def label(value=None):
    name = label_name_func(value)
    tdict = dict(sortbyyear=True,
                 films=get_data('films', 'labels', ('url', value)),
                 listtitle=u'Диафильмы с меткой <em>«%s»</em>:' % name)
    tpl = 'listview.html'
    return render(tpl, **tdict)


@app.route('/studios/')
@app.route('/studios/<id>')
def studios(id=None):
    tdict = dict(datapath='/data/studios/', scriptroot='studios')
    tpl = None

    if id:
        def entity_films(entity):
            return entity['films']
        
        tdict.update(get_entity('studios', 
                                 entity_films, 
                                 id, 
                                 u'Диафильмы студии «%s»:',
                                 'name'))
        tpl = 'listview.html'
    else:
        tdict['entities'] = get_data('studios')
        tpl = 'entitiesview.html'
    
    return render(tpl, **tdict)

@app.route('/authors/')
@app.route('/authors/<id>')
def authors(id=None):
    tdict = dict(scriptroot='authors')
    tpl = None

    if id:
        def entity_films(entity):
            keyfunc = lambda x: x['title']
            works = [x['film'] for x in entity['works']]
            return sorted(rem_dict_duplicates(works, 'id'), key=keyfunc)
        
        tdict.update(get_entity('authors', entity_films, id, u'Диафильмы:'))
        tpl = 'listview.html'
    else:
        def submenu():
            submenu = {'title': u'Быстрый переход:', 'anchors': []}
            for w in sorted(WORK_TITLES):
                submenu['anchors'].append({'href': urlify(w), 'text': w})
            return submenu
        
        def authors_expanded():
            def expand(x, y):
                dcx = deepcopy(x)
                dcx['singlework'] = y
                return dcx
            keyfunc = lambda x: x['singlework']
            authors = get_data('authors')
            expanded = [expand(x, y) for x in authors for y in x['worktitles']]
            return sorted(expanded, key=keyfunc)
        
        tdict['entities'] = authors_expanded()
        tdict.update(submenu=submenu(), viewmode='list', nogrid=True)
        tpl = 'authorsview.html'
    
    return render(tpl, **tdict)

@app.route('/characters/')
@app.route('/characters/<id>')
def characters(id=None):
    tdict = dict(datapath='/data/chars/', scriptroot='characters')
    tpl = None
    
    if id:
        def entity_films(entity):
            return get_data('films', 'chars', entity['name'])
        
        tdict.update(get_entity('chars',
                                 entity_films,
                                 id,
                                 u'Диафильмы, в которых встречается %s:',
                                 'name'))
        tpl = 'listview.html'
    else:
        tdict['entities'] = get_data('chars')
        tpl = 'entitiesview.html'
    
    return render(tpl, **tdict)

@app.route('/search/')
@app.route('/search/<query>')
def search(query=None):
    tdict = dict(query=query)
    atime = datetime.now()

    def append_results(resli, data, searchprop, urlbase, urlprop, titleprop, section):
        for d in data:
            if query.lower() in d[searchprop].lower(): 
                res = {'url': urlbase % d[urlprop],
                       'title': d[titleprop],
                       'srcurl': '/',
                       'src': u'Кашалотик',
                       'section': section}
                resli.append(res)

    results = list()
    
    append_results(results, get_data('films'), 'title', 
                   '/slides/view/%s', 'url', 
                   'title', u'Диафильмы')
    
    append_results(results, get_data('authors'), 'name', 
                   '/authors/%s', 'url', 
                   'name', u'Авторы')

    append_results(results, get_data('chars'), 'name', 
               '/characters/%s', 'url', 
               'name', u'Персонажи')

    append_results(results, get_data('studios'), 'name', 
               '/studios/%s', 'url', 
               'name', u'Студии')

    tdict['results'] = results
    btime = datetime.now()
    td = btime - atime
    tdict['stime'] = '%s.%s' % (td.seconds, td.microseconds)
    return render_template('search.html', **tdict)

@app.route('/db/<id>')
def dbhandle(id=None):
    if id == 'up':
        kdb.reset()
        kdb.upload()
        
    return render_template('index.html', 
                           **{'page': 'Database uploaded'})

@app.route('/xml/<name>.xml')
def render_xml(name):
    name = str(name)
    xml_keys = {'authors': 'name', 'slides': 'id'}
    values = {}
    
    if name in xml_keys:
        db = yaml.load(open('%s.yaml' % name, 'r').read())
        for k in db.keys():
            db[k][xml_keys[name]] = k
        values = {name: db.values()}
    return render_template('%s.xml' % name, **values)
        

@app.route('/about/')
def about():
    tdict = {'about': True}
    return render('about.html', **tdict)

@app.route('/mail/', methods=['GET', 'POST'])
def mail_send():
    form = ['sender', 'subject', 'body']
    errs = { 'general': u"""Произошла какая-то ошибка. Вы можете попробовать 
                            еще раз или <a href="/slides">вернуться к 
                            просмотру</a> диафильмов""",
            'sender': u"""Поправьте, пожалуйста, адрес вашей почты.""",
            'email': u"""Неправильный адрес электронной почты.""",
            'body': u"""Пустые письма читать не интересно.""",
            'subject': u"""Письма без темы сложно обнаружить в ящике.""",
            'success': u"""Письмо отправлено, теперь вы можете 
                            <a href="/slides">вернуться к 
                            просмотру</a> диафильмов."""
            }
    tdict = {}
    if request.method == 'POST':
        def valid_email(mail):
            return re.search( r'(<)?(\w+@\w+(?:\.\w+)+)(?(1)>)' , mail)
            
        try:
            for i in form:
                v = request.form.get(i)
                if i == 'sender':
                    if not valid_email(v): tdict['error'] = errs['email']
                if not v: tdict['error'] = errs[i]
                tdict[i] = v
            
            if not tdict.get('error'):
                mail.send_mail(sender=request.form.get('sender'), 
                               to=MAILTO, 
                               subject=request.form.get('subject'), 
                               body=request.form.get('body'))
                tdict['success'] = errs['success']
        except:
            tdict['error'] = errs['general']

    return render('mail.html', **tdict)

@app.route('/sv/<id>')
def sv(id):
    'Processes request for Simple Viewer page.'
    tdict = {'id': id, 'baseurl': baseurl()}
    return render_template('sv.html', **tdict)

# main
def main():
    util.run_wsgi_app(app)

if __name__ == '__main__':
    main()