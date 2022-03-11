"""
File: tg_decorators.py
Author: Camilla Buys
Company: Dotxml
email: camilla at dotxmltech dot com
Github: Not yet
"""

# -*- coding: utf-8 -*-
from __future__ import print_function
from tg import request
from functools import wraps
from sqlalchemy.orm.query import Query
from cattle_monitor.model import DeclarativeBase
import time
import os
import logging
import inspect
from inspect import currentframe, getouterframes
#from pylint.epylint import py_run

from tg.predicates import Predicate

LOGGER = logging.getLogger(__name__)

########################
# Python 3 decorators
########################

class CustomNotAnonymous(Predicate):

    message = ''

    def evaluate(self, environ, credentials):
        if not credentials:
            self.unmet()

def cached(func):
    func.cache = {}
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func.cache[str(kwargs)]
        except:
            func.cache[str(kwargs)] = result = func(*args, **kwargs)
            return result
    return wrapper

def time_it(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        funcname = func.__code__.co_name
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        LOGGER.info(f"""
{funcname} ran in {end - start}
        """)
        return result
    return wrapper

def func_logger(func):
    @wraps(func)
    def logger(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        filename = os.path.basename(func.__code__.co_filename)
        lineno = func.__code__.co_firstlineno + 1
        funcname = func.__code__.co_name.upper()
        LOGGER.info(f"""(line {lineno}) {filename} {funcname} ran in {end - start} """)
        return result
    return logger

def func_logger_old(func):
    @wraps(func)
    def logger(*args, **kwargs):
        usernow = request.identity['user']
        argcount = func.__code__.co_argcount
        argnames = func.__code__.co_varnames[:argcount]
        fn_defaults = func.__kwdefaults__ or list()
        argdefs = dict(zip(argnames[-len(fn_defaults):], fn_defaults))

        positional = list(map(format_arg_value, zip(argnames, args)))
        defaulted = [format_arg_value((a, argdefs[a]))
                     for a in argnames[len(args):] if a not in kwargs]
        nameless = list(map(repr, args[argcount:]))
        keyword = list(map(format_arg_value, kwargs.items()))
        all_args = positional + defaulted + nameless + keyword

        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        client_addr = request.client_addr
        remote_addr = request.remote_addr
        filename = os.path.basename(func.__code__.co_filename)
        lineno = func.__code__.co_firstlineno + 1
        funcname = func.__code__.co_name.upper()
        runtime = str(end - start)

        msg = """
Run Time of: {0} lineno:{1} file:{2} is {3} seconds
Client Addr: {4} Remote Addr: {5} User ID: {6}
Input: {7} """.format( funcname,
                       lineno,
                       filename,
                       runtime,
                       client_addr,
                       remote_addr,
                       usernow.id,
                       all_args
                    )
        LOGGER.info(msg)
        return result
    return logger

def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.  """
    arg, val = arg_val
    return "{0}={1}".format(arg, val)

########################
# Python 2 decorators
########################

def pylinter(func):
    """ Use pylint to check code quality """
    @wraps(func)
    def linter(*args, **kwargs):
        """ Internal pylinter """
        filename = func.func_code.co_filename
        py_run(filename)
        return func(*args, **kwargs)
    return linter

def countcalls(func):
    """ Count func calls """
    count = func.count = {}
    @wraps(func)
    def counter(*args, **kwargs):
        """ Internal countcalls """
        caller = getouterframes(currentframe(), 2)[1][3].upper()
        name = func.func_name.upper()
        num = count.get(name, 0)
        num += 1
        count[name] = num
        msg = """COUNTING:{0} caller:{1} count:{2}""".format(name, caller, num)
        LOGGER.info(msg)
        return func(*args, **kwargs)
    return counter

def cache_function(func):
    """ Cache a function """
    cache = func.cache = {}
    @wraps(func)
    def cacher(*args, **kwargs):
        """ Internal cache_function """
        key = '{0}{1}'.format(args[1:], kwargs)
        val = cache.get(key, None)
        status = 'FROM CACHE'
        if not val:
            status = 'CACHING'
            val = func(*args, **kwargs)
            cache[key] = val
        answer = val
        if isinstance(val, (tuple, dict, list)):
            answer = len(val)
        elif isinstance(val, Query):
            answer = len([i for i in val])
        elif isinstance(val, DeclarativeBase):
            answer = val.__tablename__
        answer = '{0} {1}'.format(type(val), answer)
        msg = """{0}:{1} class:{2} key:{3} val:{4}
              """.format(status, func.func_name.upper(),
                         args[0].__class__.__name__, key, answer)
        LOGGER.info(msg)
        return val
    return cacher

def time_function(func):
    """ Times a func """
    @wraps(func)
    def timer(*args, **kwargs):
        """ Internal time_function """
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        #filename = func.func_code.co_filename
        #lineno = func.func_code.co_firstlineno + 1
        #bname = os.path.basename(filename)
        #msg = """Run Time of:{0} line no:{1} file:{2} is {3} seconds
        #      """.format(func.func_name.upper(), lineno, bname, str(end-start))
        msg = f'{func} ran in {end-start} seconds'
        LOGGER.info(msg)
        return result
    return timer

