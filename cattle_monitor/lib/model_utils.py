# -*- coding: utf-8 -*-

import os
import uuid
from hashlib import sha256
from datetime import datetime

from sqlalchemy import event, Table
from sqlalchemy.util import OrderedDict
from sqlalchemy import asc, desc, Column
from sqlalchemy.orm import relation, synonym, mapper
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.types import Unicode, Numeric, Boolean, DateTime, Date, Time, Integer

from cattle_monitor.model import DeclarativeBase, metadata, DBSession
from cattle_monitor.lib.phat.unicode_columns import common_unicode_columns
from cattle_monitor.lib.phat.numeric_columns import common_numeric_columns
from cattle_monitor.lib.phat.boolean_columns import common_boolean_columns
from cattle_monitor.lib.phat.datetime_columns import common_datetime_columns
from cattle_monitor.lib.phat.integer_columns import common_integer_columns, get_id_primarykey

def get_numeric_column():
    return Column(Numeric(22, 8))

def get_boolean_column():
    return Column(Boolean)

def get_datetime_column():
    return Column(DateTime)

def get_time_column():
    return Column(Time)

def get_date_column():
    return Column(Date)

common_columns = {
        'description': common_unicode_columns.get('description'),
        'title': common_unicode_columns.get('title'),
        'longtext': common_unicode_columns.get('longtext'),

        'numeric': get_numeric_column,
        'boolean': get_boolean_column,
        'datetime': get_datetime_column,
        'time': get_time_column,
        'date': get_date_column,
        'currency': common_numeric_columns.get('currency'),
                      }

common_columns.update(common_unicode_columns)
common_columns.update(common_integer_columns)
common_columns.update(common_numeric_columns)
common_columns.update(common_boolean_columns)
common_columns.update(common_datetime_columns)

class PhatBase(object):

    id = get_id_primarykey()
    added_by = common_columns.get('integer')()
    added = common_columns.get('datetime_default_now')()
    active = common_columns.get('boolean_default_true')()
    AUDIT_EXCLUSION_LIST = []

    def __repr__(self):
        return f"<{self.id}: {self.__table__}>"

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
                order_by(desc(getattr(cls, attr))). \
                all()

    @classmethod
    def get_limit(cls, limit, attr, active=True):
        return DBSession.query(cls). \
                filter(cls.active==active). \
                order_by(desc(getattr(cls, attr))). \
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
    def by_attr_first_ignore_active(cls, attr, value):
        return DBSession.query(cls). \
                filter(getattr(cls, attr)==value). \
                first()

    @classmethod
    def by_attr_first(cls, attr, value):
        return DBSession.query(cls). \
                filter(cls.active==True). \
                filter(getattr(cls, attr)==value). \
                order_by(desc(getattr(cls, 'id'))). \
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
    def by_id_inactive(cls, id):
        return DBSession.query(cls). \
            filter(cls.active == False). \
            filter(cls.id == id). \
            first()

    @classmethod
    def by_id(cls, id):
        return cls.by_attr_first('id', id)

###############################################################################
# Auto audit code below
###############################################################################

    @staticmethod
    def after_insert(mapper, connection, target):
        PhatBase.before_db_change(mapper, connection, target, 'insert')

    @staticmethod
    def before_update(mapper, connection, target):
        PhatBase.before_db_change(mapper, connection, target, 'update')

    @staticmethod
    def before_delete(mapper, connection, target):
        PhatBase.before_db_change(mapper, connection, target, 'delete')

    @staticmethod
    def before_db_change(mapper, connection, target, action):
        coldict = {
            'audit_action' : action,
            'audit_deleted' : False,
            'audit_datetime' : datetime.now(),
        }
        for key in target.__table__.primary_key:
            value = mapper.get_property_by_column(key).key
            value = getattr(target, value)
            if not value:
                value = 0
            coldict[key.name] = value

        if action == 'delete':
            coldict['audit_deleted'] = True

        else:
            for column in target.__table__.c:

                name = str(column.name)
                if name.startswith('audit'):
                    continue

                if name in PhatBase.AUDIT_EXCLUSION_LIST:
                    continue

                if column.primary_key:
                    continue

                value = mapper.get_property_by_column(column).key
                coldict[column.name] = getattr(target, value)

        record = target.Audit(**coldict)
        PhatBase.DBSession.add(record)

    @classmethod
    def add_auto_audit(cls):
        PhatBase.create_audit_class(cls)
        event.listen(cls, 'after_insert', cls.after_insert)
        event.listen(cls, 'before_update', cls.before_update)
        event.listen(cls, 'before_delete', cls.before_delete)

    @classmethod
    def add_dbsession(cls, session):
        cls.DBSession = session

    @staticmethod
    def create_audit_class(cls):

        def copy_column(col):
            col = col.copy()
            if col.primary_key:
                col.index = True
                col.nullable = False
            else:
                col.nullable = True

            col.unique = False
            col.primary_key = False
            col.default = col.server_default = None
            return col

        audit_id = Column('audit_id', Integer, autoincrement=True, primary_key=True)
        audit_datetime = Column('audit_datetime', DateTime, nullable=False, default=datetime.now)
        audit_deleted = Column('audit_deleted', Boolean, nullable=False, default=False)
        audit_action = Column('audit_action', Unicode(10), nullable=False)
        audit_cols = [audit_id, audit_datetime, audit_deleted, audit_action]

        for column in cls.__mapper__.local_table.c:

            name = str(column.name)
            if name.startswith('audit'):
                continue

            if name in cls.AUDIT_EXCLUSION_LIST:
                continue

            the_column = copy_column(column)
            audit_cols.append(the_column)

        table_name = f'audit_{cls.__mapper__.local_table.name}'
        meta_data = cls.__mapper__.local_table.metadata
        schema = cls.__mapper__.local_table.schema
        table = Table(table_name, meta_data, *audit_cols, schema=schema)

        class_name = f'Audit{cls.__name__}'
        bases = cls.__mapper__.base_mapper.class_.__bases__
        audit_cls = type.__new__(type, class_name, bases, {})
        audit_cls.__table__ = table
        audit_cls.__mapper__ = mapper(audit_cls, table, OrderedDict())
        cls.Audit = audit_cls

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

class TypeBase(object):

    id = get_id_primarykey()
    added_by = common_columns.get('integer_default')(1)
    added = common_columns.get('datetime_default_now')()
    active = common_columns.get('boolean_default_true')()

    def __repr__(self):
        return f"<{self.id}: {self.name}>"

    @classmethod
    def by_id(cls, attr):
        return DBSession.query(cls). \
                filter(cls.id == attr). \
                first()

    @classmethod
    def get_all(cls, attr):
        return DBSession.query(cls). \
                order_by(desc(getattr(cls, attr))). \
                all()

    @classmethod
    def by_attr_first(cls, attr, value):
        return DBSession.query(cls). \
                filter(getattr(cls, attr)==value). \
                first()

def get_type_table(model_name=None, table_name=None):
    if not model_name or not table_name: return False
    if 'type' in model_name.lower(): return False
    if 'type' in table_name.lower(): return False
    output_table_name = f'tbl_{table_name.lower()}_type'
    output_model_name = f'{model_name}Type'

    primary_id = get_id_primarykey()
    name = common_columns.get('title')()

    type_table_dict = {
            '__tablename__': output_table_name,
            'id': primary_id,
            'name': name,
                       }

    type_table = type(output_model_name, (TypeBase, DeclarativeBase), type_table_dict)
    return type_table

needs_length = ['unicode', 'numeric']

def get_phat_table(model_name=None, columndict={}):
    if not model_name or not columndict: return False
    PhatBase.add_dbsession(DBSession)
    the_class = type(model_name, (PhatBase, DeclarativeBase), columndict)
    the_class.add_auto_audit()
    return the_class
