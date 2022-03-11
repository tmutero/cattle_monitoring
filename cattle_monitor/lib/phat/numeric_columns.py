from sqlalchemy.types import Numeric
from sqlalchemy import Column

def get_numeric_column(precision=None, scale=None, extra_params={}):
    if not precision: return False
    if not isinstance(precision, int): return False
    if not scale: return False
    if not isinstance(scale, int): return False
    return Column(Numeric(precision=precision, scale=scale), **extra_params)

def col_numeric(precision=None, scale=None, extra_params={}): return get_numeric_column(precision=22, scale=8, extra_params=extra_params)

def col_numeric_not_nullable(precision=None, scale=None, extra_params={}): 
    extra_params.update({'nullable':False})
    return get_numeric_column(precision=precision, scale=scale, extra_params=extra_params)

def col_currency(): return col_numeric(precision=22, scale=8)
def col_currency_not_nullable(): return col_numeric_not_nullable(precision=22, scale=8)

def col_currency_unique(): return col_numeric(precision=22, scale=8, extra_params={'unique':True})
def col_currency_unique_not_nullable(): return col_numeric_not_nullable(precision=22, scale=8, extra_params={'unique':True})

def col_currency_default(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric(precision=22, scale=8, extra_params=extra_params)

def col_currency_default_not_nullable(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric_not_nullable(precision=22, scale=8, extra_params=extra_params)

def col_geocoord(): return get_numeric_column(precision=10, scale=7)
def col_geocoord_not_nullable(): return col_numeric_not_nullable(precision=10, scale=7)

def col_geocoord_default(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric(precision=10, scale=7, extra_params=extra_params)

def col_geocoord_default_not_nullable(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric_not_nullable(precision=10, scale=7, extra_params=extra_params)

def col_geocoord_unique(): return col_numeric(precision=10, scale=7, extra_params={'unique':True})

def col_geocoord_unique_not_nullable(): 
    extra_params = {'unique':True}
    return col_numeric_not_nullable(precision=10, scale=7, extra_params=extra_params)


def col_percentage(): return get_numeric_column(precision=5, scale=2)
def col_percentage_not_nullable(): return col_numeric_not_nullable(precision=5, scale=2)

def col_percentage_default(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric(precision=5, scale=2, extra_params=extra_params)

def col_percentage_default_not_nullable(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric_not_nullable(precision=5, scale=2, extra_params=extra_params)

def col_percentage_unique(): return col_numeric(precision=5, scale=2, extra_params={'unique':True})

def col_percentage_unique_not_nullable(): 
    extra_params = {'unique':True}
    return col_numeric_not_nullable(precision=5, scale=2, extra_params=extra_params)

def col_factor(): return get_numeric_column(precision=8, scale=4)
def col_factor_not_nullable(): return col_numeric_not_nullable(precision=8, scale=4)

def col_factor_default(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric(precision=8, scale=4, extra_params=extra_params)

def col_factor_default_not_nullable(default=None): 
    if not default: return False
    if not isinstance(default, float): return False
    extra_params = {'default':default}
    return col_numeric_not_nullable(precision=8, scale=4, extra_params=extra_params)

def col_factor_unique(): return col_numeric(precision=8, scale=4, extra_params={'unique':True})

def col_factor_unique_not_nullable(): 
    extra_params = {'unique':True}
    return col_numeric_not_nullable(precision=8, scale=4, extra_params=extra_params)

common_numeric_columns = {
    'numeric':col_currency,
    'numeric_not_nullable':col_currency_not_nullable,
    'numeric_unique':col_currency_unique,
    'numeric_unique_not_nullable':col_currency_unique_not_nullable,
    'numeric_default':col_currency_default,
    'numeric_default_not_nullable':col_currency_default_not_nullable,

    'currency':col_currency,
    'currency_not_nullable':col_currency_not_nullable,
    'currency_unique':col_currency_unique,
    'currency_unique_not_nullable':col_currency_unique_not_nullable,
    'currency_default':col_currency_default,
    'currency_default_not_nullable':col_currency_default_not_nullable,

    'geocoord':col_geocoord,
    'geocoord_not_nullable':col_geocoord_not_nullable,
    'geocoord_unique':col_geocoord_unique,
    'geocoord_unique_not_nullable':col_geocoord_unique_not_nullable,
    'geocoord_default':col_geocoord_default,
    'geocoord_default_not_nullable':col_geocoord_default_not_nullable,

    'percentage':col_percentage,
    'percentage_not_nullable':col_percentage_not_nullable,
    'percentage_unique':col_percentage_unique,
    'percentage_unique_not_nullable':col_percentage_unique_not_nullable,
    'percentage_default':col_percentage_default,
    'percentage_default_not_nullable':col_percentage_default_not_nullable,

    'factor':col_factor,
    'factor_not_nullable':col_factor_not_nullable,
    'factor_unique':col_factor_unique,
    'factor_unique_not_nullable':col_factor_unique_not_nullable,
    'factor_default':col_factor_default,
    'factor_default_not_nullable':col_factor_default_not_nullable,
        }
