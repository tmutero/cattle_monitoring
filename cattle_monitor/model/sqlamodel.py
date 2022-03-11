# -*- coding: utf-8 -*-

import os
from datetime import datetime
from hashlib import sha256

from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, Boolean
from sqlalchemy.orm import relation, synonym

from cattle_monitor.model import DeclarativeBase, metadata, DBSession
from cattle_monitor.lib.model_utils import PhatBase, common_columns, get_type_table, get_phat_table




tbl_reading_data = {
    '__tablename__': 'tbl_reading_data',
    'lat': common_columns.get('description')(),
    'lng': common_columns.get('description')(),
    'pulse': common_columns.get('description')(),
    'date': common_columns.get('description')(),
    'temperature': common_columns.get('description')(),
    'uuid': common_columns.get('description')(),
    }
ReadingData = get_phat_table(model_name='ReadingData', columndict=tbl_reading_data)

tbl_threshold_temperature = {
    '__tablename__': 'tbl_threshold_temperature',
    'maximum': common_columns.get('description')(),
    'minimum': common_columns.get('description')(),
    }
ThresholdTemperature = get_phat_table(model_name='ThresholdTemperature', columndict=tbl_threshold_temperature)

tbl_threshold_pulse = {
    '__tablename__': 'tbl_threshold_pulse',
    'maximum': common_columns.get('description')(),
    'minimum': common_columns.get('description')(),
    }
ThresholdPulse = get_phat_table(model_name='ThresholdPulse', columndict=tbl_threshold_pulse)


tbl_threshold_location = {
    '__tablename__': 'tbl_threshold_location',
    'lat': common_columns.get('description')(),
    'lng': common_columns.get('description')(),
    }
ThresholdLocation = get_phat_table(model_name='ThresholdLocation', columndict=tbl_threshold_location)



tbl_threshold_logs = {
    '__tablename__': 'tbl_threshold_logs',
    'name': common_columns.get('description')(),
    'value': common_columns.get('description')(),
    }
ThresholdLogs = get_phat_table(model_name='ThresholdLogs', columndict=tbl_threshold_logs)


