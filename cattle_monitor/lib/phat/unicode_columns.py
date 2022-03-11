from sqlalchemy.types import Unicode
from sqlalchemy import Column

def col_unicode(length=None, extra_params={}):
    if not length: return False
    return Column(Unicode(length), **extra_params)

def col_unicode_not_nullable(length=None, extra_params={}): 
    if not length: return False
    extra_params.update({'nullable':False})
    return col_unicode(length=length, extra_params=extra_params)

def col_unicode_default(length=None, default=None):
    if not length: return False
    if not default: return False
    if not isinstance(default, str): return False
    return col_unicode(length=length, extra_params={'default':default})

def col_unicode_default_not_nullable(length=None, default=None):
    if not length: return False
    if not default: return False
    if not isinstance(default, str): return False
    return col_unicode(length=length, extra_params={'default':default, 'nullable':False})

def col_unicode_unique(length=None): 
    if not length: return False
    return col_unicode(length=length, extra_params={'unique':True})

def col_unicode_unique_not_nullable(length=None): 
    if not length: return False
    return col_unicode(length=length, extra_params={'unique':True, 'nullable':False})

def col_code(): return col_unicode(length=10)

def col_code_default(default): return col_unicode_default(length=10, default=default)

def col_code_unique(): return col_unicode_unique(length=10)

def col_code_not_nullable(): return col_unicode_not_nullable(length=10)

def col_code_unique_not_nullable(default): return col_unicode_unique_not_nullable(length=10)

def col_code_default_not_nullable(default): return col_unicode_default_not_nullable(length=10, default=default)


def col_title(): return col_unicode(length=100)

def col_title_default(default): return col_unicode_default(length=100, default=default)

def col_title_unique(): return col_unicode_unique(length=100)

def col_title_not_nullable(): return col_unicode_not_nullable(length=100)

def col_title_unique_not_nullable(default): return col_unicode_unique_not_nullable(length=100)

def col_title_default_not_nullable(default): return col_unicode_default_not_nullable(length=100, default=default)


def col_description(): return col_unicode(length=200)

def col_description_default(default): return col_unicode_default(length=200, default=default)

def col_description_unique(): return col_unicode_unique(length=200)

def col_description_not_nullable(): return col_unicode_not_nullable(length=200)

def col_description_unique_not_nullable(default): return col_unicode_unique_not_nullable(length=200)

def col_description_default_not_nullable(default): return col_unicode_default_not_nullable(length=200, default=default)


def col_longtext(): return col_unicode(length=1024)

def col_longtext_default(default): return col_unicode_default(length=1024, default=default)

def col_longtext_unique(): return col_unicode_unique(length=1024)

def col_longtext_not_nullable(): return col_unicode_not_nullable(length=1024)

def col_longtext_unique_not_nullable(default): return col_unicode_unique_not_nullable(length=1024)

def col_longtext_default_not_nullable(default): return col_unicode_default_not_nullable(length=1024, default=default)


def col_hugetext(): return col_unicode(length=20480)

def col_hugetext_default(default): return col_unicode_default(length=20480, default=default)

def col_hugetext_unique(): return col_unicode_unique(length=20480)

def col_hugetext_not_nullable(): return col_unicode_not_nullable(length=20480)

def col_hugetext_unique_not_nullable(default): return col_unicode_unique_not_nullable(length=20480)

def col_hugetext_default_not_nullable(default): return col_unicode_default_not_nullable(length=20480, default=default)

common_unicode_columns = {
        'code':col_code,
        'code_default':col_code_default,
        'code_unique':col_code_unique,
        'code_not_nullable':col_code_not_nullable,
        'code_default_not_nullable':col_code_default_not_nullable,
        'code_unique_not_nullable':col_code_unique_not_nullable,

        'title':col_title,
        'title_default':col_title_default,
        'title_unique':col_title_unique,
        'title_not_nullable':col_title_not_nullable,
        'title_default_not_nullable':col_title_default_not_nullable,
        'title_unique_not_nullable':col_title_unique_not_nullable,

        'description':col_description,
        'description_default':col_description_default,
        'description_unique':col_description_unique,
        'description_not_nullable':col_description_not_nullable,
        'description_default_not_nullable':col_description_default_not_nullable,
        'description_unique_not_nullable':col_description_unique_not_nullable,

        'longtext':col_longtext,
        'longtext_default':col_longtext_default,
        'longtext_unique':col_longtext_unique,
        'longtext_not_nullable':col_longtext_not_nullable,
        'longtext_default_not_nullable':col_longtext_default_not_nullable,
        'longtext_unique_not_nullable':col_longtext_unique_not_nullable,

        'hugetext':col_hugetext,
        'hugetext_default':col_hugetext_default,
        'hugetext_unique':col_hugetext_unique,
        'hugetext_not_nullable':col_hugetext_not_nullable,
        'hugetext_default_not_nullable':col_hugetext_default_not_nullable,
        'hugetext_unique_not_nullable':col_hugetext_unique_not_nullable,
        }
