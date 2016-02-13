
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
      fill: '#025',
      "stroke-width": 1,
      'stroke' : '#036'
    },
    'stateHoverStyles': {
      fill: '#900000'
    },
    'click' : function(event, data) {
    }
  });
};
