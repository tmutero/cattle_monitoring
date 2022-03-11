from sqlalchemy.types import Date, Time, DateTime
from sqlalchemy import Column
from datetime import datetime

#DATETIMES HERE
def get_datetime_column(extra_params={}): return Column(DateTime(), **extra_params)

def col_datetime(extra_params={}): return get_datetime_column(extra_params=extra_params)

def col_datetime_not_nullable(extra_params={}):
    extra_params['nullable'] = False
    return get_datetime_column(extra_params)

def col_datetime_default_now(extra_params={}):
    extra_params['default'] = datetime.now
    return col_datetime(extra_params)

def col_datetime_default_now_not_nullable():
    extra_params['default'] = datetime.now
    return col_datetime_not_nullable(extra_params)

#DATES HERE
def get_date_column(extra_params={}): return Column(Date(), **extra_params)

def col_date(extra_params={}): return get_date_column(extra_params=extra_params)

def col_date_not_nullable(extra_params={}):
    extra_params['nullable'] = False
    return get_date_column(extra_params)

def col_date_default_now():
    extra_params['default'] = datetime.now
    return col_date(extra_params)

def col_date_default_now_not_nullable():
    extra_params['default'] = datetime.now
    return col_date_not_nullable(extra_params)

#DATES HERE
def get_time_column(extra_params={}): return Column(Time(), **extra_params)

def col_time(extra_params={}): return get_time_column(extra_params=extra_params)

def col_time_not_nullable(extra_params={}):
    extra_params['nullable'] = False
    return get_time_column(extra_params)

def col_time_default_now():
    extra_params['default'] = datetime.now
    return col_time(extra_params)

def col_time_default_now_not_nullable():
    extra_params['default'] = datetime.now
    return col_time_not_nullable(extra_params)


common_datetime_columns = {
        'datetime': col_datetime,
        'datetime_not_nullable': col_datetime_not_nullable,
        'datetime_default_now': col_datetime_default_now,
        'datetime_default_now_nullable': col_datetime_default_now_not_nullable,

        'time': col_time,
        'time_not_nullable': col_time_not_nullable,
        'time_default_now': col_time_default_now,
        'time_default_now_nullable': col_time_default_now_not_nullable,

        'date': col_date,
        'date_not_nullable': col_date_not_nullable,
        'date_default_now': col_date_default_now,
        'date_default_now_nullable': col_date_default_now_not_nullable,
        }
