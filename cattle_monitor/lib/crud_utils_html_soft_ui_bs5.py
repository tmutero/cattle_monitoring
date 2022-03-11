from cattle_monitor.model import *
import logging
log = logging.getLogger(__name__)


def get_form(**kwargs):
    """ usage = get_form(**{
        'table_name': table_name,
        'html_inputs': html_inputs,
        'form_id': form_id,
        'form_class': form_class,
        'form_attrs': form_attrs,
    })
    """
    table_name = kwargs.get('table_name', None)
    if not table_name:
        log.warning('get_html_form: Please supply a table_name')
        return ''
    
    html_inputs = kwargs.get('html_inputs', None)
    if not html_inputs:
        log.warning('get_html_form: Please supply html_inputs')
        return ''

    form_id = kwargs.get('form_id', f'{table_name}_form')
    form_class = kwargs.get('form_class', '')
    form_attrs = kwargs.get('form_attrs', '')
    return f"""
    <form id="{form_id}" class="{form_class}" {form_attrs}>
        {html_inputs}
    </form>
    """

def get_input_wrapper(**kwargs):
    """ usage = get_input_wrapper(**{
        'wrapper_class': wrapper_class,
        'wrapper_attrs': wrapper_attrs,
        'label_class': label_class,
        'input_id': input_id,
        'required': required,
        'label_attrs': label_attrs,
        'label_val': label_val,
        'field': field,
    })
    """
    wrapper_class = kwargs.get('wrapper_class','')
    wrapper_attrs = kwargs.get('wrapper_attrs','')
    label_class = kwargs.get('label_class','')
    input_id = kwargs.get('input_id','')
    required = kwargs.get('required','')
    label_attrs = kwargs.get('label_attrs','')
    label_val = kwargs.get('label_val','')
    field = kwargs.get('field','')
    return f"""
        <div class="{wrapper_class}" {wrapper_attrs}>
            <label class="{label_class}" for="{input_id}" {required} {label_attrs}>{label_val}</label>
            <div class="input-group">
                {field}
            </div>
        </div>
    """

def get_input(**kwargs):
    """ usage = get_input(**{
        'input_id': input_id,
        'input_class': input_class,
        'input_type': input_type,
        'required': required,
        'input_attrs': input_attrs,
        'input_val': input_val,
    })
    """
    input_id = kwargs.get('input_id', '')
    if not input_id:
        log.warning('get_html_input: Please supply an input_id')
        return ''

    input_class = kwargs.get('input_class', '')
    input_type = kwargs.get('input_type', 'text')
    required = kwargs.get('required', '')
    input_attrs = kwargs.get('input_attrs', '')
    input_val = kwargs.get('input_val', '')
    return f"""
        <input id="{input_id}" class="form-control {input_class}" type="{input_type}" 
            name="{input_id}" {required} {input_attrs} value="{input_val}"/>
    """

def get_checkbox(**kwargs):
    """ usage = get_checkbox(**{
        'wrapper_class': wrapper_class,
        'wrapper_attrs': wrapper_attrs,
        'label_class': label_class,
        'label_attrs': label_attrs,
        'label_val': label_val,
        'input_id': input_id,
        'input_attrs': input_attrs,
        'input_val': input_val,
    })
    """
    wrapper_class = kwargs.get('wrapper_class', '')
    wrapper_attrs = kwargs.get('wrapper_attrs', '')
    label_class = kwargs.get('label_class', '')
    label_attrs = kwargs.get('label_attrs', '')
    label_val = kwargs.get('label_val', '')
    input_id = kwargs.get('input_id', '')
    input_attrs = kwargs.get('input_attrs', '')
    input_val = kwargs.get('input_val', '')
    return f"""
        <div class="{wrapper_class}" {wrapper_attrs}>
            <div class="form-group py-2 pl-3 row">
                <div class="form-check">
                    <input id="{input_id}" class="form-check-input" type="checkbox" name="{input_id}" {input_attrs} {input_val}/>
                    <label class="form-check-label {label_class}" for="{input_id}" {label_attrs}>{label_val}</label>
                </div>
            </div>
        </div>
    """

def get_file_input(**kwargs):
    """ usage = get_file_input(**{
        'label_class': label_class,
        'label_val': label_val,
        'input_class': input_class,
        'required': required,
    })
    """
    label_class = kwargs.get('label_class', '')
    label_val = kwargs.get('label_val', 'Choose file')
    input_class = kwargs.get('input_class', '')
    required = kwargs.get('required', '')
    return f"""
        <div class="mb-3">
            <label for="file" class="form-label {label_class}">{label_val}</label>
            <input id="file" class="form-control {input_class}" type="file" name="file" {required}>
        </div>
    """

def get_textarea(**kwargs):
    """ usage = get_textarea(**{
        'input_id': input_id,
        'max_length': max_length,
        'required': required,
        'input_class': input_class,
        'input_val': input_val,
        'input_attrs': input_attrs,
        'row_count': row_count,
    })
    """
    input_id = kwargs.get('input_id', '')
    if not input_id:
        log.warning('get_textarea: No input_id in kwargs')
        return ''

    max_length = kwargs.get('max_length', '')
    if not max_length:
        log.warning('get_textarea: No max_length in kwargs')
        return ''

    required = kwargs.get('required', '')
    input_class = kwargs.get('input_class', '')
    input_val = kwargs.get('input_val', None)
    input_attrs = kwargs.get('input_attrs', '')
    row_count = kwargs.get('row_count', 4)
    return f"""
        <textarea id="{input_id}" class="form-control {input_class}" rows="{row_count}" name="{input_id}" {required} 
            maxlength="{max_length}" {input_attrs}
            >{input_val}</textarea>
    """

def get_model_selectbox(model, **kwargs):
    """ usage = get_model_selectbox(model, **{
        'not_in_list': not_in_list,
        'not_in_id': not_in_id,
        'display_col': display_col,
        'display_id': display_id,

        # create_selectbox_html
        'selectbox_id': selectbox_id,
        'disabled': disabled,
        'selected': selected,
        'required': required,
        'input_attrs': attributes,
        'outputlist': outputlist,
        'class_names': class_names,
        'case_sensitive': case_sensitive,
        'multi_select': multi_select,
        'live_search': live_search,
        'empty_message': empty_message,
    })
    """
    # print('get_model_selectbox kwargs', kwargs)
    if not model:
        return 'No model in options'
    filter_col = kwargs.get('filter_col', None)
    filter_val = kwargs.get('filter_val', None)
    not_in_list = kwargs.get('not_in_list', None)
    not_in_id = kwargs.get('not_in_id', None)
    dbase_query = DBSession.query(model)
    
    if filter_col and filter_val:
        dbase_query = dbase_query.filter(getattr(model, filter_col) == filter_val)

    if not_in_list and not_in_id:
        dbase_query = dbase_query.filter((getattr(model, not_in_id)).notin_(not_in_list))

    dbase_query = dbase_query.all()

    display_col = kwargs.get('display_col', 'name')
    display_id = kwargs.get('display_id', 'id')
    kwargs['outputlist'] = [{'name' : getattr(m, display_col), 'id' : getattr(m, display_id)} for m in dbase_query]
    return create_selectbox_html(**kwargs)

def create_selectbox_html(**kwargs):
    # print('create_selectbox_html', kwargs)
    """ usage = create_selectbox_html(**{
        'selectbox_id': selectbox_id,
        'disabled': disabled,
        'selected': selected,
        'required': required,
        'input_attrs': input_attrs,
        'outputlist': outputlist,
        'class_names': class_names,
        'case_sensitive': case_sensitive,
        'multi_select': multi_select,
        'live_search': live_search,
        'empty_message': empty_message,
    })
    """
    selectbox_id = kwargs.get('id', None)
    disabled = kwargs.get('disabled', None)
    selected = kwargs.get('selected', None)
    required = kwargs.get('required', None)
    input_attrs = kwargs.get('input_attrs', '')
    outputlist = kwargs.get('outputlist', [])
    class_names = kwargs.get('class_names', '')
    required = 'required="true"' if required else ''
    case_sensitive = kwargs.get('case_sensitive', False)

    multi_select = kwargs.get('multi_select', False)
    live_search = kwargs.get('live_search', False)

    if live_search:
        input_attrs += ' data-dropup-auto="false"'

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
            name='{selectbox_id}' {input_attrs} {multi_select} {live_search} {required}>
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
