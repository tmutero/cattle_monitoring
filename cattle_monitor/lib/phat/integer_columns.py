from sqlalchemy.types import Integer
from sqlalchemy import Column

def col_integer(extra_params={}): return Column(Integer, **extra_params)

def col_integer_not_nullable(extra_params={}):
    extra_params.update({'nullable':False})
    return col_integer(extra_params)

def col_integer_default(default=None, extra_params={}):
    if not default: return False
    if not isinstance(default, int): return False
    extra_params['default'] = default
    return col_integer(extra_params=extra_params)

def col_integer_default_not_nullable(default=None, extra_params={}):
    if not default: return False
    if not isinstance(default, int): return False
    extra_params['default'] = default
    return col_integer_not_nullable(extra_params=extra_params)

def col_integer_unique(): return col_integer(extra_params={'unique':True})

def col_integer_unique_not_nullable(): return col_integer_not_nullable(extra_params={'unique':True})

def get_id_primarykey():
    primary_id_dict = {'name':'id', 'autoincrement':True, 'unique':True, 'nullable':False, 'primary_key':True}
    return col_integer(primary_id_dict)

common_integer_columns = {
    'integer':col_integer,
    'integer_not_nullable':col_integer_not_nullable,
    'integer_default': col_integer_default,
    'integer_default_not_nullable': col_integer_default_not_nullable,
    'integer_unique': col_integer_unique,
    'integer_unique_not_nullable': col_integer_unique_not_nullable,
        }
