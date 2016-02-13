
var BOOTSTRAP_MIN_SCREEN_WIDTH = {
  'xs': 256,
  'sm': 768,
  'md': 992,
  'lg': 1200,
};

var USA_MAP_SIZE_FOR_SCREEN_SIZE = {
  'xs': 320,
  'sm': 768,
  'md': 992,
  'lg': 1200,
};

function findBootstrapScreenSize() {
    var envs = ['xs', 'sm', 'md', 'lg'];

    var $el = $('<div>');
    $el.appendTo($('body'));

    for (var i = envs.length - 1; i >= 0; i--) {
        var env = envs[i];

        $el.addClass('hidden-'+env);
        if ($el.is(':hidden')) {
            $el.remove();
            return env;
        }
    }
};

function buildMap(element, width) {
  var height = 630/930 * width;
  element.width(width);
  element.height(height);
  element.empty();
  element.usmap({
    'showLabels': false,
    'stateStyles': {
      'fill': '#025',
      "stroke-width": 1,
      'stroke' : '#036'
    },
    'stateHoverStyles': {
      'stroke': '#34A853',
      'stroke-width': 4
    },
    'stateHoverAnimation': 100,
    'click' : function(event, data) {
      console.log("Clicked " + data.name);
    },
    'stateSpecificStyles': {
      'MD': {fill: getInterpolatedColor(Math.random())},
      'VA': {fill: getInterpolatedColor(Math.random())},
      "AL": {fill: getInterpolatedColor(Math.random())},
      "AK": {fill: getInterpolatedColor(Math.random())},
      "AS": {fill: getInterpolatedColor(Math.random())},
      "AZ": {fill: getInterpolatedColor(Math.random())},
      "AR": {fill: getInterpolatedColor(Math.random())},
      "CA": {fill: getInterpolatedColor(Math.random())},
      "CO": {fill: getInterpolatedColor(Math.random())},
      "CT": {fill: getInterpolatedColor(Math.random())},
      "DE": {fill: getInterpolatedColor(Math.random())},
      "DC": {fill: getInterpolatedColor(Math.random())},
      "FM": {fill: getInterpolatedColor(Math.random())},
      "FL": {fill: getInterpolatedColor(Math.random())},
      "GA": {fill: getInterpolatedColor(Math.random())},
      "GU": {fill: getInterpolatedColor(Math.random())},
      "HI": {fill: getInterpolatedColor(Math.random())},
      "ID": {fill: getInterpolatedColor(Math.random())},
      "IL": {fill: getInterpolatedColor(Math.random())},
      "IN": {fill: getInterpolatedColor(Math.random())},
      "IA": {fill: getInterpolatedColor(Math.random())},
      "KS": {fill: getInterpolatedColor(Math.random())},
      "KY": {fill: getInterpolatedColor(Math.random())},
      "LA": {fill: getInterpolatedColor(Math.random())},
      "ME": {fill: getInterpolatedColor(Math.random())},
      "MH": {fill: getInterpolatedColor(Math.random())},
      "MD": {fill: getInterpolatedColor(Math.random())},
      "MA": {fill: getInterpolatedColor(Math.random())},
      "MI": {fill: getInterpolatedColor(Math.random())},
      "MN": {fill: getInterpolatedColor(Math.random())},
      "MS": {fill: getInterpolatedColor(Math.random())},
      "MO": {fill: getInterpolatedColor(Math.random())},
      "MT": {fill: getInterpolatedColor(Math.random())},
      "NE": {fill: getInterpolatedColor(Math.random())},
      "NV": {fill: getInterpolatedColor(Math.random())},
      "NH": {fill: getInterpolatedColor(Math.random())},
      "NJ": {fill: getInterpolatedColor(Math.random())},
      "NM": {fill: getInterpolatedColor(Math.random())},
      "NY": {fill: getInterpolatedColor(Math.random())},
      "NC": {fill: getInterpolatedColor(Math.random())},
      "ND": {fill: getInterpolatedColor(Math.random())},
      "MP": {fill: getInterpolatedColor(Math.random())},
      "OH": {fill: getInterpolatedColor(Math.random())},
      "OK": {fill: getInterpolatedColor(Math.random())},
      "OR": {fill: getInterpolatedColor(Math.random())},
      "PW": {fill: getInterpolatedColor(Math.random())},
      "PA": {fill: getInterpolatedColor(Math.random())},
      "PR": {fill: getInterpolatedColor(Math.random())},
      "RI": {fill: getInterpolatedColor(Math.random())},
      "SC": {fill: getInterpolatedColor(Math.random())},
      "SD": {fill: getInterpolatedColor(Math.random())},
      "TN": {fill: getInterpolatedColor(Math.random())},
      "TX": {fill: getInterpolatedColor(Math.random())},
      "UT": {fill: getInterpolatedColor(Math.random())},
      "VT": {fill: getInterpolatedColor(Math.random())},
      "VI": {fill: getInterpolatedColor(Math.random())},
      "VA": {fill: getInterpolatedColor(Math.random())},
      "WA": {fill: getInterpolatedColor(Math.random())},
      "WV": {fill: getInterpolatedColor(Math.random())},
      "WI": {fill: getInterpolatedColor(Math.random())},
      "WY": {fill: getInterpolatedColor(Math.random())}
    }
  });
};

// Returns a color in [RepublicanRed, DemocratBlue]
function getInterpolatedColor(t) {
  var republicanRed = hexToRgb("BF0A30");
  var democratBlue = hexToRgb("002868");
  var r = Math.floor(republicanRed.r + t * (democratBlue.r - republicanRed.r));
  var g = Math.floor(republicanRed.g + t * (democratBlue.g - republicanRed.g));
  var b = Math.floor(republicanRed.b + t * (democratBlue.b - republicanRed.b));
  return rgbToHex(r, g, b);
};

function hexToRgb(hex) {
  var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : null;
};

function rgbToHex(r, g, b) {
  return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
};
