from cattle_monitor.model import DeclarativeBase, metadata, DBSession
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import relation, synonym
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import asc, desc
import os
from datetime import datetime
from hashlib import sha256
from lib.phat.unicode_columns import common_unicode_columns
from lib.phat.integer_columns import common_integer_columns
#from lib.phat.numeric_columns import common_numeric_columns
#from lib.phat.boolean_columns import common_boolean_columns
#from lib.phat.datetime_columns import common_datetime_columns

def get_numeric_column():
    return Column(Numeric(22,8))

def get_boolean_column():
    return Column(Boolean)

def get_datetime_column():
    return Column(DateTime)

common_columns = {
        'numeric_columns':common_numeric_columns,
        'currency':common_numeric_columns.get('currency'),
        'boolean':common_numeric_columns.get('boolean'),
        'datetime':common_datetime_columns.get('datetime'),
        }

common_columns = {
        'unicode_columns':common_unicode_columns,
        'integer_columns':common_integer_columns,

        'description':common_unicode_columns.get('description'),
        'title':common_unicode_columns.get('title'),
        'longtext':common_unicode_columns.get('longtext'),
        'integer':common_unicode_columns.get('longtext'),

        'numeric':get_numeric_column,
        'boolean':get_boolean_column,
        'datetime':get_datetime_column,
                      }

class PhatBase(object):

    #id = Column(Integer, autoincrement=True, primary_key=True)
    id = get_id_primarykey().get('column')
    added_by = Column(Integer, nullable=False)
    added = Column(DateTime, default=datetime.now)
    active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<{self.id}: {self.__tablename__[4:].title()}>"

    @classmethod
    def latest_entry(cls):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                order_by(cls.added.desc()). \
                first()

    @classmethod
    def oldest_entry(cls):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                order_by(cls.added.asc()). \
                first()

    @classmethod
    def get_all(cls, attr, active=True):
        return DBSession.query(cls). \
                filter(cls.active==active). \
                order_by(asc(getattr(cls, attr))). \
                all()

    @classmethod
    def get_limit(cls, limit, attr, active=True):
        return DBSession.query(cls). \
                filter(cls.active==active). \
                order_by(asc(getattr(cls, attr))). \
                limit(limit)

    @classmethod
    def by_attr_count(cls, attr, value):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr)==value). \
                count()

    @classmethod
    def by_attr_one(cls, attr, value):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr)==value). \
                one()

    @classmethod
    def by_attr_first(cls, attr, value):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr)==value). \
                first()

    @classmethod
    def by_attr_all(cls, attr, value):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr)==value). \
                all()

    @classmethod
    def by_attr_limit(cls, attr, value, limit):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr)==value). \
                limit(limit)

    @classmethod
    def like_attr_one(cls, attr, value, limit):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr).like(value)). \
                one()

    @classmethod
    def like_attr_first(cls, attr, value, limit):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr).like(value)). \
                first()

    @classmethod
    def like_attr_all(cls, attr, value, limit):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr).like(value)). \
                all()

    @classmethod
    def like_attr_limit(cls, attr, value, limit):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr).like(value)). \
                limit(limit)

    @classmethod
    def by_id(cls, id):
        return cls.by_attr_first('id', id)

def get_default_columns():
    default_columns = {}
    default_config = {}

    id_config = get_id_primarykey()
    id_column = id_config.pop('column')
    default_columns['id'] = id_column
    default_config['id'] = id_config

    added_config = get_datetime_now('added')
    added_column = added_config.pop('column')
    default_columns['added'] = added_column
    default_config['added'] = added_config

    added_by_config = get_id_secondary('added_by')
    added_by_column = added_by_config.pop('column')
    default_columns['added_by'] = added_by_column
    default_config['added_by'] = added_by_config

    edited_config = get_datetime_now('edited')
    edited_column = edited_config.pop('column')
    default_columns['edited'] = edited_column
    default_config['edited'] = edited_config

    edited_by_config = get_id_secondary('edited_by')
    edited_by_column = edited_by_config.pop('column')
    default_columns['edited_by'] = edited_by_column
    default_config['edited_by'] = edited_by_config

    active_config = get_boolean_true('active')
    active_column = active_config.pop('column')
    default_columns['active'] = active_column
    default_config['active'] = active_config

    default_config['default_columns'] = default_columns
    return default_config

def get_type_table(model_name=None, table_name=None):
    if not model_name or not table_name: return False
    if 'type' in model_name.lower(): return False
    if 'type' in table_name.lower(): return False
    tablename = f'tbl_{table_name.lower()}_type'
    modelname = f'{model_name}Type'
    primary_id = get_id_primarykey()
    name = get_title_column()

    type_table_dict = {
            '__tablename__':tablename,
            'id':primary_id.get('column'),
            'name':name.get('column'),
                       }

    type_table = type(model_name, (PhatBase, DeclarativeBase), type_table_dict)

    type_table_config = {}
    columns = []
    columns.append(primary_id)
    columns.append(name)

    type_table_config['modelname'] = modelname
    type_table_config['tablename'] = tablename
    type_table_config['table_dict'] = type_table_dict
    return type_table_config, type_table

datatype_dict = {
        'unicode':Unicode, 
        'integer':Integer, 
        'boolean':Boolean, 
        'date':Date,
        'time':Time,
        'datetime':DateTime,
        'numeric':Numeric,
        'binary':Binary,
        }

needs_length = ['unicode', 'numeric']

def get_column_dict(column_config):
    column_dict = {}

    column_name = column_config.get('name', None)
    if not column_name: return False

    default = column_config.get('default', None)
    if default: column_dict['default'] = default

    datatype_name = column_config.get('datatype', None)
    datatype = datatype_dict.get(datatype_name, None)
    if not datatype: return False

    length = column_config.get('length', None)
    if datatype_name in needs_length:
        if length: datatype_instance = datatype(length)
        elif not length: return False
    else: datatype_instance = datatype()

    params = ['unique', 'auto_increment', 'primary_key', 'nullable']

    for param in params:
        column_param = column_config.get(param, None)
        if column_param == True: column_dict[param] = True
        elif column_param == False: column_dict[param] = False

    column_dict['name'] = column_name
    column_dict['column'] = Column(datatype_instance, **column_dict)
    return column_dict

def get_model_dict(tablename=None, columns=[]):
    model_dict = {}
    print("breaked")
    if len(columns) == 0: return False
    default_column_config = get_default_columns()
    default_columns = default_column_config.pop('default_columns')

    column_config = {}
    for column in columns:
        column_name = column.get('name', None)
        if not column_name: pass
        column_config[column_name] = get_column_dict(column)

        column_dict = get_column_dict(column)
        column_instance = column_dict.get('column')
        column_config[column_name] = column_instance
    
    column_config['__tablename__'] = f'tbl_{tablename}'.lower()
    column_config.update(default_columns)
    model = type(tablename, (declarative_base,), column_config)
    
    model_dict['table'] = model
    model_dict['column_config'] = column_config
    return model_dict

common_columns = {'title', get_title_column}
