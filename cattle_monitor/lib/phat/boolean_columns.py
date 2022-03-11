from sqlalchemy.types import Boolean
from sqlalchemy import Column

def get_boolean_column(extra_params={}): 
    return Column(Boolean(), **extra_params)

def col_boolean(): return get_boolean_column()

def col_boolean_default_true(): return get_boolean_column({'default':True})

def col_boolean_default_false(): return get_boolean_column({'default':False})

def col_boolean_not_nullable(): return get_boolean_column({'nullable':False})

def col_boolean_default_true_not_nullable(): return get_boolean_column({'nullable':False, 'default':True})

def col_boolean_default_false_not_nullable(): return get_boolean_column({'nullable':False, 'default':False})

common_boolean_columns = {
    'boolean':col_boolean,
    'boolean_not_nullable':col_boolean_not_nullable,

    'boolean_default_true': col_boolean_default_true,
    'boolean_default_true_not_nullable': col_boolean_default_true_not_nullable,

    'boolean_default_false': col_boolean_default_false,
    'boolean_default_false_not_nullable': col_boolean_default_false_not_nullable,
        }
