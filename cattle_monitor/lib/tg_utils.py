# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import os
import json
import random
import locale
import string
import math
import logging
#import requests

from collections import defaultdict
from babel.numbers import format_decimal
from sqlalchemy.inspection import inspect
from pkg_resources import resource_filename
from datetime import datetime, timedelta, date
from xml.etree import ElementTree
from dotenv import dotenv_values

env_vars = dotenv_values()
log = logging.getLogger(__name__)

VAT_RATE = 0.15
LIMIT = 20

###############################################################################
# COMMON HELPERS
###############################################################################

def sort_dict_list(thelist, thekey, reverse=False):
    return sorted(thelist, key=lambda k: k[thekey], reverse=reverse)

def sane_date(strdate):
    """ sane_date """
    if not strdate:
        return None
    try:
        return str_to_date(strdate)
    except TypeError:
        return strdate.date()
    else:
        return None

def add_days_to_date(thisdate, days=0):
    """ add_days_to_date """
    if not thisdate:
        return None
    if type(thisdate) == date:
        return thisdate+timedelta(days=days)
    return None

def first_day_of_month(thisdate):
    """ return the first day of the month in the date """
    if thisdate:
        return None
    if type(thisdate) == date:
        return_date = thisdate.replace(day=1)
        return return_date
    return None

def date_to_datetime(from_date):
    return datetime(from_date.year, from_date.month, from_date.day)

def date_to_start_datetime(from_date):
    return datetime(from_date.year, from_date.month, from_date.day, 0, 0)

def date_to_end_datetime(from_date):
    return datetime(from_date.year, from_date.month, from_date.day, 23, 59)

###############################################################################
# SERVICE HELPERS
###############################################################################

def remove_hash_from_filename(filename, seperator='_'):
    """ remove_hash_from_filename """
    if filename.find(seperator) <= 0: return filename
    if not filename: return None
    filelist = filename.split(seperator)[1:]
    return seperator.join(filelist)

def str_to_float(string):
    """ str_to_float """
    if not string:
        return None
    try:
        return float(string)
    except ValueError:
        return None

def str_to_bool(strbool):
    """ str_to_bool"""
    if strbool in ['1', 1, 'true', 'True']:
        return True
    if strbool in ['0', 0, 'false', 'False']:
        return False
    return None

def str_to_date(strdate, dateformat='%d/%m/%Y'):
    """ str_to_date """
    if not strdate:
        return None
    if type(strdate)==date:
        return strdate
    try:
        return datetime.strptime(strdate, dateformat)
    except ValueError:
        return None

def str_to_datetime(strdate, dateformat='%d/%m/%Y %H:%M:%S'):
    """ str_to_date """
    if not strdate:
        return None
    if type(strdate)==date:
        return strdate
    try:
        return datetime.strptime(strdate, dateformat)
    except ValueError:
        return None

def date_to_str(strdate, dateformat='%d/%m/%Y'):
    """ date_to_str """
    if not strdate:
        return None
    try:
        return datetime.strftime(strdate, dateformat)
    except ValueError:
        return None

def datetime_to_str(strdate, dateformat='%d/%m/%Y %H:%M:%S'):
    """ date_to_str """
    if not strdate:
        return None
    try:
        return datetime.strftime(strdate, dateformat)
    except ValueError:
        return None

def str_to_int(string):
    """ str_to_int """
    if not string:
        return None
    try:
        return int(string)
    except ValueError:
        return None

def get_xml_from_url(url, data=None, datatype=None):
    """ get_content_from_url """
    if not datatype:
        datatype = []
    if not url:
        #print('get_content_from_url NO URL')
        return datatype
    response = None
    try:
        if data:
            response = requests.get(url, data=data)
        else:
            response = requests.get(url)
    except RequestConnectionError:
        #print('get_content_from_url ConnectionError')
        return datatype
    content = {}
    if response:
        try:
            content = response.content
            content = ElementTree.fromstring(content)
            return content.text
        except ValueError:
            return datatype
    #print(content)
    if content.get('status'):
        return content.get('data', datatype)
    return datatype

def get_content_from_url(url, data=None, datatype=None):
    """ get_content_from_url """
    #if not datatype: datatype = []
    #print(data)
    if not url:
        #print('get_content_from_url NO URL')
        return datatype
    response = None
    try:
        if data:
            response = requests.get(url, data=data)
        else:
            response = requests.get(url)
    except RequestConnectionError:
        #print('get_content_from_url RequestConnectionError')
        return datatype
    except NewConnectionError:
        #print('get_content_from_url NewConnectionError')
        return datatype
    content = {}
    if response:
        try:
            content = json.loads(response.content)
        except ValueError:
            return datatype
    #print()
    #print(url)
    #print(content)
    if content.get('status'):
        #print(content.get('data', datatype))
        return content.get('data', datatype)
    return datatype

def post_json_to_url(url, data, datatype=None):
    """ post_json_to_url """
    if not url:
        #print('post_json_to_url NO URL')
        return datatype
    response = None
    try:
        response = requests.post(url, data=data)
    except RequestConnectionError:
        #print('post_json_to_url ConnectionError')
        return datatype
    content = {}
    if response:
        try:
            content = response.content
            content = json.loads(content)
        except ValueError:
            return datatype
    #print()
    #print(url)
    #print(content)
    if content.get('status'):
        #print(content.get('data', datatype))
        return content.get('data', datatype)
    if content.get('success'):
        #print(content.get('tenant', datatype))
        return content.get('tenant', datatype)
    return datatype

###############################################################################
# NEW UTILS
###############################################################################

def get_service_url():
    curpath = os.path.abspath(os.path.curdir)
    FILENAME = os.path.abspath(resource_filename('eiffel_back', 'public'))
    filepath = os.path.join(FILENAME, 'services_url.txt')
    filepath = os.path.join(curpath, 'services_url.txt')
    with open(filepath, 'r') as f:
        url = f.readline()
    if url.startswith('http://'): url = url[7:]
    print(url)
    return url

def get_name_from_enum_id(enum, value):
    """ get_name_from_enum_id """
    try:
        return enum(int(value)).name.replace('_', ' ').title()
    except ValueError:
        return None
    except TypeError:
        return None

def get_id_from_enum_name(enum, name):
    """ get_id_from_enum_name """
    try:
        name = name.title().replace(' ', '_')
        return enum[name].value
    except KeyError:
        return None

def create_radio_html(**kwargs):
    """ create_radio_html """
    classname = kwargs.get('class', None)
    name_key = kwargs.get('name_key', None)
    name_value = kwargs.get('name_value', None)
    id_key = kwargs.get('id_key', None)
    id_value = kwargs.get('id_value', None)
    return f"""
    <div class='form-check form-check-radio'>
        <label class='form-check-label'>
            <input class='form-check-input {classname}'
                   type='radio'
                   name='{classname}'
                   {name_key}='{name_value}'
                   {id_key}='{id_value}'
            >
            <span class='form-check-sign'></span>
        </label>
    </div>
    """

def create_selectbox_html(**kwargs):
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

    disabled_text = ''
    empty_message = kwargs.get('empty_message') if 'empty_message' in kwargs.keys() else 'Select an option...'
    if not outputlist:
        disabled_text = "disabled"
        empty_message = 'No options to select...'
    if disabled:
        disabled_text = 'disabled'

    html = f"""
        <select {disabled_text} class='form-control {class_names}' data-style='form-control' id='{selectbox_id}' name='{selectbox_id}' {attributes} {required}>
            <option value=''>{empty_message}</option>
    """
    for item in outputlist:
        option_attributes = item.get('option_attributes', '')
        if case_sensitive: name = item.get('name', None).replace('_', ' ')
        else: name = item.get('name', None).replace('_', ' ').title()
        if item.get('id') == selected:
            html += f"<option selected='true' {option_attributes} value='{item.get('id')}'>{name}</option>"
        else:
            html += f"<option {option_attributes} value='{item.get('id')}' >{name}</option>"
    html += '</select>'

    return html

def create_boolean_selectbox_html(**kwargs):
    """ Get Boolean selectbox """
    selectbox_id = kwargs.get('id', None)
    selected = kwargs.get('selected', True)
    html = f"""
        <select class='form-control' id='{selectbox_id}' name='{selectbox_id}'>
    """
    if selected:
        html += """ <option value=1 selected="selected">True</option>
                    <option value=0>False</option> """
    else:
        html += """ <option value=1>True</option>
                    <option value=0 selected="selected">False</option> """
    html += '</select>'
    return html

def create_fileinput_html(**kwargs):
    status_dict = {
        'success': 'success',
        'pending': 'info',
        'declined': 'danger'
    }
    label_text = kwargs.get('label_text', 'Choose file...') # the placeholder inside the input
    input_id = kwargs.get('input_id', 'file')
    existing_filename = kwargs.get('existing_filename', None)
    status_label = kwargs.get('status_label', 'pending')
    status = status_dict.get(status_label, 'info')
    required = 'required' if status_label == 'declined' else ''
    html = f"""
        <div class="input-group mb-0">
            <div class="custom-file">
                <input type="file" class="custom-file-input" name="{input_id}" id="{input_id}" {required}>
                <label class="custom-file-label overflow_ellipsis" maxlength="100" for="{input_id}">{label_text}</label>
            </div>
        </div>

    """
    existing_class = f'text-{status}'
    existing_error = '(file rejected, please re submit a new file)' if status_label == 'declined' else f'(status: {status_label})'
    html += f'<p class="mb-0"><small class="{existing_class} font-weight-bold">{existing_filename} {existing_error}</small></p>' if existing_filename else ''
    include_js = kwargs.get('include_js', False)
    max_filesize = kwargs.get('max_filesize', 2)
    if include_js: # if you only need one input, this comes in handy, use the catch all js function in the controller
        html += f"""
        <script>
            $('#{input_id}').on('change', function(e){{
                validateFile('{input_id}', {max_filesize});
                var fileName = e.target.files[0].name;
                $('label[for="{input_id}"]').text(fileName);
                return;
            }});
        </script>
        """
    # catch_all_js = """ # Copy and paste this code into the js of your controller
    # <script>
    #     $(document).on('change','input[type="file"]', function(e){
    #            var thisId = $(this).attr('id');
    #            var result = validateFile(thisId, 5);

    #            var firstFile = e.target.files[0];
    #            var fileName = 'Choose file...'
    #            if (firstFile !== undefined){
    #                console.log(firstFile !== undefined);
    #                fileName = e.target.files[0].name;
    #            }
    #            $('label[for="'+ thisId +'"]').text(fileName);
    #            return;
    #        });
    # </script>
    # """
    return html

###############################################################################
# OLD UTILS
###############################################################################

def ensure_dir(filename):
    """ Ensure dir exists """
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)

def get_divs_package_random(content, divcount=2):
    """ Get divs by divcount """
    rnd = random.random()
    rnd = str(rnd).split('.')[1]
    div_name_some_list = 'div_{0}_parent'.format(rnd)
    div_some_list = """<div id={0}>{1}</div>""".format(div_name_some_list, content)
    if divcount < 2:
        divcount = 2
    div_list = []
    div_name_list = []
    for div in range(1, divcount):
        div_name_list.append('div_{0}_child_{1}'.format(rnd, div))
        div_list.append('<div id={0}></div>'.format(div_name_list[-1]))
    divs = div_some_list + ''.join(div_list)
    style = """
                <style>
                    #{0} {{
                        width : 25%;
                        height: 75vh;
                        float: left;
                        overflow-y: scroll;
                        background: #f2f2f2;
                    }}
                """.format(div_name_some_list)
    divwidth = (75/int(divcount - 1))-1
    for div in range(1, divcount):
        style_tmp = """
                    #{0} {{
                        width : {1}%;
                        height: 75vh;
                        float: left;
                        overflow-y: auto;
                        margin-left: 2px;
                        border-right : 3px dashed grey;
                    }}
                    """.format(div_name_list[int(div) - 1], divwidth)
        style = style + style_tmp
    style = style + '</style>'
    return divs + style

def get_selectbox_bln_text(name, state):
    """ Get Boolean selectbox """
    if state:
        active_txt = """
           <select name='{0}'>
               <option value='1' selected="selected">True</option>
               <option value="0">False</option>
           </select>
           """.format(name)
    else:
        active_txt = """
                   <select name='{0}'>
                       <option value='1'>True</option>
                       <option value="0" selected="selected">False</option>
                   </select>
                   """.format(name)
    return active_txt

def get_selectbox_id_text(name, iter_id, iter_txt, selected):
    """ Get selectbox from iterable """
    top = """
       <select id='{0}' name='{0}'>
       <option value='None' >--Select an option</option>
          """.format(name)
    middle = ""
    for i, itr in enumerate(iter_id):
        if str(i) == selected:
            mid = """ <option value='{0}' selected="selected">{1}</option>
                  """.format(itr, iter_txt[i])
        else:
            mid = """ <option value='{0}'>{1}</option>
                  """.format(itr, iter_txt[i])
        middle = middle + mid
    end = """ </select>"""
    return top + middle + end

def isnumeric(value):
    """ Isnumeric """
    return str(value).replace(".", "").replace("-", "").isdigit()

def checknullvalue(value):
    """ Check if value """
    if not value:
        return 'undefined'
    return str(value)

def get_currency_by_locale(value, the_locale='en_ZA.utf-8', cents=True):
    locale.setlocale(locale.LC_ALL, the_locale)
    if not value:
        return locale.currency(0, grouping=True)
    try:
        value = int(value)
    except:
        return locale.currency(0, grouping=True)
    if cents:
        value = value / 100
    return locale.currency(value, grouping=True)

def getcurrency(value):
    """ Format as Currency """
    if not value:
        return 0
    return format_decimal(value, format='#0.00;-#0.00', locale='en')

def get_vat_amount(amount):
    """ Get vat amount """
    return amount * (1 + VAT_RATE)

def get_month_date_list(months_total=6, dt_start=None):
    """ Get list of month start and end dates """
    if not dt_start:
        dt_start = datetime.date(datetime.now())
    month_date_list = []
    dt_firstday = dt_start.replace(day=1)
    month_date_list.append([dt_firstday, dt_start])
    one_day = timedelta(days=1)
    for _ in range(months_total-1):
        dt_lastday_lastmonth = dt_firstday - one_day
        dt_firstday = dt_lastday_lastmonth.replace(day=1)
        month_date_list.append([dt_firstday, dt_lastday_lastmonth])
    return month_date_list

def get_week_days_list(day_total=7, dt_start=None):
    """ Get list of week start and end dates """
    if not dt_start:
        dt_start = datetime.date(datetime.now())
    week_days_list = []
    week_days_list.append(dt_start)
    for day in range(day_total-1):
        dt_prev = dt_start - timedelta(days=1+day)
        week_days_list.append(dt_prev)
    return week_days_list

def get_month_week_list(week_total=12, dt_start=None):
    """ Get list of week start and end dates """
    if not dt_start:
        dt_start = datetime.date(datetime.now())
    month_weeks_list = []
    dt_firstday = dt_start - timedelta(days=dt_start.weekday())
    for week in range(week_total):
        week_start = dt_firstday - timedelta(days=week*7)
        week_end = week_start + timedelta(days=6)
        month_weeks_list.append([week_start, week_end])
    return month_weeks_list

def build_accordion_html(name='name', iter_list=None, header=None, linkcont='', jslink=''):
    """Usage
        iter_list = [{
                          'link_id':'',
                          'left_label':'',
                          'right_label1':'',
                          'right_label2':'',
                          'right_label3':'',
                          'right_label4':'',
                        }]
        header = [{
                          'left_header':'',
                          'left_header1':'',
                          'right_header':'',


                 }]
        name = accordion_name
        linkcont = 'some/linke/controller/without/kwargs?somearg='
        jslink = 'javascript linking name'
    """
    if not iter_list:
        iter_list = []
    if not header:
        header = []
    html = """<div id="{0}">""".format(name)
    for item in iter_list:
        htmltemp = """ <div class='accord_header'>
                           <h3 link_id={0} {6}='{0}'>{1}
                                <span class='pull-right'>{2}: {3}</span><span class='accord_qty' > {4}:  {5}</span>
                            </h3>
                            <div class='accord_content'></div>
                        <div>
                   """.format(item['link_id'], item['left_label'], item['right_label1'],
                              item['right_label2'], item['right_label3'], item['right_label4'],
                              jslink)
        html = html + htmltemp + "</div></div>"
    for head in header:
        heading = """<h4 class="modal-content">{0}: {1}
                        <span class='pull-right'>{2}</span>
                     </h4>""".format(head['left_header'],
                                     head['left_header1'],
                                     head['right_header'])
    javascript = """
    <script>
            var icons = {{ header: "ui-icon-circle-arrow-e",
                           activeHeader: "ui-icon-circle-arrow-s" }};
            $("#{0}" ) .accordion({{ header: "h3",
                                     heightStyle: 'content',
                                     icons: icons,
                                     active: 'false',
                                     collapsible:'false',
                                     event: 'click',
              }})
              /*
              .sortable({{
                axis: "y",
                handle: "h3",
                collapsible:false,
                stop: function( event, ui ) {{
                  ui.item.children( "h3" ).triggerHandler( "focusout" );
                }}
              }});
              */
            $('#{0} h3').bind('click', function (e) {{
                var this_id = $(this).attr('{2}');
                $(".accord_content").empty();
                $(this).next('div').load("{1}"+this_id, function(responseTxt, statusTxt, xhr){{
                    return false;
                }});
                e.preventDefault();
                e.stopPropagation();
            }});
    </script> """.format(name, linkcont, jslink)
    return  heading + html + "</div>" + javascript

def query_to_list(query_in):
    """ Return: columns name, list of result """
    result = []
    for obj in query_in:
        instance = inspect(obj)
        items = instance.attrs.items()
        result.append([x.value for _, x in items])
    return instance.attrs.keys(), result

def query_to_dict(query_in):
    """ Return: dict of query """
    result = defaultdict(list)
    for obj in query_in:
        instance = inspect(obj)
        for key, val in instance.attrs.items():
            result[key].append(val.value)
    return result

def get_search_generic_dbase_field(**kwargs):
    """Usage
        #thisurl = "/controller/search_some_callback"
        #payload = {'input_element_id': 'old_item',
                    'output_element_id': 'req_item_description',
                    'callback_url': thisurl}
        #search_data = get_search_generic_dbase_field(**payload)

        @expose('jsonp')
        def search_some_callback(self, **kwargs):
            phrase = "%(q)s" % kwargs
            callback = kw['callback']
            searchphrase = "%"+phrase+"%"
            ot = DBS_Session.query(JistSQLTable). \
                    filter(JistItems.description.like(searchphrase)). \
                    order_by(desc(JistItems.id)).limit(50).distinct()
            outerlist = [(k.description) for k in ot]
            descriptionlist = set(outerlist)
            d = json.dumps(list(descriptionlist))
            return callback +'('+d+');'
    """
    input_element_id = kwargs.get('input_element_id', 'input')
    input_name = kwargs.get('input_name', 'Search Items (min 3 characters - max search 50 items) ')
    output_element_id = kwargs.get('output_element_id', 'output')
    output_name = kwargs.get('output_name', 'Output Name')
    callback_url = kwargs.get('callback_url', '')
    html = """ <label for="{0}">{2}</label>
               <input id="{0}"></input><br/>

               <label for="{1}">{3}</label>
               <input id="{1}"></input>
           """.format(input_element_id, output_element_id, input_name, output_name)
    javascript = """
    <style>
        .ui-autocomplete-loading {
            background: white url("/images/ui-anim_basic_16x16.gif") right center no-repeat;
         }
        .ui-autocomplete {
            max-height: 200px;
            overflow-y: auto;
            overflow-x: hidden;
          }
      </style>
      <script>
         var output_width = $("#%s").width();
         $("#%s").css('width', output_width)
          $(function() {
            $( "#%s" ).autocomplete({
              source: function( request, response ) {
                $.ajax({ url: "%s",
                         dataType: "jsonp",
                        data: { q: request.term },
                        success: function( data ) {
                            response( data );
                        }
                });
              },
              minLength: 3,
              select: function( event, ui ) {
                $("#%s").val(ui.item.label);
                $("#%s").focus();
              },
              open: function() {
                $( this ).removeClass( "ui-corner-all" ).addClass( "ui-corner-top" );
              },
              close: function() {
                $( this ).removeClass( "ui-corner-top" ).addClass( "ui-corner-all" );
              }
            });
          });
      </script> """%(output_element_id, input_element_id,
                     input_element_id, callback_url,
                     output_element_id, output_element_id)
    return html + javascript

def dbsafe(incoming):
    """ Replace incoming to be database safe """
    incoming.replace("'", "\'")
    incoming.replace('"', '\"')
    incoming.replace("'\'", "\\")
    incoming.replace("%", r"\%")
    incoming.replace("_", r"\_")
    return incoming

def filenamesafe(filename):
    """ filenamesafe """
    filename.replace(' ', '')
    filename.replace('/', '-')
    return filename

def calculate_panel_sq_m(width_mm=0, height_mm=0, qty=0):
    """ Calculate SQM """
    if not width_mm or not height_mm or not qty:
        return 0
    width_mm = float(width_mm)
    height_mm = float(height_mm)
    qty = float(qty)
    area_m = (width_mm/1000) * (height_mm/1000) * qty
    return area_m

def generate_dates(start_date, end_date):
    """
    start_date = datetime.date(2010, 1, 25)
    end_date = datetime.date(2010, 3, 5)
    generate_dates(start_date, end_date)
    """
    delta = timedelta(hours=24)
    current_date = start_date
    while current_date <= end_date:
        current_date += delta

def format_timedelta(delta):
    """ Format timedelta to string """
    if delta < timedelta(0):
        return '-' + format_timedelta(-delta)
    return str(delta)

def between(early_dt, late_dt, time_now=datetime.now().time()):
    """ Check if dates are between """
    early_time = early_dt.time()
    late_time = late_dt.time()
    if early_time < time_now:
        if time_now < late_time:
            return True
    return False

def get_sweetalert_click(**kwargs):
    supported_types = ['warning', 'success', 'error', 'info', 'question']
    bln_script_tag = kwargs.get('wrap_script', True)
    target_element = kwargs.get('target_element')
    title = kwargs.get('title', None)
    alert_type = kwargs.get('alert_type', 'warning')
    if alert_type not in supported_types: return "Type not Found"
    alert_content = kwargs.get('alert_content', None)
    bln_cancel_button = kwargs.get('cancel_button', True)
    if bln_cancel_button: cancel_toggle = 'true'
    else: cancel_toggle = 'false'
    cancel_color = kwargs.get('cancel_color', '#d33')
    confirm_color = kwargs.get('confirm_color', '#EEA206')
    confirm_text = kwargs.get('confirm_text', 'Ok')
    proceed_target = kwargs.get('proceed_target', None)
    if not proceed_target: return False

    sweetalert = f"""
        $("{target_element}").click(function(){{
            Swal.fire({{
                title: '{title}',
                type: '{alert_type}',
                html: `{alert_content}`,
                showCancelButton: {cancel_toggle},
                cancelButtonColor: '{cancel_color}',
                confirmButtonColor: '{confirm_color}',
                confirmButtonText: '<div id="proceed">{confirm_text}</div>',
                onBeforeOpen: function(){{
                    $('#proceed').click(function(){{
                        $.redirect('{proceed_target}');
                    }});
                }},
            }})
        }});
        """
    if bln_script_tag: return f"<script type='text/javascript'> {sweetalert} </script>"
    else: return sweetalert

def build_html_form(form_id='form_id', params_list=[], form_class=''):
    form_content = build_html_form_inputs(params_list)
    html = f"""
    <form id="{form_id}" class="{form_class}">
        {form_content}
    </form>
    """
    return html

def build_html_form_inputs(params_list=[]):
    form_content = ""
    for item in params_list:
        input_id = item.get('input_id', '') # also the key/name for formserial
        label_attrs = item.get('label_attrs', '') # any settings like for and data attributes go here
        label_val = item.get('label_val', '') # you need css to have the * appear after a required field, see Tanzanite for an example
        label_class = item.get('label_class', '') # controls the 
        input_val = item.get('input_val', '') # value of the input
        input_attrs = item.get('input_attrs', '') # settings like min, max, required, disabled, data attributes go here
        input_type = item.get('input_type', 'text') # number, text, radio, file, hidden etc
        input_field = item.get('input_field', '') # works with input type 'custom', here you can enter anything your heart desires, make sure the content fits
        input_wrapper_class = item.get('input_wrapper_class', '') # d-flex will make multiple inputs stack into one line if their widths allow it
        input_wrapper_attrs = item.get('input_wrapper_attrs', '')
        widget = item.get('widget', '') # any custom element, like div for dynamic content
        if input_type == 'hidden':
            form_content += f"""
            <input id="{input_id}" name="{input_id}" {input_attrs} hidden {input_val}/>
            """
        elif input_type == 'custom':
            form_content += f"""
                <div class="form-group {input_id} {input_wrapper_class}">
                    <label class="{label_class}" for="{input_id}" {label_attrs}>{label_val}</label>
                    {input_field}
                </div>
            """
        elif input_type == 'widget':
            form_content += widget
        else:
            form_content += f"""
                <div class="form-group {input_wrapper_class}" {input_wrapper_attrs}>
                    <label class="" for="{input_id}" {label_attrs}>{label_val}</label>
                    <input type="{input_type}" class="form-control" id="{input_id}" name="{input_id}" {input_attrs} {input_val}/>
                </div>
            """
    return form_content

def build_html_prepend_form(form_id, params_list, show_icon=False):
    form_content = ""
    for item in params_list:
        input_id = item.get('input_id', '') # also the key/name for formserial
        label_attrs = item.get('label_attrs', '') # any settings like for and data attributes go here
        label_val = item.get('label_val', '') # you need css to have the * appear after a required field, see Tanzanite for an example
        input_val = item.get('input_val', '')
        input_attrs = item.get('input_attrs', '') # settings like min, max, required, disabled, data attributes go here
        input_type = item.get('input_type', 'text') # number, text, radio, file, hidden etc
        input_field = item.get('input_field', '') # works with input type 'custom', here you can enter anything your heart desires, make sure the content fits
        input_wrapper_class = item.get('input_wrapper_class', '') # d-flex will make multiple inputs stack into one line if their widths allow it
        input_wrapper_attrs = item.get('input_wrapper_attrs', '') # enables you to hide a entire input with hidden or style="display:none;" for animations
        fa_icon = item.get('fa_icon', '') # font awesome icons https://fontawesome.com/icons?d=gallery&m=free
        widget = item.get('widget', '') # any custom element, like div for dynamic content
        prepend_icon = ''
        if show_icon:
            prepend_icon = f"""
            <div class="input-group-prepend">
                <span class="input-group-text">
                    <i class="{fa_icon}"></i>
                </span>
            </div>
            """

        if input_type == 'hidden':
            form_content += f"""
            <input id="{input_id}" name="{input_id}" {input_attrs} hidden {input_val}/>
            """
        elif input_type == 'custom':
            form_content += f"""
                <div class="form-group {input_id} {input_wrapper_class}" {input_wrapper_attrs}>
                    <div class="input-group input-group-alternative">
                        {prepend_icon}
                        {input_field}
                    </div>
                </div>
            """
        elif input_type == 'widget':
            form_content += widget
        else:
            form_content += f"""
                <div class="form-group {input_wrapper_class}" {input_wrapper_attrs}>
                    <div class="input-group input-group-alternative">
                        {prepend_icon}
                        <input type="{input_type}" class="form-control" id="{input_id}" name="{input_id}" {input_attrs} {input_val}/>
                    </div>
                </div>
            """
    html = f"""
    <form id="{form_id}">
        {form_content}
    </form>
    """
    return html

def create_checkbox_html(**kwargs):
    check_value = str_to_bool(kwargs.get('value', False))
    label_text = kwargs.get('label_text', '') # the label on the right side of the checkbox
    input_id = kwargs.get('input_id', 'check')
    checked = 'checked' if check_value == True else ''
    return f"""
        <div class="form-check">
            <label class="form-check-label">
                <input id="{input_id}" class="form-check-input" type="checkbox" name="{input_id}" {checked}>
                <span class="form-check-sign"></span>
                {label_text}
            </label>
        </div>
    """
def get_binary_check_or_cross(**kwargs):
    value = kwargs.get('value', False)
    if value:
        return '<i class="fa fa-check text-success ml-2 mt-2" aria-hidden="true"></i>'
    else:
        return '<i class="fa fa-times text-danger ml-2 mt-2" aria-hidden="true"></i>'

def kwargs_valitator(key_list=None, **kwargs):
    if not key_list: return {'success': False}
    for key in key_list:
        this = kwargs.get(key, None)
        if not this:
            print(f'DEBUG: NO {key}')
            key = key.title()
            return {'success': False, 'message': f'{key} needs to be completed'}
    return {'success': True}

def get_random_string(length=16, *args, **kwargs):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def get_binary_check_or_cross(value=False):
    # Font Awesome Icons
    if value:
        return '<i class="fa fa-check text-success ml-2 mt-2" aria-hidden="true"></i>'
    else:
        return '<i class="fa fa-times text-danger ml-2 mt-2" aria-hidden="true"></i>'

def build_html_table(**kwargs):
    """ build_html_table """
    outputlist = kwargs.pop('outputlist', [])
    dbcolumnlist = kwargs.pop('dbcolumnlist', [])
    theadlist = kwargs.pop('theadlist', [])
    table_id = kwargs.pop('table_id', 'table_id')
    table_class = kwargs.pop('table_class', 'table-hover')
    table_attrs = kwargs.pop('table_attrs', '')
    tdclasslist = kwargs.pop('tdclasslist', None)
    trclass = kwargs.pop('trclass', '')

    html = f"<div class='table-responsive'><table id='{table_id}' class='table {table_class}' {table_attrs}>"
    if theadlist:
        html += '<thead><tr>'
        for i, head in enumerate(theadlist):
            classname = tdclasslist[i] if tdclasslist else ''
            html += f'<th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 {classname}">{head}</th>'
    
        html += "</tr></thead>"

    html += "<tbody>"
    row_class = f"class='{trclass}'"
    
    if outputlist:
        for row in outputlist:
            html += f'<tr {row_class}>'
            dbcolumnlist = dbcolumnlist if dbcolumnlist else list(row.keys())
            for i, _ in enumerate(dbcolumnlist):
                value = row[dbcolumnlist[i]]
                classname = f"class='{tdclasslist[i]}'" if tdclasslist else ''
                html += f'<td {classname}>{value}</td>'
            html += '</tr>'
    
    if not outputlist:
        html += f'''
            <tr>
                <td colspan="{len(theadlist) + 1}" 
                    class="noRecords text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 px-4">
                    No records found...
                </td>
            </tr>
        '''

    html += "</tbody></table></div>"
    return html

def build_paginated_html_table(**kwargs):
    """ build_paginated_html_table """
    outputlist = kwargs.pop('outputlist', [])
    dbcolumnlist = kwargs.pop('dbcolumnlist', [])
    theadlist = kwargs.pop('theadlist', [])
    table_id = kwargs.pop('table_id', 'table_id')
    table_class = kwargs.pop('table_class', 'table-hover')
    tdclasslist = kwargs.pop('tdclasslist', None)
    trclass = kwargs.pop('trclass', '')

    html = f"<div class='table-responsive'><table class='table {table_class} align-items-center mb-0' id='{table_id}'>"
    if theadlist:
        html += '<thead><tr>'
        for i, head in enumerate(theadlist):
            classname = tdclasslist[i] if tdclasslist else ''
            html += f'<th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 {classname}">{head}</th>'
    
        html += "</tr></thead>"

    html += "<tbody>"
    row_class = f"class='{trclass}'"
    
    if outputlist:
        for row in outputlist:
            html += f'<tr {row_class}>'
            dbcolumnlist = dbcolumnlist if dbcolumnlist else list(row.keys())
            for i, _ in enumerate(dbcolumnlist):
                value = row[dbcolumnlist[i]]
                classname = f"class='{tdclasslist[i]}'" if tdclasslist else ''
                html += f'<td {classname}>{value}</td>'
            html += '</tr>'
    
    if not outputlist:
        html += f'''
            <tr>
                <td colspan="{len(theadlist) + 1}" 
                    class="noRecords text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 px-4"
                    >No records found...
                </td>
            </tr>'''
    html += "</tbody></table></div>"

    pagination = ''
    if outputlist:
        pagination = set_pagination_html(**kwargs)
    return html + pagination

def paginate(**kwargs):
    debug = False
    if debug:
        print()
        print('DEBUG paginate kwargs', kwargs)
        print()

    query = kwargs.get('query', [])
    if not query:
        if debug: print('DEBUG pagination query not present in kwargs')

    page = kwargs.get('page', 1)
    if not page:
        if debug: print('DEBUG pagination page not present in kwargs')

    page_size = str_to_int(kwargs.get('page_size', LIMIT))
    if not page_size:
        if debug: print('DEBUG pagination page_size not present in kwargs')


    if not query: return {'success': False, 'message': 'No query present.', 'status': 'danger'}
    if page <= 0: return {'success': False, 'message': 'Page cannot be 0 or less.', 'status': 'danger'}
    if page_size <= 0: return {'success': False, 'message': 'Page size cannot be 0 or less.', 'status': 'danger'}

    items = query.limit(page_size).offset((page - 1) * page_size).all()
    total = query.order_by(None).count()

    has_previous = page > 1
    previous_page = page - 1 if has_previous else None

    previous_items = (page - 1) * page_size
    has_next = previous_items + len(items) < total
    next_page = page + 1 if has_next else None

    pages = int(math.ceil(total / float(page_size)))

    return {
        'success': True,
        'items': items,
        'total': total,
        'current_page': page,
        'pages': pages,
        'has_previous': has_previous,
        'previous_page': previous_page,
        'has_next': has_next,
        'next_page': next_page,
    }

def set_pagination_html(**kwargs):
    debug = False
    if debug:
        print()
        print('DEBUG set_pagination_html kwargs', kwargs)
        print()

    page_size_div = kwargs.get('page_size_div', '#pageSizeDiv')

    table_wrapper_id = kwargs.get('table_wrapper_id', '#tableDiv')
    refresh_target = kwargs.get('refresh_target', '')
    page = kwargs.get('page', {})
    current_page = page.get('current_page', 1)
    total_pages = page.get('pages', 1)
    size_list = kwargs.get('size_list', '5,10,20,50,100')
    size_list = size_list.split(',')
    page_size = kwargs.get('page_size', '10')
    options = ""
    for n in size_list:
        selected = 'selected="true"' if int(n) == int(page_size) else ''
        options += f"<option {selected} value='{n}'>{n}</option>"

    html = f"""
        <div class="col-md-12">
            <div class="row mt-4 d-flex align-items-center">
                <span id="pageSizeDiv">
                    <span class="page-size d-flex align-items-center">
                        <span> Show </span>
                            <select class="selectpicker form-control mx-2" data-style="form-control" id="pageSizeSelect" name="pageSizeSelect">
                                {options}
                            </select>
                        <span class="text-nowrap"> per page </span>
                    </span>
                </span>
                <ul id="pagination" class="pagination ml-auto mb-0" data-table_wrapper_id="{table_wrapper_id}"
                    data-current_page="{current_page}" data-total_pages="{total_pages}" data-refresh_target="{refresh_target}"
                    data-page_size_div="{page_size_div}" data_size_list="{size_list}">
                </ul>
            </div>
        </div>
    """
    # Docs http://josecebe.github.io/twbs-pagination/#options-and-events
    javascript = f"""
    <script>
        (function($){{
            var tableWrapperId = '{table_wrapper_id}';
    """
    javascript += """
            var pagination = $(tableWrapperId + ' #pagination');
            var data = $(pagination).data();
            var kwargs = $(tableWrapperId).data();
            kwargs['width'] = $(window).width();
            pagination.twbsPagination({
                totalPages: data.total_pages,
                initiateStartPageClick:false,
                hideOnlyOnePage:false,
                visiblePages: 4,
                startPage: data.current_page,
                prev: '<span aria-hidden="true">&laquo;</span>',
                next: '<span aria-hidden="true">&raquo;</span>',
                first: '',
                last: '',
                onPageClick: function (event, page) {
                    kwargs['page'] = page;
                    $(tableWrapperId).load(data.refresh_target, kwargs);
                    return false;
                }
            });

            $(tableWrapperId + ' #pageSizeSelect').change(function(){
                $(tableWrapperId).data('page_size', $(this).val());
                kwargs['page'] = 1;
                $(tableWrapperId).load(data.refresh_target, kwargs);
                return false;
            });
            $(tableWrapperId + " .selectpicker").selectpicker({
                width: 'fit',
                tickIcon: "ui-1_check",
                iconBase: "now-ui-icons",
                dropdownAlignRight: 'auto',
            });
        })(jQuery);
    </script>
    """
    return html + javascript

def build_accordion_html_table(**kwargs):
    """ build_accordion_html_table """
    outputlist = kwargs.pop('outputlist', [])
    dbcolumnlist = kwargs.pop('dbcolumnlist', [])
    theadlist = kwargs.pop('theadlist', [])
    table_id = kwargs.pop('table_id', 'table_id')
    table_class = kwargs.pop('table_class', '')
    tdclasslist = kwargs.pop('tdclasslist', None)
    trclass = kwargs.pop('trclass', '')
    custom_toggle = kwargs.pop('custom_toggle', False)

    html = f"<div class='table-responsive'><table class='table {table_class}' id='{table_id}'>"
    if theadlist:
        html += '<thead>'
        for i, head in enumerate(theadlist):
            classname = tdclasslist[i] if tdclasslist else ''
            html += f'<th class="text-uppercase text-secondary text-xxs font-weight-bolder opacity-7 {classname}">{head}</th>'
    
        html += "</thead>"

    html += "<tbody>"
    if outputlist:
        for n, row in enumerate(outputlist):
            trigger_attrs = ''
            accord_content = row.pop('accord_content', None)
            if accord_content:
                trigger_attrs = accord_content.get('trigger_attrs', '')

            # html += f'<tr class="accordion-toggle collapsed" id="accordion{n}" data-toggle="collapse" data-parent="#accordion{n}" href="#collapse{n}">'
            html += f"""
                <tr class="accordion-toggle collapsed" id="accordion{n}" data-parent="#accordion{n}" 
                    data-url="collapse{n}" {trigger_attrs}>
            """

            dbcolumnlist = dbcolumnlist if dbcolumnlist else list(row.keys())
            cell_count = 0
            for i, _ in enumerate(dbcolumnlist):
                value = row[dbcolumnlist[i]]
                colspan = ''
                if cell_count > 0:
                    cell_count -= 1
                    continue
                if 'colspan' in value:
                    soup = bs(value, 'html.parser')
                    attr_dict = soup.find().attrs
                    if 'colspan' in attr_dict.keys():
                        colspan_val = attr_dict['colspan']
                        colspan = f'colspan="{colspan_val}"'
                        cell_count = int(colspan_val) - 1
                classname = f"class='{tdclasslist[i]}'" if tdclasslist else ''
                html += f'<td {colspan} {classname}>{value}</td>'
            html += '</tr>'
            html += f"""
                <tr class="hide-table-padding">
                    <td colspan="{len(list(row.keys()))}">
                        <div id="collapse{n}" class="collapse"></div>
                    </td>
                </tr>"""
    
    if not outputlist:
        html += f'<tr><td colspan="{len(theadlist) + 1}" class="noRecords">No records found...</td></tr>'
    html += "</tbody></table></div>"

    javascript = ""
    if not custom_toggle:
        javascript = """
        <script>
            $('.accordion-toggle').click(function(){
                var data = $(this).data();
                var thisAccord = $('#'+ data.url);
                thisAccord.load(data.load_target, data, function(){
                    $('#'+ data.url).collapse('toggle');
                });
            });
        </script>
        """
    return html + javascript

