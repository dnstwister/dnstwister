// See dnstwist.py's validate_domain().
function validateUrlArg(url) {
  if (url.length > 255 || url.length === 0) {
    return false;
  }

  if (url[url.length - 1] === '.') {
    url = url.slice(0, -1);
  }

  var urlValidation = /^http:\/\/([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$/;
  return urlValidation.test(url);
}

try {
  phantom.onError = function() {};

  var page = require('webpage').create();
  page.onError = function () {};
  page.onResourceTimeout = function () {};
  page.XSSAuditingEnabled = true;
  page.loadImages = false;
  page.resourceTimeout = 100;
  page.viewportSize = { width: 800, height: 600 };
  page.clipRect = { top: 0, left: 0, width: 800, height: 600 };

  var system = require('system');
  var args = system.args;
  if (args.length !== 2) {
    phantom.exit(1);
  }

  var url = args[1];
  if (validateUrlArg(url) !== true) {
    phantom.exit(2);
  }

  page.open(url, function(status) {
    if (status === 'success') {
      console.log(page.renderBase64('png'));
      phantom.exit(0);
    }
    else {
      phantom.exit(3);
    }
  });
}
catch (err) {
  phantom.exit(4);
}
