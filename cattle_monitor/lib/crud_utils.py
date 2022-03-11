from tg import request
from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Unicode, Table, Boolean, Numeric, VARCHAR
from cattle_monitor.model import *
from cattle_monitor.lib.tg_utils import date_to_str, str_to_date, str_to_datetime, str_to_int
from cattle_monitor.lib.crud_utils_html_soft_ui_bs5 import *

import logging
log = logging.getLogger(__name__)

DEBUG = False

class ModelForm():

    def __init__(self, **kwargs): 

        self.model = kwargs.get('model', None)
        if not self.model:
            log.warning('ModelForm init: No model in kwargs')

        self.record = kwargs.get('record', None)

        self.model_fields = self.__get_model_fields()
        self.required_fields = self.__get_required_fields(**kwargs)
        self.optional_fields = self.__get_optional_fields()
        self.table_name = self.__get_tablename()
        self.excl_fields = self.__get_excluded_fields()

    def __get_model_fields(self):
        if not self.model:
            print('Please provide a model')
            return None
        return self.model.__table__.columns.keys()

    def __get_required_fields(self, **kwargs):
        required_fields = kwargs.get('required_fields', [])
        if self.model_fields:
            for item in self.model_fields:
                column = getattr(self.model, item).property.columns[0]
                if not column.nullable:
                    if item not in required_fields:
                        required_fields.append(item)
        
        return required_fields

    def __get_optional_fields(self):
        optional_fields = []
        if self.model_fields:
            for item in self.model_fields:
                column = getattr(self.model, item).property.columns[0]
                if column.nullable and item not in self.required_fields:
                    optional_fields.append(item)

        return optional_fields

    def __get_tablename(self):
        if self.model:
            table_name = self.model.__table__.name
            if table_name[0:4] == 'tbl_':
                return table_name[4:]
            elif table_name[0:3] == 'tg_':
                return table_name[3:]
            else:
                return None

    def __get_excluded_fields(self):
        excl_fields = ['id','added','added_by','edited','active']
        if self.record:
            excl_fields = ['added','added_by','edited','active']
        return excl_fields

    def __validate_fields(self, **kwargs):

        for item in self.required_fields:
            if item == 'id':
                if item not in kwargs.keys():
                    item = f'{self.table_name}_id'
                if item not in kwargs.keys():
                    continue

            this = kwargs.get(item, None)
            if not this:
                log.warning(f'\n\n{self.table_name} save: No {item} in kwargs\n\n')
                pretty_fieldname = item.replace('_', ' ').title()
                return {'success': False, 'message': f'{pretty_fieldname} is a required field', 'status': 'danger'}

        return {'success': True}

    def __ensure_correct_datatypes(self, **kwargs):
        return_dict = {}
        for k, v in kwargs.items():
            if k not in self.model_fields:
                continue
            
            if k == f"{self.table_name}_id":
                k = 'id'
            
            if not hasattr(self.model, k):
                return {'success': False, 'message':f'{self.table_name} does not have attr: {k}', 'status': 'danger'}
            
            column = getattr(self.model, k).property.columns[0]

            if isinstance(column.type, DateTime) or isinstance(column.type, Date):
                if not v or v == '': continue
                if isinstance(v, str):
                    return_dict[k] = str_to_date(v, dateformat='%Y-%m-%d')
                else:
                    return_dict[k] = v

            elif isinstance(column.type, Integer) or isinstance(column.type, Numeric):
                if not v or v == '': continue
                return_dict[k] = str_to_int(v)
            
            elif isinstance(column.type, Boolean):
                return_dict[k] = True if v == 'on' else False
            
            elif isinstance(column.type, Unicode) or isinstance(column.type, VARCHAR):
                if len(v) > column.type.length:
                    return {'success': False, 'message': f'{k} has too many characters (limit={column.type.length}, provided={len(v)})', 'status': 'danger'}
                return_dict[k] = v.strip()

            else:
                return_dict[k] = v
            
        return return_dict

    def save(self, *args, **kwargs):
        if DEBUG: print('save kwargs', kwargs)
        result = self.__validate_fields(**kwargs)
        if not result.get('success', None):
            return result
        
        this_id = kwargs.get('id', None)
        if not this_id:
            this_id = kwargs.get(f'{self.table_name}_id', None)
        
        this = self.model.by_id(this_id)
        if DEBUG: print('save self.model.by_id(this_id):', this)

        clean_dict = self.__ensure_correct_datatypes(**kwargs)
        if DEBUG: print(clean_dict)
        
        usernow = request.identity.get('user', {})
        if not this:
            this = self.model()
            for k, v in clean_dict.items():
                if DEBUG: print(k, v)
                if k not in self.model_fields:
                    continue
                setattr(this, k, v)
            
            this.active = kwargs.get('active', True)
            this.added = datetime.now()
            this.added_by = usernow.user_id
            DBSession.add(this)
            DBSession.flush()

        else:
            for k, v in clean_dict.items():
                if DEBUG: print(k, v)
                if k not in self.model_fields:
                    continue
                setattr(this, k, v)
                
            DBSession.flush()
        outcome = 'added' if not this else 'updated'
        return {'success': True, 'message': f'Record was successfully {outcome}', 'status': 'success', f'{self.table_name}_id': this.id}

    def get_form(self, *args, **kwargs):
        form_id = kwargs.get('form_id', None)
        if not form_id:
            kwargs['form_id'] = f'{self.table_name}_form'

        kwargs['table_name'] = self.table_name
        kwargs['html_inputs'] = self.get_form_fields(**kwargs)
        return get_form(**kwargs)

    def get_form_fields(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        if fields:
            for field in fields:
                if field not in self.model_fields:
                    log.warning(f'get_form_fields: "{field}" not in model')
                    return ''
            self.model_fields = fields

        html = ''
        for i, col in enumerate(self.model_fields):
            if col not in kwargs.keys():
                if col in self.excl_fields and not fields:
                    continue

            if not col in kwargs.keys():
                kwargs[col] = dict()

            wrapper_class = kwargs.get('wrapper_class', None)
            if not wrapper_class:
                if len(self.model_fields) >= 13:
                    kwargs[col]['wrapper_class'] = 'col-md-6'
            form_type = kwargs.get('form_type', None)
            if form_type:
                kwargs[col]['input_attrs'] = 'disabled'
            
            value = getattr(self.record, col) if self.record else ''
            
            column = getattr(self.model, col).property.columns[0]

            if not isinstance(column, Column): 
                log.warning(f'\n\t column ({column}) is not an instance of a Column')
                continue

            col_name = column.name.lower()
            options = kwargs.get(column.name.lower(), {})
            wrapper_class = options.get('wrapper_class', None)
            if not wrapper_class:
                options['wrapper_class'] = 'col-md-12'

            wrapper_attrs = options.get('wrapper_attrs', None)
            if not wrapper_attrs:
                options['wrapper_attrs'] = '' if not col_name == 'id' else 'hidden'

            options['required'] = 'required' if not column.nullable else ''

            label_val = options.get('label_val', None)
            if not label_val:
                options['label_val'] = column.name.title().replace('_', ' ')

            input_id = options.get('input_id', None)
            if not input_id:
                options['input_id'] = col_name if not col_name == 'id' else f'{self.table_name}_id'

            input_val = options.get('input_val', None)
            if not input_val:
                options['input_val'] = value if value else ''
            
            input_type = kwargs.get('input_type', None)
            if not input_type:
                options['input_type'] = 'text'

            field = ''
            # print('column.type', col, column.type)
            if options.get('field_input_type', None) and options.get('field_input_type') == 'widget':
                html += options.get('widget', '')
                continue
    
            elif isinstance(column.type, Integer) or isinstance(column.type, Numeric):
                field_input_type = options.get('field_input_type', 'number')
                if field_input_type == 'number':
                    options['input_type'] = 'number'
                    field = get_input(**options)

                elif field_input_type == 'select':
                    field = options.get('field', None)
                    if not field:
                        select_model = options.get('select_model', None)
                        options['id'] = options['input_id']
                        options['selected'] = options['input_val']
                        field = get_model_selectbox(select_model, **options)

            elif isinstance(column.type, Unicode) or isinstance(column.type, VARCHAR):
                field_input_type = options.get('field_input_type', 'text')
                max_length = column.type.length

                if field_input_type == 'file':
                    options['input_type'] = 'file'
                    input_attrs = options.get('input_attrs', '')
                    options['input_attrs'] = f'{input_attrs}'
                    options['input_id'] = 'file'
                    field = get_input(**options)
                    # field = get_file_input(**options)

                elif 'email' in col:
                    options['input_type'] = 'email'
                    input_attrs = options.get('input_attrs', '')
                    options['input_attrs'] = f'{input_attrs} maxlength="{max_length}"'
                    field = get_input(**options)
                    
                elif field_input_type == 'number':
                    options['input_type'] = 'number'
                    field = get_input(**options)

                elif max_length < 200 or field_input_type == 'normal':
                    input_attrs = options.get('input_attrs', '')
                    options['input_attrs'] = f'{input_attrs} maxlength="{max_length}"'
                    field = get_input(**options)

                else:
                    options['input_type'] = 'text'
                    options['max_length'] = max_length
                    field = get_textarea(**options)

            elif isinstance(column.type, DateTime) or isinstance(column.type, Date):
                field_input_type = options.get('field_input_type', 'date')

                if field_input_type == 'time': input_val = datetime_to_str(value, dateformat='%H:%M')
                elif field_input_type == 'date': input_val = datetime_to_str(value, dateformat='%Y-%m-%d')
                else: input_val = datetime_to_str(value)
                
                options['input_val'] = input_val
                options['input_type'] = field_input_type

                input_class = options.get('input_class', '')
                options['input_class'] = f'{input_class} datetimepicker'
                field = get_input(**options)

            elif isinstance(column.type, Time):
                options['input_type'] = 'time'
                options['input_val'] = date_to_str(options['input_val'], dateformat='%H: %M')
                field = get_input(**options)

            elif isinstance(column.type, Boolean):
                options['input_type'] = 'checkbox'
                options['input_val'] = 'checked' if value else ''
                html += get_checkbox(**options)
                continue
        
            options['field'] = field
            html += get_input_wrapper(**options)
        
        return html

# Conversion Utils

def datetime_to_str(strdate, dateformat='%d/%m/%Y %H:%M:%S'):
    """ date_to_str """
    if not strdate:
        return None
    try:
        return datetime.strftime(strdate, dateformat)
    except ValueError:
        return None