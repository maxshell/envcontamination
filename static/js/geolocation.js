// Constants
ACCURACE = 2000;
MAP_ZOOM = 12;
OPACITY = 0;
// Kyiv by default
DEFAULT_LAT = 50.457941;
DEFAULT_LNG = 30.524139;
// Math calculations
// Degrees to radians 
D2R = Math.PI / 180; 
// Radians to degrees
R2D = 180 / Math.PI;
// Earth radius
EARTH_RADIUS = 6378100;
MIN_ANGLE=0;
MAX_ANGLE=360;
MULTIPLIER=1000;
// Storage keys
LAT_STORED="DEFAULT_LAT";
LNG_STORED="DEFAULT_LNG";
TAB_STORED="DEFAULT_TAB";
// Presentation coefficients
WINDS=[{w:0.5, a:360}, {w:1, a:180}, {w:2, a:90}, {w:Number.POSITIVE_INFINITY, a:45}];
ZOOMS=[{r:300, z:16}, {r:900, z:15}, {r:1600, z:14}, {r:3200, z:13},
       {r:6200, z:12}, {r:13000, z:11}, {r:24000, z:10}, {r:50000, z:9},
       {r:90000, z:8}, {r:180000, z:7}, {r:Number.POSITIVE_INFINITY, z:6}];
STROKES=[{c:"red", w:2}, {c:"blue", w:3}, {c:"black", w:4}];
TIMES=[1, 3];
COUNT=3;
// Callback constants
ANGLE_CALLBACKS=[{a:360, c:drawCircle}, {a:0, c:drawSector}];
GEO_MESSAGES_PANEL_TIMEOUT=5000;
// Selectors
MAP_SELECTOR="geo";
GEO_MESSAGES_PANEL_SELECTOR="#geo-messages-panel";
GEO_MESSAGE_HOLDER_SELECTOR="#geo-message-holder";
RESULTS_SELECTORS=["#firstZone", "#secondZone", "#finalZone"];
RESULT_PANEL_SELECTOR="#resultsPanel";
TABS_SELECTOR="#tabs";

function initializeMap() {
  geocoder = new google.maps.Geocoder();
  latlng = new google.maps.LatLng(DEFAULT_LAT, DEFAULT_LNG);
  mapOptions = {
    zoom: MAP_ZOOM,
    mapTypeId: google.maps.MapTypeId.ROADMAP,
    center : latlng
  };
  map = new google.maps.Map(document.getElementById(MAP_SELECTOR), mapOptions);
  markerOptions = {
    map: map,
    position : latlng
  };
  marker = new google.maps.Marker(markerOptions);
  circleOptions = {
    map: map,
    fillOpacity: OPACITY
  };
  polyLineOptions = {
    map: map 
  };
  circles=[];
  polyLines=[];
  for(var i=0;i<COUNT;i++) {
    circles[i] = new google.maps.Circle(circleOptions);
    polyLines[i] = new google.maps.Polyline(polyLineOptions);
  }
}

function resetMapMarker() {
  map.setCenter(latlng );
  map.setZoom(MAP_ZOOM);
  marker.setPosition(latlng);  
}

function resetZones() {
  for(var i=0;i<COUNT;i++) {
    circles[i].setRadius(0);
    polyLines[i].setPath([latlng]);
  }
}

function setMapByAddress() {
  var address = $("#address").attr("value");
  geocoder.geocode({
    'address': address
  }, function(results, status) {
    if (status == google.maps.GeocoderStatus.OK) {
      latlng = results[0].geometry.location;
      resetMapMarker();
    }
    else {
      showGeoError("#geocoding-error");
    }
  });
}

function setMapByLatLng() {
  var latitude = $("#latitude").attr("value");
  var longtitude = $("#longtitude").attr("value");
  latlng = new google.maps.LatLng(latitude, longtitude);
  resetMapMarker();
}

function setMapByGeoLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(geoLocationSuccess, geoLocationError);
  }
  else {
    showGeoError("#geo-support");
  } 
}

function geoLocationSuccess(loc) {
  if (loc.coords.accurace>ACCURACE) {
    geoLocationError();
  } else {
    latlng = new google.maps.LatLng(loc.coords.latitude, loc.coords.longitude);
    resetMapMarker();
  }
}

function geoLocationError() {
  showGeoError("#geo-error");
}

function showGeoError (selector) {
  $(GEO_MESSAGE_HOLDER_SELECTOR).html($(selector).html());
  $(GEO_MESSAGES_PANEL_SELECTOR).show("slider", callback);
}

function callback() {
  setTimeout(function() {
      $(GEO_MESSAGES_PANEL_SELECTOR).fadeOut();
    }, GEO_MESSAGES_PANEL_TIMEOUT);
}

function calculate() {
  var mass = $("#mass").attr("value");
  var dvs_id = $("#dvss option:selected").attr("value");
  var substance_id = $("#substances option:selected").attr("value");
  var wind = $("#winds option:selected").attr("value");
  var temperature = $("#temperatures option:selected").attr("value");
  
  // Dirty hack because of RU locale
  wind=wind.replace(",", ".");
  wind=parseFloat(wind);

  $.get("/contamination/" + dvs_id + "/" + substance_id + "/" + wind +
        "/" + temperature + "/" + mass + "/calculate/", function(data) {
    var result=JSON.parse(data);
    var radius = parseInt(result.radius);
    var speed=Number(result.speed);   
    resetZones();
    resetMapMarker();
    setZoom(radius);
    var azimuth = $("#slider").slider("value");
    var width;
    for(var i in WINDS) {
      if(wind<=WINDS[i].w) {
        width=WINDS[i].a;
        break;
      }
    }
    var drawer;
    for(var i in ANGLE_CALLBACKS) {
      if(width>=ANGLE_CALLBACKS[i].a) {
        drawer=ANGLE_CALLBACKS[i].c;
        break;
      }
    }  
    var radiuses=[Math.min(speed*TIMES[0]*MULTIPLIER, radius),
                  Math.min(speed*TIMES[1]*MULTIPLIER, radius),
                  radius];
    for(var i in STROKES) {
      circleOptions = {
        map: map,
        fillOpacity: OPACITY,
        strokeColor:STROKES[i].c,
        strokeWeight:STROKES[i].w
      };
      circles[i].setOptions(circleOptions);   
      polyLineOptions = {
        map: map,
        strokeColor:STROKES[i].c,
        strokeWeight:STROKES[i].w 
      };
      polyLines[i].setOptions(polyLineOptions);  
      drawer(radiuses[i], i, azimuth, width);
      $(RESULTS_SELECTORS[i]).html(radiuses[i]);
    }
    $(RESULT_PANEL_SELECTOR).show("slide");
  });
}

function setZoom(radius) {
  var zoom;
  for(var i in ZOOMS) {
    if(radius<=ZOOMS[i].r) {
      zoom=ZOOMS[i].z;
      break;
    }
  }
  map.setZoom(zoom);
}

function drawCircle(radius, i) {
  circles[i].setCenter(latlng);
  circles[i].setRadius(radius);
}

function drawSector(radius, i,azimuth,width) { 
  var centerPoint = latlng;
  var lat = latlng.lat();
  var lng = latlng.lng();

  var PRlat = (radius/EARTH_RADIUS) * R2D;
  var PRlng = PRlat/Math.cos(lat*D2R);

  var PGpoints = []; 
  PGpoints.push(centerPoint);
  with (Math) { 
    lat1 = lat + (PRlat * cos( D2R * (azimuth  - width/2 ))); 
    lon1 = lng + (PRlng * sin( D2R * (azimuth  - width/2 ))); 
    PGpoints.push( new google.maps.LatLng(lat1,lon1)); 
    lat2 = lat + (PRlat * cos( D2R * (azimuth  + width/2 ))); 
    lon2 = lng + (PRlng * sin( D2R * (azimuth  + width/2 ))); 
    var theta = 0; 
    var gamma = D2R * (azimuth  + width/2 ); 
    for (var a = 1; theta < gamma ; a++ ) { 
      theta = D2R * (azimuth  - width/2 +a); 
      PGlon = lng + (PRlng * sin( theta )); 
      PGlat = lat + (PRlat * cos( theta )); 
      PGpoints.push(new google.maps.LatLng(PGlat,PGlon)); 
    } 
    PGpoints.push(new google.maps.LatLng(lat2,lon2)); 
    PGpoints.push(centerPoint); 
  }
  polyLines[i].setPath(PGpoints);
}

function initializeControls() {
  $(RESULT_PANEL_SELECTOR).hide();
  var indexTab=0;
  if(sessionStorage) {
    indexTab=sessionStorage.getItem(TAB_STORED);
  }
  if (indexTab != "" && indexTab != null) {
    $(TABS_SELECTOR).tabs({ selected: indexTab });
  }
  else {
    $(TABS_SELECTOR).tabs();
  }
  $("#accordion1").accordion({autoHeight: false});
  $("#accordion2").accordion({autoHeight: false});
  $("#geo-messages-panel").hide();
  $("button").button();
  $("#slider").slider({ min: MIN_ANGLE, max: MAX_ANGLE });
  if (!navigator.geolocation) {
    showGeoError("#geo-support");
    $("#geo-button").addClass("invisible");
  }
  $("#address-button").on('click', setMapByAddress);
  $("#latlng-button").on('click', setMapByLatLng);
  $("#geo-button").on('click', setMapByGeoLocation);
  $("#calculate-button").on('click', calculate); 
  $("#resultsPanelClose").on('click', function () {
    $(RESULT_PANEL_SELECTOR).hide("fold");
  });
  $("#slider").on("slide", function(event, ui) {
    $("#arrow").rotate(ui.value);
    $("#azimuth").html(ui.value);
  });
}

function initializeDefaultCoordinates() {
  if(localStorage) {
    var lat = localStorage.getItem(LAT_STORED);
    var lng = localStorage.getItem(LNG_STORED);
    if(lat != "" && lng != "" && lat != null && lng != null) {
      DEFAULT_LAT = lat;
      DEFAULT_LNG = lng;
    }
  }
}

function initializeBindings() {
  viewModel={
    sub_sel:ko.observable("-1"),
    dvs_sel:ko.observable("-1"),
    w_sel:ko.observable("-1"),
    t_sel:ko.observable("-1"),
    mass:ko.observable("")
  };
}

function initialize() {
  initializeControls();
  initializeDefaultCoordinates();
  initializeMap();
  initializeBindings();
  ko.applyBindings(viewModel);
}

function storeCurrentCoordinates() {
  if(localStorage) {
    localStorage.setItem(LAT_STORED, latlng.lat());
    localStorage.setItem(LNG_STORED, latlng.lng());
  }
}

function storeSelectedTab() {
  if(sessionStorage) {
    var indexTab=$(TABS_SELECTOR).tabs("option", "selected");
    sessionStorage.setItem(TAB_STORED, indexTab);
  }
}

// main
$(document).ready(function() {
  initialize()
});

$(window).unload(function() {
  storeCurrentCoordinates();
  storeSelectedTab();
});