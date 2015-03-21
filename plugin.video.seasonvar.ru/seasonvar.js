page = require('webpage').create();


page.onLoadFinished = function (status)
{
  if (status == 'success')
  {	
    console.log('Connection OK.');	
    phantom.exit();
  }
  else
  {
    console.log('Connection failed.');
    phantom.exit();
  };
};


page.open('http://www.seasonvar.ru/serial-3251-7_samuraev.html');
