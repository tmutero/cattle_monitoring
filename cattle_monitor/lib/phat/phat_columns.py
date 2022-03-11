from sqlalchemy.types import Unicode, Integer, DateTime, Boolean, Date, Numeric, Time, Binary
from sqlalchemy import Table, ForeignKey, Column
from lib.phat.unicode_columns import common_unicode_columns
from lib.phat.integer_columns import common_integer_columns
from lib.phat.integer_columns import common_numeric_columns

def get_numeric_column(length=None, extra_params={}):
    if not length: return False
    if isinstance(length, tuple): 
        return Column(Numeric(length, **extra_params))

def get_integer_column(extra_params={}):
    return Column(Integer, **extra_params)

def get_boolean_column(extra_params):
    return Column(Boolean, **extra_params)

def get_datetime_column(extra_params):
    return Column(DateTime, **extra_params)

def get_date_column(extra_params):
    return Column(Date, **extra_params)

def get_time_column(extra_params):
    return Column(Time, **extra_params)

def get_datetime_now(name=None):
    if not name: return False
    datetime_now_dict = {'name':name, 'nullable':False, 'default':datetime.now}
    datetime_now_dict['column'] = get_datetime_column(datetime_now_dict)
    datetime_now_dict['datatype'] = 'datetime'
    return datetime_now_dict

def get_datetime(name=None):
    if not name: return False
    datetime_dict = {'name':name, 'nullable':False}
    datetime_dict['column'] = get_datetime_column()
    datetime_dict['datatype'] = 'datetime'
    return datetime_dict

def get_date_now(name=None):
    if not name: return False
    date_now_dict = {'name':name, 'nullable':False, 'default':date.now}
    date_now_dict['column'] = get_date_column(date_now_dict)
    date_now_dict['datatype'] = 'date'
    return date_now_dict

def get_time_now(name=None):
    if not name: return False
    time_now_dict = {'name':name, 'nullable':False, 'default':time.now}
    time_now_dict['column'] = get_time_column(time_now_dict)
    time_now_dict['datatype'] = 'time'
    return time_now_dict

def get_time(name=None):
    if not name: return False
    time_dict = {'name':name, 'nullable':False}
    time_dict['column'] = get_time_column()
    time_dict['datatype'] = 'time'
    return time_dict

def get_date(name=None):
    if not name: return False
    date_dict = {'name':name, 'nullable':False}
    date_dict['column'] = get_date_column()
    date_dict['datatype'] = 'date'
    return date_dict

def get_boolean_true(name=None):
    if not name: return False
    boolean_dict = {'name':name, 'nullable':False, 'default':True}
    boolean_dict['column'] = get_boolean_column(boolean_dict)
    boolean_dict['datatype'] = 'boolean'
    return boolean_dict

def get_boolean_false(name=None):
    if not name: return False
    boolean_dict = {'name':name, 'nullable':False, 'default':False}
    boolean_dict['column'] = get_boolean_column(boolean_dict)
    boolean_dict['datatype'] = 'boolean'
    return boolean_dict

