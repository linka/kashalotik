# -*- coding: utf-8 -*-
# taken from django's urlify.js and corrected a bit
RUSSIAN_MAP = {
    u'а':u'a', u'б':u'b', u'в':u'v', u'г':u'g', u'д':u'd', u'е':u'e', u'ё':u'yo', u'ж':u'zh',
    u'з':u'z', u'и':u'i', u'й':u'j', u'к':u'k', u'л':u'l', u'м':u'm', u'н':u'n', u'о':u'o',
    u'п':u'p', u'р':u'r', u'с':u's', u'т':u't', u'у':u'u', u'ф':u'f', u'х':u'h', u'ц':u'ts',
    u'ч':u'ch', u'ш':u'sh', u'щ':u'sch', u'ъ':u'', u'ы':u'y', u'ь':u'', u'э':u'e', u'ю':u'yu',
    u'я':u'ya',
    u'А':u'a', u'Б':u'b', u'В':u'v', u'Г':u'g', u'Д':u'd', u'Е':u'e', u'Ё':u'yo', u'Ж':u'zh',
    u'З':u'z', u'И':u'i', u'Й':u'j', u'К':u'k', u'Л':u'l', u'М':u'm', u'Н':u'n', u'О':u'o',
    u'П':u'p', u'Р':u'r', u'С':u's', u'Т':u't', u'У':u'u', u'Ф':u'f', u'Х':u'h', u'Ц':u'ts',
    u'Ч':u'ch', u'Ш':u'sh', u'Щ':u'sch', u'Ъ':u'', u'Ы':u'y', u'Ь':u'', u'Э':u'e', u'Ю':u'yu',
    u'Я':u'ya'
}

UKRAINIAN_MAP = {
    u'Є':u'ye', u'І':u'i', u'Ї':u'yi', u'Ґ':u'g', u'є':u'ye', u'і':u'i', u'ї':u'yi', u'ґ':u'g'
}

MAPS = dict(RUSSIAN_MAP, **UKRAINIAN_MAP)

def urlify(s):
    result = u''
    s = s.replace(' ', '-')
    s = s.replace('.', '-')
    s = s.replace(',', '-')
    s = s.replace('?', '')
    for alpha in s:
        try: result += MAPS[alpha]
        except: result+= alpha
    return result

def htmlify(s):
    s = s.replace('\n', '<br/>')
    return s

def anchor(s):
    return {'name':s, 'url':urlify(s)}

def filedict(file):
    return {'name':file['name'], 'type':file['type'], 'url':'/storage/%s/%s' % (file['type'], file['name'])}

def download(file):
    return {'name':file.name, 'type':file.type, 'url':'/storage/%s/%s' % (file.type, file.name)}

def rem_dict_duplicates(li, keyProp):
    torem = [y for (idx, x) in enumerate(li) for y in li[idx+1:] if x[keyProp] == y[keyProp]]
    for r in torem:
        li.remove(r) 
    return li

def try_nested(x, val):
    '''Gives boolean return, when looks in x, which can be dict, list or 
    list of dicts, for the given val, which can be single value or tuple.'''
    if isinstance(val, tuple):
        if isinstance(x, list):
            return [y for y in x if y[val[0]] == val[1]]
        else:
            return x[val[0]] == val[1]
    else:
        if isinstance(x, list):
            return val in x
        else:
            return x == val
    return False

def get_valid_option(x, li, default):
    '''Validates value by given list range or returns given default.'''
    return x if x in li else default

if __name__ == '__main__':
    pass