# -*- coding: utf-8 -*-
"""Home controller module"""
import arrow as arrow
from parse import parse
from tg import predicates, expose, require, redirect, validate, flash, url, request, response, predicates

from cattle_monitor.lib.base import BaseController
from cattle_monitor.lib.crud_utils import ModelForm
from cattle_monitor.lib.endpoint_utils import get_reading_data_history
from cattle_monitor.lib.tg_utils import *
from cattle_monitor.lib.tg_decorators import time_it
import datetime
from cattle_monitor.model import *
from sqlalchemy import func, desc, asc ,  or_
from cattle_monitor.lib.base import BaseController
from cattle_monitor.model import *
from cattle_monitor.controllers.common import CommonController

TIMEOUT_WAIT_IN_MINS = 5
BALANCE_TABLE_NAME = 'tbl_merchant_balance'
HISTORY_TABLE_NAME = 'tbl_transaction_history'
COMMON = CommonController()

class HomeController(BaseController):

###############################################################################
# Dashboard
###############################################################################

    @time_it
    @expose()
    def get_sidebar_html(self, *args, **kwargs):

        nav_items = self.get_nav_items_html()
        usernow = request.identity.get('user', {})
        html = f"""
          <div class="sidebar" data-color="white" data-active-color="danger">
      <div class="logo">
        <a href="" class="simple-text logo-mini">
          <div class="logo-image-small">
            <img src="/img/logo-small.png">
          </div>
          <!-- <p>CT</p> -->
        </a>
        <a class="simple-text logo-normal">
           {usernow.display_name}
        </a>
      </div>
      <div class="sidebar-wrapper">
        		<ul class="nav">
                    {nav_items}
				</ul>
      </div>
    </div>
        """
        javascript = """
        <script>
            var origin = window.location.origin;
            var url = window.location.href.replace(origin, '');
            $('.sidebar-wrapper a').each(function(){
                var href = $(this).attr('href');
                if(href === url){
                    $(this).closest('li').addClass('active');
                    $(this).closest('li').parent().closest('div').addClass('show');
                    $(this).closest('li').parent().closest('li').addClass('active');
                    $(this).closest('li').parent().closest('a').attr('aria-expanded', true);
                };
            });
        </script>
        """
        return html + javascript

    def get_nav_items_html(self, *args, **kwargs):
        nav_items_list = [
            {'destination': '/', 'icon': 'nc-icon nc-bank', 'title': 'Dashboard'},
            {'destination': '/home/config', 'icon': 'nc-icon nc-spaceship', 'title': 'Configurations'},
            {'destination': '/logout_handler', 'icon': 'nc-icon nc-bell-55', 'title': 'Logout'},


        ]
        nav_items = ''
        for item in nav_items_list:
            nav_items += f"""
            <li>
                <a href="{item.get('destination', '/')}">
                    <i class="{item.get('icon','nc nc-university')}"></i>
                    <p>{item.get('title', 'Dashboard')}</p>
                </a>
            </li>
            
            """
        return nav_items

    @require(predicates.not_anonymous())
    def get_home_html(self, *args, **kwargs):
        self.sync_reading_data()

        reading_details = DBSession.query(ReadingData). \
            order_by(ReadingData.added.desc()). \
            first()

        logs_table =self.get_threshold_logs(**kwargs)

        html = f"""
             <div class="row">
          <div class="col-lg-3 col-md-6 col-sm-6">
            <div class="card card-stats">
              <div class="card-body ">
                <div class="row">
                  <div class="col-5 col-md-4">
                    <div class="icon-big text-center icon-warning">
                      <i class="nc-icon nc-globe text-warning"></i>
                    </div>
                  </div>
                  <div class="col-7 col-md-8">
                    <div class="numbers">
                      <p class="card-category">Logs Created</p>
                      <p class="card-title">10<p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card-footer ">
                <hr>
                <div class="stats">
                  <i class="fa fa-refresh"></i>
                  Update Now
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-3 col-md-6 col-sm-6">
            <div class="card card-stats">
              <div class="card-body ">
                <div class="row">
                  <div class="col-5 col-md-4">
                    <div class="icon-big text-center icon-warning">
                      <i class="nc-icon nc-money-coins text-success"></i>
                    </div>
                  </div>
                  <div class="col-7 col-md-8">
                    <div class="numbers">
                      <p class="card-category">Logs Created</p>
                      <p class="card-title">100<p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card-footer ">
                <hr>
                <div class="stats">
                  <i class="fa fa-calendar-o"></i>
                  Last day
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-3 col-md-6 col-sm-6">
            <div class="card card-stats">
              <div class="card-body ">
                <div class="row">
                  <div class="col-5 col-md-4">
                    <div class="icon-big text-center icon-warning">
                      <i class="nc-icon nc-vector text-danger"></i>
                    </div>
                  </div>
                  <div class="col-7 col-md-8">
                    <div class="numbers">
                      <p class="card-category">Errors</p>
                      <p class="card-title">23<p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card-footer ">
                <hr>
                <div class="stats">
                  <i class="fa fa-clock-o"></i>
                 Last updated:  
                </div>
              </div>
            </div>
          </div>
          <div class="col-lg-3 col-md-6 col-sm-6">
            <div class="card card-stats">
              <div class="card-body ">
                <div class="row">
                  <div class="col-5 col-md-4">
                    <div class="icon-big text-center icon-warning">
                      <i class="nc-icon nc-atom text-primary"></i>
                    </div>
                  </div>
                  <div class="col-7 col-md-8">
                    <div class="numbers">
                      <p class="card-category">Connected Monitors</p>
                      <p class="card-title">4<p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="card-footer ">
                <hr>
                <div class="stats">
                  <i class="fa fa-refresh"></i>
               Last updated: 
                </div>
              </div>
            </div>
          </div>
        </div>
        
            <div class="row">
          <div class="col-md-6">
            <div class="card ">
              <div class="card-header ">
                <h5 class="card-title">Heart Rate Statistics</h5>
                <p class="card-category">Collected Data</p>
              </div>
              <div class="card-body ">
                <canvas id="chartjs_pulse"></canvas>
              </div>
              <div class="card-footer ">
          
                <hr>
                <div class="stats">
                  <i class="fa fa-calendar"></i> Last updated:  
                </div>
              </div>
            </div>
          </div>
            <div class="col-md-6">
            <div class="card ">
              <div class="card-header ">
                <h5 class="card-title">Temperature Statistics</h5>
                <p class="card-category">Collected Data</p>
              </div>
              <div class="card-body ">
                <canvas id="chartjs_canvas"></canvas>
              </div>
              <div class="card-footer ">
          
                <hr>
                <div class="stats">
                  <i class="fa fa-calendar"></i>  Last updated: 
                </div>
              </div>
            </div>
          </div>   
          <div class="col-md-6">
            <div class="card ">
              <div class="card-header ">
                <h5 class="card-title">Geolocation of Cattle</h5>
                <p class="card-category">Location tracked</p>
              </div>
              <div class="card-body ">
            <div id="map" style="width:100%; height:400px" class="chart"></div>. 
              </div>
              <div class="card-footer ">
          
                <hr>
                <div class="stats">
                  <i class="fa fa-calendar"></i> Last updated: 
                </div>
              </div>
            </div>
          </div>
          
          
            <div class="col-md-6">
            <div class="card">
              <div class="card-header">
                <h4 class="card-title">Threshold Logs</h4>
              </div>
              <div class="card-body">
               {logs_table}
              </div>
            </div>
          </div>
        </div>
        """
        javacsript = """
        <script>
       
   


            $(document).ready(function(){
            
            
            /**
 * A full list of available request parameters can be found in the Routing API documentation.
 * see:  http://developer.here.com/rest-apis/documentation/routing/topics/resource-calculate-route.html
 */
var routeRequestParams = {
      routingMode: 'fast',
      transportMode: 'truck',
      origin: '40.7249546323,-74.0110042', // Manhattan
      destination: '40.7324386599,-74.0341396', // Newport
      return: 'polyline,travelSummary',
      units: 'imperial',
      spans: 'truckAttributes'
    },
    routes = new H.map.Group();

function calculateRoutes(platform) {
  var router = platform.getRoutingService(null, 8);

  // The blue route showing a simple truck route
  calculateRoute(router, routeRequestParams, {
    strokeColor: 'rgba(0, 128, 255, 0.7)',
    lineWidth: 10
  });

  // The green route showing a truck route with a trailer
  calculateRoute(router, Object.assign(routeRequestParams, {
    'truck[axleCount]': 4,
  }), {
    strokeColor: 'rgba(25, 150, 10, 0.7)',
    lineWidth: 7
  });

  // The violet route showing a truck route with a trailer
  calculateRoute(router, Object.assign(routeRequestParams, {
    'truck[axleCount]': 5,
    'truck[shippedHazardousGoods]': 'flammable'
  }), {
    strokeColor: 'rgba(255, 0, 255, 0.7)',
    lineWidth: 5
  });
}

/**
 * Calculates and displays a route.
 * @param {Object} params The Routing API request parameters
 * @param {H.service.RoutingService} router The service stub for requesting the Routing API
 * @param {mapsjs.map.SpatialStyle.Options} style The style of the route to display on the map
 */
function calculateRoute (router, params, style) {
  router.calculateRoute(params, function(result) {
    addRouteShapeToMap(style, result.routes[0]);
  }, console.error);
}

/**
 * Boilerplate map initialization code starts below:
 */

// set up containers for the map  + panel
var mapContainer = document.getElementById('map');

// Step 1: initialize communication with the platform
// In your own code, replace variable window.apikey with your own apikey
var platform = new H.service.Platform({
  apikey: "q99Md4ZjnRBk99hbZIwP4zVMWuTXXALlfkuyEgSv6cg"
});

var defaultLayers = platform.createDefaultLayers();

// Step 2: initialize a map - this map is centered over Berlin
var map = new H.Map(mapContainer,
  // Set truck restriction layer as a base map
  defaultLayers.vector.normal.truck,{
  center: {lat: 40.745390, lng: -74.022917},
  zoom: 13.2,
  pixelRatio: window.devicePixelRatio || 1
});
// add a resize listener to make sure that the map occupies the whole container
window.addEventListener('resize', () => map.getViewPort().resize());

// Step 3: make the map interactive
// MapEvents enables the event system
// Behavior implements default interactions for pan/zoom (also on mobile touch environments)
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));

map.addObject(routes);

/**
 * Creates a H.map.Polyline from the shape of the route and adds it to the map.
 * @param {Object} route A route as received from the H.service.RoutingService
 */
function addRouteShapeToMap(style, route){
  route.sections.forEach((section) => {
    // decode LineString from the flexible polyline
    let linestring = H.geo.LineString.fromFlexiblePolyline(section.polyline);

    // Create a polyline to display the route:
    let polyline = new H.map.Polyline(linestring, {
      style: style
    });

    // Add the polyline to the map
    routes.addObject(polyline);
    // And zoom to its bounding rectangle
    map.getViewModel().setLookAtData({
      bounds: routes.getBoundingBox()
    });
  });
}

// Now use the map as required...
calculateRoutes (platform);


                $.getJSON('/home/get_today_temperature', function (datalist) {

                    var labels = [];
                    var data = [];
                    for(var idx in datalist){
                        var date = datalist[idx]['date'];
                        var amount = datalist[idx]['temp'];
                        labels.push(date);
                        data.push(amount);
                    };

                    var ctx = document.getElementById('chartjs_canvas').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Temperature',
                                backgroundColor: 'rgba(255, 99, 132, 0)',
                                borderColor: 'rgb(65, 184, 83)',
                                data: data
                            }]
                        },
                        options: {}
                    });
                    return false;
                });
            });
            
              $(document).ready(function(){
                $.getJSON('/home/get_today_pulse', function (datalist) {

                    var labels = [];
                    var data = [];
                    for(var idx in datalist){
                        var date = datalist[idx]['date'];
                        var amount = datalist[idx]['pulse'];
                        labels.push(date);
                        data.push(amount);
                    };

                    var ctx = document.getElementById('chartjs_pulse').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Pulse',
                                backgroundColor: 'rgba(255, 99, 132, 0)',
                                borderColor: 'rgb(65, 184, 83)',
                                data: data
                            }]
                        },
                        options: {}
                    });
                    return false;
                });
            });
            
            
            
            
        </script>
        """
        return html + javacsript


    @expose()
    def get_threshold_logs(self, *args, **kwargs):
        dbase_query = self.get_thresholds_logs(**kwargs)

        outputlist = []
        for item in dbase_query:
            outputlist.append({
                'description': f'<span class="display_link station_edit text-gradient text-primary" data-station_id="{item.id}">{item.name}</span>',
                'created': item.added,
                'value': item.value,
                'active': get_binary_check_or_cross(item.active),
            })
        theadlist = [
            'Name',
            'Value',
            'Created',
            'Active'
        ]
        params = {
            'outputlist': outputlist,
            'theadlist': theadlist,
            'table_id': 'station_table',
            'table_class': 'table-hover',
        }
        javascript = """
            <script>
               
            </script>
            """
        return build_html_table(**params) + javascript


    def get_thresholds_logs(self, paginated=False, *args, **kwargs):
        dbase_query = DBSession.query(ThresholdLogs). \
            filter(ThresholdLogs.active == True)
        if paginated:
            kwargs['query'] = dbase_query
            page = paginate(**kwargs)
            return page

        return dbase_query.all()

    ###############################################################################
# Chartjs Canvas
###############################################################################

    @expose()
    def get_today_chart_html(self, *args, **kwargs):
        html = self.get_chartjs_canvas_html("Today's Sales", 'Hourly earnings')
        javacsript = """
        <script>
            $(document).ready(function(){
                $.getJSON('/home/get_today_datalist', function (datalist) {

                    var labels = [];
                    var data = [];
                    for(var idx in datalist){
                        var date = datalist[idx]['date'];
                        var amount = datalist[idx]['amount'];
                        labels.push(date);
                        data.push(amount);
                    };

                    var ctx = document.getElementById('chartjs_canvas').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Hourly earnings',
                                backgroundColor: 'rgba(255, 99, 132, 0)',
                                borderColor: 'rgb(65, 184, 83)',
                                data: data
                            }]
                        },
                        options: {}
                    });
                    return false;
                });
            });
        </script>
        """
        return html + javacsript

    @expose()
    def get_week_chart_html(self, *args, **kwargs):
        html = self.get_chartjs_canvas_html("This Week's Sales", 'Daily earnings')
        javacsript = """
        <script>
            $(document).ready(function(){
                $.getJSON('/home/get_week_datalist', function (datalist) {

                    var labels = [];
                    var data = [];
                    for(var idx in datalist){
                        var date = datalist[idx]['date'];
                        var amount = datalist[idx]['amount'];
                        labels.push(date);
                        data.push(amount);
                    };

                    var ctx = document.getElementById('chartjs_canvas').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Daily earnings for the week',
                                backgroundColor: 'rgba(255, 99, 132, 0)',
                                borderColor: 'rgb(65, 184, 83)',
                                data: data
                            }]
                        },
                        options: {}
                    });
                    return false;
                });
            });
        </script>
        """
        return html + javacsript

    @expose()
    def get_month_chart_html(self, *args, **kwargs):
        html = self.get_chartjs_canvas_html("This Month's Sales", 'Daily earnings')
        javacsript = """
        <script>
            $(document).ready(function(){
                $.getJSON('/home/get_month_datalist', function (datalist) {

                    var labels = [];
                    var data = [];
                    for(var idx in datalist){
                        var date = datalist[idx]['date'];
                        var amount = datalist[idx]['amount'];
                        labels.push(date);
                        data.push(amount);
                    };

                    var ctx = document.getElementById('chartjs_canvas').getContext('2d');
                    var chart = new Chart(ctx, {
                        type: 'line',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: 'Daily earnings for the month',
                                backgroundColor: 'rgba(255, 99, 132, 0)',
                                borderColor: 'rgb(65, 184, 83)',
                                data: data
                            }]
                        },
                        options: {}
                    });
                    return false;
                });
            });
        </script>
        """
        return html + javacsript

    def get_chartjs_canvas_html(self, time_period='Example Time Period', title='Example Title', *args, **kwargs):
        html = f"""
        <div class="card">
            <div class="card-header">
                <div class="row">
                    <div class="col-sm-7">
                        <div class="numbers pull-left">
                            {time_period}
                        </div>
                    </div>
                    <div class="col-sm-5">
                        <div class="pull-right">
                            <span class="badge badge-pill badge-success">
                                today increase percent
                            </span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="card-body">
                <h6 class="big-title">{title}</h6>
                <canvas id="chartjs_canvas" width="826" height="380"></canvas>
            </div>
            <div class="card-footer">
                <hr>
                <div class="row">
                    <div class="col-sm-7">
                        <div class="footer-title">Financial Statistics</div>
                    </div>
                    <div class="col-sm-5">
                        <div class="pull-right">
                            <button class="btn btn-success btn-round btn-icon btn-sm">
                                <i class="nc-icon nc-simple-add"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        return html

###############################################################################
# Configurations
###############################################################################
    @expose('cattle_monitor.templates.generic')
    @require(predicates.not_anonymous())
    def config(self, *args, **kwargs):
        title = "Threshold Configurations"
        pulse_config = self.get_threshold_pulse(**kwargs)
        temp_config = self.get_threshold_temperature(**kwargs)
        geo_location_config = self.get_threshold_geo_location(**kwargs)
        logs_table = self.get_threshold_logs(**kwargs)

        html = f"""
   <div class="content">
        <div class="row">
          <div class="col-md-4">
          <div id="temp_div">  {temp_config}</div>
 <div id="pulse_div">   {pulse_config}</div>
<div id="geo_div">    {geo_location_config}</div>
            
          </div>
          <div class="col-md-8">
            <div class="card card-user">
              <div class="card-header">
                <h5 class="card-title">Logs Created</h5>
              </div>
              <div class="card-body">
               {logs_table}
              </div>
            </div>
          </div>
        </div>
      </div>
"""
        javascript = """
           
             $('#threshold_edit_save').click(function(){
                var valid = FormIsValid("#threshold_form");
             if(valid){
                var formserial = $('#threshold_form').serialize();
                console.log(formserial);
                
                $.post('/home/save_threshold_values', formserial, function(data){
                    var result = JSON.parse(data);
                    if(result.success === true){
                       
                    };
                    return false;
                });
             }
        });
        
            
        """
        return dict(title=title, html=html, javascript=javascript)



    @expose()
    def get_threshold_pulse(self, *args, **kwargs):
        dbase_query = DBSession.query(ThresholdPulse). \
            filter(ThresholdPulse.active == True)

        reading_details = DBSession.query(ThresholdPulse). \
            order_by(ThresholdPulse.added.desc()). \
            count()
        outputlist = []
        for item in dbase_query:
            outputlist.append({
                'minimum': f'<span class="display_link temp_pulse_edit text-gradient text-primary" data-threshold_id="{item.id}">{item.minimum}</span>',
                'maximum': item.maximum,
                'created': item.added,
                'active': get_binary_check_or_cross(item.active),
            })
        theadlist = [
            'Minimum',
            'Maximum',
            'Created',
            'Active'
        ]
        params = {
            'outputlist': outputlist,
            'theadlist': theadlist,
            'table_id': 'station_table',
            'table_class': 'table-hover',
        }
        temp_config = build_html_table(**params)

        create_new_button = ''

        if (reading_details < 1):
            create_new_button = f"""
                <div class="col-md-6">
                                <button id="new_pulse_config" class="btn btn-primary btn-round">Add</button></div>
                """

        html = f"""
    
                   <div class="card ">
                              <div class="row card-header">
                               <div class="col-md-6">
                                <h5 class="card-title">Pulse Thresholds</h5>
                               </div>
                               {create_new_button}
                              </div>
                              <div class="card-body">
                              {temp_config}
                              </div>
                            </div>
                """
        javascript = """
            <script>
               $("#new_pulse_config").click(function(){
                $('#dialogdiv').load('/home/new_pulse_config?', function(data){
                    return false;
                });
            });
              $(".temp_pulse_edit").click(function(){
                var data = $(this).data();
                $('#dialogdiv').load('/home/new_pulse_config?', data, function(data){
                    return false;
                });
            });
    
                            </script>
                            """
        return html + javascript


    @expose()
    def get_threshold_temperature(self, *args, **kwargs):
        dbase_query = DBSession.query(ThresholdTemperature). \
            filter(ThresholdTemperature.active == True)

        reading_details = DBSession.query(ThresholdTemperature). \
            order_by(ThresholdTemperature.added.desc()). \
            count()
        outputlist = []
        for item in dbase_query:
            outputlist.append({
                'minimum': f'<span class="display_link temp_threshold_edit text-gradient text-primary" data-threshold_id="{item.id}">{item.minimum}</span>',
                'maximum': item.maximum,
                'created': item.added,
                'active': get_binary_check_or_cross(item.active),
            })
        theadlist = [
            'Minimum',
            'Maximum',
            'Created',
            'Active'
        ]
        params = {
            'outputlist': outputlist,
            'theadlist': theadlist,
            'table_id': 'station_table',
            'table_class': 'table-hover',
        }
        temp_config = build_html_table(**params)

        create_new_button = ''

        if(reading_details <1):
            create_new_button = f"""
            <div class="col-md-6">
                            <button id="new_temp_config" class="btn btn-primary btn-round">Add</button></div>
            """

        html = f"""
                    
               <div class="card ">
                          <div class="row card-header">
                           <div class="col-md-6">
                            <h5 class="card-title">Temp Thresholds</h5>
                           </div>
                           {create_new_button}
                          </div>
                          <div class="card-body">
                          {temp_config}
                          </div>
                        </div>
            """
        javascript = """
        <script>
           $("#new_temp_config").click(function(){
            $('#dialogdiv').load('/home/new_temp_config?', function(data){
                return false;
            });
        });
          $(".temp_threshold_edit").click(function(){
            var data = $(this).data();
            $('#dialogdiv').load('/home/new_temp_config?', data, function(data){
                return false;
            });
        });
           
                        </script>
                        """
        return html + javascript

    @expose()
    def get_threshold_geo_location(self, *args, **kwargs):
        dbase_query = DBSession.query(ThresholdLocation). \
            filter(ThresholdLocation.active == True)

        outputlist = []
        for item in dbase_query:
            outputlist.append({
                'lat': f'<span class="display_link station_edit text-gradient text-primary" data-station_id="{item.id}">{item.lat}</span>',
                'lng': item.lng,
                'created': item.added,
                'active': get_binary_check_or_cross(item.active),
            })
        theadlist = [
            'Latitude',
            'Longitude',
            'Created',
            'Active'
        ]
        params = {
            'outputlist': outputlist,
            'theadlist': theadlist,
            'table_id': 'station_table',
            'table_class': 'table-hover',
        }
        geo_config = build_html_table(**params)
        html = f"""
                 
                     <div class="card ">
                          <div class="row card-header">
                           <div class="col-md-6">
                            <h5 class="card-title">Geo Locations</h5>
                           </div><div class="col-md-6">
                            <button type="submit" class="btn btn-primary btn-round">Add</button></div>
                          </div>
                          <div class="card-body">
                          {geo_config}
                          </div>
                        </div>
                 """
        javascript = """
                             <script>

                             </script>
                             """
        return html + javascript


    @expose()
    def get_threshold_geo_location(self, *args, **kwargs):
        dbase_query = DBSession.query(ThresholdLocation). \
            filter(ThresholdLocation.active == True)

        reading_details = DBSession.query(ThresholdLocation). \
            order_by(ThresholdLocation.added.desc()). \
            count()
        outputlist = []
        for item in dbase_query:
            outputlist.append({
                'lng': f'<span class="display_link geo_threshold_edit text-gradient text-primary" data-threshold_id="{item.id}">{item.lng}</span>',
                'lat': item.lat,
                'created': item.added,
                'active': get_binary_check_or_cross(item.active),
            })
        theadlist = [
            'Longitude',
            'Latitude',
            'Created',
            'Active'
        ]
        params = {
            'outputlist': outputlist,
            'theadlist': theadlist,
            'table_id': 'station_table',
            'table_class': 'table-hover',
        }
        temp_config = build_html_table(**params)

        create_new_button = ''

        if (reading_details < 1):
            create_new_button = f"""
                <div class="col-md-6">
                                <button id="new_geo_config" class="btn btn-primary btn-round">Add</button></div>
                """

        html = f"""
    
                   <div class="card ">
                              <div class="row card-header">
                               <div class="col-md-6">
                                <h5 class="card-title">Geo Location</h5>
                               </div>
                               {create_new_button}
                              </div>
                              <div class="card-body">
                              {temp_config}
                              </div>
                            </div>
                """
        javascript = """
            <script>
               $("#new_geo_config").click(function(){
                $('#dialogdiv').load('/home/new_geo_config?', function(data){
                    return false;
                });
            });
              $(".geo_threshold_edit").click(function(){
                var data = $(this).data();
                $('#dialogdiv').load('/home/new_geo_config?', data, function(data){
                    return false;
                });
            });
                            </script>
                            """
        return html + javascript


    @expose()
    def new_geo_config(self, *args, **kwargs):
        threshold_id = kwargs.get('threshold_id', None)
        hidden_input = ''
        card_title = 'New Geo Fencing'
        threshold = None
        lat = ''
        lng = ''
        if threshold_id:
            card_title = 'Edit Geo Fencing'
            threshold = ThresholdLocation.by_id(threshold_id)
            lat = threshold.lat
            lng = threshold.lng
            hidden_input = f"""	<input id="threshold_id" type="hidden" name="threshold_id" value="{threshold_id}" class="form-control" required='true'>"""

        html = f"""
            <div id="geo_modal" class="modal fade" role="dialog">
                <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"> {card_title}</h5>
                        </div>
                        <div class="modal-body text-center">
                            <form id="new_geo_config">
                            {hidden_input}
                              <div class="row">
                        <div class="col-md-6 pr-1">
                          <div class="form-group">
                            <label>Lat</label>
                            <input type="number"  id="lat" name="lat" class="form-control" placeholder="" value={lat}>
                          </div>
                        </div>
                        <div class="col-md-6 pl-1">
                          <div class="form-group">
                            <label>Lng</label>
                            <input type="number" id="lng" name= "lng" class="form-control" placeholder="" value ={lng}>
                          </div>
                        </div>
                      </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button id="close_btn_geo" type="button" class="btn bg-gradient-secondary" data-bs-dismiss="modal">Close</button>
                              <button id='save_threshold_geo' class="btn btn-primary btn-round">Save</button>
                        </div>
                    </div>
                </div>
            </div>
                       """
        javascript = """
                       <script>
                          var form_id = '#new_geo_config'
                    setFormValidation(form_id);
                    $('#save_threshold_geo').click(function(){
                        var valid = FormIsValid(form_id);
                        if(valid){
                            var formserial = $(form_id).serialize();
                            $.post('/home/save_threshold_geo?', formserial, function(data){
                            var result = JSON.parse(data);
    
                                if(result.success === true){
                                    $('#geo_modal').modal('hide');
    
                                      $('#geo_div').load('/home/get_threshold_geo_location', function(){
                                          return false;
                                       })
                                };
                                showNotification(result);
                                return false;
                            });
                        }
                    });
                           $('#close_btn_geo').click(function(){
                               $('#geo_modal').modal('hide');
                           });
                           $('#geo_modal').modal();
                       </script>
                       """
        return html + javascript


    @expose()
    def new_temp_config(self, *args, **kwargs):

        threshold_id = kwargs.get('threshold_id', None)
        hidden_input = ''
        card_title = 'New Temperature Thresholds'
        threshold = None
        maximum =''
        minimum =''
        if threshold_id:
            card_title = 'Edit Temperature Thresholds'
            threshold = ThresholdTemperature.by_id(threshold_id)
            maximum = threshold.maximum
            minimum = threshold.minimum
            hidden_input = f"""	<input id="threshold_id" type="hidden" name="threshold_id" value="{threshold_id}" class="form-control" required='true'>"""

        html = f"""
        <div id="media_modal" class="modal fade" role="dialog">
            <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"> {card_title}</h5>
                    </div>
                    <div class="modal-body text-center">
                        <form id="new_temp_config">
                        {hidden_input}
                          <div class="row">
                    <div class="col-md-6 pr-1">
                      <div class="form-group">
                        <label>Minimum Temperature</label>
                        <input type="number"  id="minimum" name="minimum" class="form-control" placeholder="" value={minimum}>
                      </div>
                    </div>
                    <div class="col-md-6 pl-1">
                      <div class="form-group">
                        <label>Maximum Temperature</label>
                        <input type="number" id="maximum" name= "maximum" class="form-control" placeholder="" value ={maximum}>
                      </div>
                    </div>
                  </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button id="close_btn" type="button" class="btn bg-gradient-secondary" data-bs-dismiss="modal">Close</button>
                          <button id='save_threshold' class="btn btn-primary btn-round">Save</button>
                    </div>
                </div>
            </div>
        </div>
                   """
        javascript = """
                   <script>
                      var form_id = '#new_temp_config'
                setFormValidation(form_id);
                $('#save_threshold').click(function(){
                    var valid = FormIsValid(form_id);
                    if(valid){
                        var formserial = $(form_id).serialize();
                        $.post('/home/save_threshold_temp?', formserial, function(data){
                        var result = JSON.parse(data);
                    
                            if(result.success === true){
                                $('#media_modal').modal('hide');
                          
                                  $('#temp_div').load('/home/get_threshold_temperature', function(){
                                      return false;
                                   })
                            };
                            showNotification(result);
                            return false;
                        });
                    }
                });
                       $('#close_btn').click(function(){
                           $('#media_modal').modal('hide');
                       });
                       $('#media_modal').modal();
                   </script>
                   """
        return html + javascript

    @expose()
    def new_pulse_config(self, *args, **kwargs):

        threshold_id = kwargs.get('threshold_id', None)
        hidden_input = ''
        card_title = 'New Pulse Thresholds'
        threshold = None
        maximum =''
        minimum =''
        if threshold_id:
            card_title = 'Edit Pulse Thresholds'
            threshold = ThresholdPulse.by_id(threshold_id)
            maximum = threshold.maximum
            minimum = threshold.minimum
            hidden_input = f"""	<input id="threshold_id" type="hidden" name="threshold_id" value="{threshold_id}" class="form-control" required='true'>"""

        html = f"""
        <div id="pulse_modal" class="modal fade" role="dialog">
            <div class="modal-dialog modal-dialog-centered modal-lg" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title"> {card_title}</h5>
                    </div>
                    <div class="modal-body text-center">
                        <form id="new_pulse_config">
                        {hidden_input}
                          <div class="row">
                    <div class="col-md-6 pr-1">
                      <div class="form-group">
                        <label>Minimum Pulse</label>
                        <input type="number"  id="minimum" name="minimum" class="form-control" placeholder="" value={minimum}>
                      </div>
                    </div>
                    <div class="col-md-6 pl-1">
                      <div class="form-group">
                        <label>Maximum Pulse</label>
                        <input type="number" id="maximum" name= "maximum" class="form-control" placeholder="" value ={maximum}>
                      </div>
                    </div>
                  </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button id="close_btn" type="button" class="btn bg-gradient-secondary" data-bs-dismiss="modal">Close</button>
                          <button id='save_pulse' class="btn btn-primary btn-round">Save</button>
                    </div>
                </div>
            </div>
        </div>
                   """
        javascript = """
                   <script>
                      var form_id = '#new_pulse_config'
                setFormValidation(form_id);
                $('#save_pulse').click(function(){
                    var valid = FormIsValid(form_id);
                    if(valid){
                        var formserial = $(form_id).serialize();
                        $.post('/home/save_threshold_pulse?', formserial, function(data){
                        var result = JSON.parse(data);
                    
                            if(result.success === true){
                                $('#pulse_modal').modal('hide');
                          
                                  $('#pulse_div').load('/home/get_threshold_pulse', function(){
                                      return false;
                                   })
                            };
                            showNotification(result);
                            return false;
                        });
                    }
                });
                       $('#close_btn').click(function(){
                           $('#pulse_modal').modal('hide');
                       });
                       $('#pulse_modal').modal();
                   </script>
                   """
        return html + javascript



    @expose()
    def save_threshold_temp(self, *args, **kwargs):

        print(kwargs)

        usernow = request.identity.get('user', None)
        threshold_id = kwargs.get('threshold_id', None)
        if not threshold_id:
            this = ThresholdTemperature()
            this.minimum = kwargs.get('minimum', None)
            this.maximum = kwargs.get('maximum', None)
            this.added_by = 1
            DBSession.add(this)
            DBSession.flush()
            return json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully saved data'})
        else:
            this = ThresholdTemperature.by_id(threshold_id)
            if not this: return 'false'
            this.minimum = kwargs.get('minimum', None)
            this.maximum = kwargs.get('maximum', None)
            DBSession.flush()
            return json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully edited data'})
        return  json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully saved data'})

    @expose()
    def save_threshold_geo(self, *args, **kwargs):

        print(kwargs)

        threshold_id = kwargs.get('threshold_id', None)
        if not threshold_id:
            this = ThresholdLocation()
            this.lat = kwargs.get('lat', None)
            this.lng = kwargs.get('lng', None)
            this.added_by = 1
            DBSession.add(this)
            DBSession.flush()
            return json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully saved data'})
        else:
            this = ThresholdLocation.by_id(threshold_id)
            if not this: return 'false'
            this.lat = kwargs.get('lat', None)
            this.lng = kwargs.get('lng', None)
            DBSession.flush()
            return json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully edited data'})
        return  json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully saved data'})

    @expose()
    def save_threshold_pulse(self, *args, **kwargs):

        print(kwargs)

        usernow = request.identity.get('user', None)
        threshold_id = kwargs.get('threshold_id', None)
        if not threshold_id:
            this = ThresholdPulse()
            this.minimum = kwargs.get('minimum', None)
            this.maximum = kwargs.get('maximum', None)
            this.added_by = 1
            DBSession.add(this)
            DBSession.flush()
            return json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully saved data'})
        else:
            this = ThresholdPulse.by_id(threshold_id)
            if not this: return 'false'
            this.minimum = kwargs.get('minimum', None)
            this.maximum = kwargs.get('maximum', None)
            DBSession.flush()
            return json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully edited data'})
        return  json.dumps({'success': True, 'data': this.id, 'status': 'success', 'data':'Successfully saved data'})


    @expose()
    def get_today_temperature(self, *args, **kwargs):

        outputlist = []
        midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        hourlist = [midnight + timedelta(hours=i) for i in range(25)]
        for i, hour in enumerate(hourlist):
            try:
                next_hour = hourlist[i+1]
            except IndexError:
                next_hour = hourlist[i]

            temperature = DBSession.query(ReadingData). \
                    filter(ReadingData.date >= hour). \
                    filter(ReadingData.date <= next_hour). \
                    order_by(ReadingData.added.asc())

          #  temperature_value = temperature
         #   print(temperature_value)
            for x in temperature:
              #  print(x.temperature)
                outputlist.append({
                    'date': hour.strftime('%H:%M'),
                     'temp' : x.temperature,
                })
        return json.dumps(outputlist)

    @expose()
    def get_today_pulse(self, *args, **kwargs):
        usernow = request.identity.get('user', {})
        outputlist = []
        midnight = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        hourlist = [midnight + timedelta(hours=i) for i in range(25)]
        for i, hour in enumerate(hourlist):
            try:
                next_hour = hourlist[i + 1]
            except IndexError:
                next_hour = hourlist[i]


            temperature = DBSession.query(ReadingData). \
                    filter(ReadingData.date >= hour). \
                    filter(ReadingData.date <= next_hour). \
                    order_by(ReadingData.added.asc())

        #    temperature_value = temperature.pulse
         #   print(temperature_value)
            for x in temperature:

                outputlist.append({
                    'date': hour.strftime('%H:%M'),
                     'pulse' : x.pulse,
                })
        return json.dumps(outputlist)




    def sync_reading_data(self, *args, **kwargs):
        usernow = request.identity.get('user', {})
        reading_data_response = get_reading_data_history()


        if not reading_data_response:
            print('DEBUG No data returned')
            return True
        for i in reading_data_response:
            uuid = i.get('_id', None)

            if not uuid:
                continue
            exists = DBSession.query(ReadingData). \
                filter(ReadingData.uuid == uuid). \
                first()



            if not exists:


                arrowObj = arrow.get( i.get("date"))

                # datetime.datetime(2014, 10, 9, 10, 56, 9, 347444, tzinfo=tzoffset(None, -25200))
                tmpDatetime = arrowObj.datetime

                tmpDatetime = tmpDatetime.replace(tzinfo=None)
                print(tmpDatetime)



                this = ReadingData()
                this.added_by = usernow.user_id
                this.added = datetime.now()
                this.uuid = uuid
                this.lat =  i.get("lat")
                this.lng =  i.get("lng")
                this.pulse =  i.get("pulse")
                this.date =tmpDatetime
                #this.date =f'{dt.date()} {time_obj}'

                this.temperature =  i.get("temperature")
                this.active = True
                DBSession.add(this)
                DBSession.flush()
        print('Reading Data Sync Complete')
        return True