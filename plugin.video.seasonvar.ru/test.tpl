var url = encodeURI('$url$');

var page = require('webpage').create();

page.onInitialized = function () 
{
        page.evaluate(function () 
        {
            window.navigator = {
                plugins: {length: 2, 'Shockwave Flash': {name: 'Shockwave Flash', description: 'Shockwave Flash 11.6 r602'}},
                mimeTypes: {length: 2, "application/x-shockwave-flash":
                    {description: "Shockwave Flash", suffixes: "swf", type: "application/x-shockwave-flash", enabledPlugin: {description: "Shockwave Flash 11.6 r602"}}
                },
                appCodeName: "Mozilla",
                appName: "Netscape",
                appVersion: "5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 Safari/537.22",
                cookieEnabled: true,
                language: "en",
                onLine: true,
                platform: "CentOS 5.7",
                product: "Gecko",
                productSub: "20030107",
                userAgent: "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.22 (KHTML, like Gecko) Chrome/25.0.1364.172 Safari/537.22",
            };
        });
};

page.open(url, function(status) {
    var result;
    
    if (status !== 'success') 
    {
        console.log('Error: Unable to access network!');
    }  
    else 
    {
    	result = page.evaluate(function () 
        {
    	    return document.getElementById("videoplayer719").parentNode.innerHTML; 
        });

	console.log(result);
    }
    phantom.exit();
});