# -*- coding: utf-8 -*-

import subprocess, os, sys

MODELS = ['FilmModel', 'StudioModel', 'FileModel', 'SourceModel', 'AuthorModel', 'LinkModel', 'WorkModel', 'CharModel', 'BioPicModel', 'CharPicModel']

DIR = 'db'
FILE = 'db/%s.sqlite'
EMAIL = 'lista.anta@gmail.com'

ARGS = {'download': {'action': 'download_data',
                      'url': "http://localhost:8084/remote_api",
                      'application': 'kashalotik-2',
                      'email': EMAIL},
        'upload': {'action': 'upload_data',
                      'url': "http://localhost:8084/remote_api",
                      'application': 'kashalotik-2',
                      'email': EMAIL}}

PATH = """python "%(exec_path)s" %(action)s --application=%(app)s --url=%(url)s --kind=%(kind)s --filename=%(file)s --email=%(email)s --log_file=bulkloader.log --passin"""
EXEC = "appcfg.py"

def mkdbdir(path):
    if not os.path.exists(path):
        os.mkdir(path)

def log(msg):
    print msg

def gae_path():
    env_path = os.environ['PATH']
    li = env_path.split(';')
    for i in li:
        if 'google_appengine' in i:
            return i
    return ''

def construct_call(id, kind, file, exec_path):
    return PATH % dict(action=ARGS[id]['action'], 
                      app=ARGS[id]['application'], 
                      url=ARGS[id]['url'], 
                      kind=kind, 
                      file=file, 
                      email=ARGS[id]['email'], 
                      exec_path=exec_path)

def appcfg(option):
    exec_path = os.path.join(gae_path(), EXEC)
    log('Using GAE executable: "%s"' % exec_path)
    
    for m in MODELS:
        file = FILE % m
        
        if option in ARGS:
            if option == 'download':
                mkdbdir(DIR)
                
                try:
                    os.remove(file)
                    log('Removed file: %s' % file)
                except:
                    log('File %s does not exist' % file) 
    
            path = construct_call(option, m, file, exec_path)
            log('Executing: %s' % path)
            if path:
                p = subprocess.Popen(path)
                p.communicate()
        else:
            log("Option '%s' is not supported" % option)

def main():
    args = sys.argv
    
    try:
        appcfg(args[1])
    except:
        log(sys.exc_info())
        return
    
if __name__ == '__main__':
    main()