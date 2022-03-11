from tg import request
from sqlalchemy import Column, Integer, String, DateTime, Date, Unicode, Table, Boolean, Numeric, VARCHAR, Time
from cattle_monitor.model import *
from cattle_monitor.lib.tg_utils import date_to_str, datetime_to_str, str_to_date, str_to_datetime, str_to_int

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
        print('save kwargs', kwargs)
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
        return {'success': True, 'message': f'{self.model} saved successfully', 'status': 'success', f'{self.table_name}_id': this.id}

    def get_form(self, *args, **kwargs):
        form_id = kwargs.get('form_id', f'{self.table_name}_form')
        form_class = kwargs.get('form_class', '')
        html = self.get_form_fields(**kwargs)
        return f"""
        <form id="{form_id}" class="{form_class}">
            {html}
        </form>
        """

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
            wrapper_class = options.get('wrapper_class', 'col-md-12')
            wrapper_attrs = options.get('wrapper_attrs', None)
            if not wrapper_attrs:
                wrapper_attrs = '' if not col_name == 'id' else 'hidden'
            required = 'required' if not column.nullable else ''
            label_val = options.get('label_val', column.name.title().replace('_', ' '))
            label_class = options.get('label_class', '')
            label_attrs = options.get('label_attrs', '')
            input_id = options.get('input_id', None)
            if not input_id:
                input_id = col_name if not col_name == 'id' else f'{self.table_name}_id'
            input_attrs = options.get('input_attrs', '')
            # input_wrapper_class = options.get('input_wrapper_class', '')
            input_val = options.get('input_val', None)

            if not input_val:
                input_val = value if value else ''
            elif input_val:
                input_val = value if value else input_val

            input_class = options.get('input_class', '')
            input_type = kwargs.get('input_type', None)
            if not input_type:
                input_type = 'text'

            field = ''
            # print('column.type', col, column.type)
            if options.get('field_input_type', None) and options.get('field_input_type') == 'widget':
                html += options.get('widget', '')
                continue
    
            elif isinstance(column.type, Integer) or isinstance(column.type, Numeric):
                field_input_type = options.get('field_input_type', 'number')
                if field_input_type == 'number':
                    field = f'<input id="{input_id}" class="form-control {input_class}" type="number" name="{input_id}" {required} {input_attrs} value="{input_val}"/>'
                elif field_input_type == 'select':
                    field = options.get('field', None)
                    if not field:
                        select_model = options.get('select_model', None)
                        if not select_model:
                            field = 'No model in options'
                        options['id'] = input_id
                        options['selected'] = input_val
                        options['required'] = required 
                        options['attributes'] = input_attrs 
                        field = self.get_model_selectbox(select_model, **options)

            elif isinstance(column.type, Unicode) or isinstance(column.type, VARCHAR):
                field_input_type = options.get('field_input_type', 'text')
                max_length = column.type.length

                if field_input_type == 'file':
                    field = f'<input id="file" class="form-control {input_class}" type="file" name="file" {required}/>'
                elif 'email' in col:
                    field = f'<input id="{input_id}" class="form-control {input_class}" type="email" name="{input_id}" {required} maxlength="{max_length}" {input_attrs} value="{input_val}"/>'
                elif field_input_type == 'number':
                    field = f'<input id="{input_id}" class="form-control {input_class}" type="number" name="{input_id}" {required} {input_attrs} value="{input_val}"/>'
                elif max_length < 200 or field_input_type == 'normal':
                    field = f'<input id="{input_id}" class="form-control {input_class}" type="text" name="{input_id}" {required} maxlength="{max_length}" {input_attrs} value="{input_val}"/>'
                else:
                    field = f'<textarea id="{input_id}" class="form-control {input_class}" rows="4" name="{input_id}" {required} maxlength="{max_length}" {input_attrs}>{input_val}</textarea>'

            elif isinstance(column.type, DateTime) or isinstance(column.type, Date):
                input_type = options.get('input_type', 'date')
                
                if input_type == 'time': input_val = datetime_to_str(input_val, dateformat='%H:%M')
                elif input_type == 'date': input_val = datetime_to_str(input_val, dateformat='%Y-%m-%d')
                else: datetime_to_str(input_val)
                field = f'<input id="{input_id}" class="form-control datetimepicker {input_class}" type="{input_type}" name="{input_id}" {input_attrs} value="{input_val}"/>'
            
            elif isinstance(column.type, Time):
                input_type = options.get('input_type', 'time')
                field = f'<input id="{input_id}" class="form-control {input_class}" type="{input_type}" name="{input_id}" {input_attrs} value="{input_val}"/>'

            elif isinstance(column.type, Boolean):
                input_type = kwargs.get('input_type', 'checkbox')
                input_val = 'checked' if value else ''
                html += f"""
                    <div class="{wrapper_class}" {wrapper_attrs}>
                        <div class="form-group py-2 pl-3">
                            <div class="form-check">
                                <input id="{input_id}" class="form-check-input" type="{input_type}" name="{input_id}" {input_attrs} {input_val}/>
                                <label class="form-check-label {label_class}" for="{input_id}" {label_attrs}>{label_val}</label>
                            </div>
                        </div>
                    </div>
                """
                continue

            html += f"""
                <div class="{wrapper_class}" {wrapper_attrs}>
                    <label class="{label_class}" for="{input_id}" {required} {label_attrs}>{label_val}</label>
                    <div class="input-group">
                        {field}
                    </div>
                </div>
            """
            
        return html
        # for item in dir(thisuser.__class__):
        #     try:
        #         print(item, getattr(thisuser, item), type(getattr(thisuser, item)))
        #     except AttributeError:
        #         continue

    def get_model_selectbox(self, model, **kwargs):
        # print('get_model_selectbox kwargs', kwargs)
        not_in_list = kwargs.get('not_in_list', None)
        not_in_id = kwargs.get('not_in_id', None)
        dbase_query = DBSession.query(model)
        
        if not_in_list and not_in_id:
            dbase_query = dbase_query.filter((getattr(model, not_in_id)).notin_(not_in_list))

        dbase_query = dbase_query.all()

        display_col = kwargs.get('display_col', 'name')
        display_id = kwargs.get('display_id', 'id')
        kwargs['outputlist'] = [{'name' : getattr(m, display_col), 'id' : getattr(m, display_id)} for m in dbase_query]
        return self.create_selectbox_html(**kwargs)

    def create_selectbox_html(self, **kwargs):
        # print('create_selectbox_html kwargs', kwargs)
        """ create_selectbox_html """
        selectbox_id = kwargs.get('id', None)
        disabled = kwargs.get('disabled', None)
        selected = kwargs.get('selected', None)
        required = kwargs.get('required', None)
        attributes = kwargs.get('attributes', '')
        outputlist = kwargs.get('outputlist', [])
        class_names = kwargs.get('class_names', '')
        required = 'required="true"' if required else ''
        case_sensitive = kwargs.get('case_sensitive', False)

        multi_select = kwargs.get('multi_select', False)
        live_search = kwargs.get('live_search', False)

        if live_search:
            attributes += ' data-dropup-auto="false"'

        multi_select = 'multiple' if multi_select else ''
        live_search = 'data-live-search="true"' if live_search else ''

        disabled_text = ''
        empty_message = kwargs.get('empty_message', 'Choose item...')
        if not outputlist:
            disabled_text = "disabled"
            empty_message = 'No options to select...'
        if disabled:
            disabled_text = 'disabled'

        html = f"""
            <select {disabled_text} class='selectpicker form-control {class_names}' data-style='form-control' id='{selectbox_id}' 
                name='{selectbox_id}' {attributes} {multi_select} {live_search} {required}>
        """
        if not multi_select:
            html += f"""
                <option value=''>{empty_message}</option>
            """

        for item in outputlist:
            option_attributes = item.get('option_attributes', '')

            if case_sensitive: 
                name = item.get('name', None).replace('_', ' ')
            else: 
                name = item.get('name', None).replace('_', ' ').title()

            if item.get('id') == selected:
                html += f"<option selected='true' {option_attributes} value='{item.get('id')}'>{name}</option>"
            else:
                html += f"<option {option_attributes} value='{item.get('id')}' >{name}</option>"
        html += '</select>'

        javascript = """
        <script>
            $(document).ready(function(){
                $(".selectpicker").selectpicker({
                //width: 'auto',
                tickIcon: "fa-check",
                iconBase: "fas",
                dropdownAlignRight: 'auto',
                });
            });
        </script>
        """
        return html

# ~~ Classy End ~~
