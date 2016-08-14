var page = require('webpage').create(), system = require('system'), address, output;
//viewportSize being the actual size of the headless browser
page.viewportSize = { width: 1024, height: 768 };
//the clipRect is the portion of the page you are taking a screenshot of
page.clipRect = { top: 192, left: 256, width: 512, height: 384 };
//the rest of the code is the same as the previous example
address = system.args[1];
output = system.args[2];
page.settings.resourceTimeout = 10000; // Avoid freeze!!!
page.open(address, function() {
window.setTimeout(function () {
                page.render(output);
                phantom.exit();
            }, 2000);
});
