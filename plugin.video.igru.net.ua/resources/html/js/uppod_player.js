//	Uppod.AJAX 1.1 for Uppod.Player (http://uppod.ru/player/ajax/)  
//	use 1pixelout plugin
//	!!!test only on server!!!

	var uppod_instances = new Array();
	var uppod_instances_id = new Array();

	// SETTINGS
	var uppod_play_next=0; // set 1 for autoplay next player
	
	//*******************************************
	// EVENTS
	//*******************************************
	
	//start
	function uppodStartsReport(playerID) {
		//alert(playerID);
	}
	//file not found
	function uppodErrorReport(playerID) {
		//alert(playerID);
	}
	//end of play (uppod_play_next=1 - play next player)
	function uppodTheEnd(playerID) {
		if(uppod_play_next==1){
			if(uppod_instances_id[playerID]<uppod_instances.length-1){
				document.getElementById(uppod_instances[uppod_instances_id[playerID]+1]).sendToUppod('play');
			}
			else{
				document.getElementById(uppod_instances[0]).sendToUppod('play');
			}
		}
	}
	//file onEnd (set in style > Plugins > Uppod.AJAX) 0.51
	function uppodOnEnd(playerID) {
		//alert(playerID);
	}
	//file onLoad (set in style > Plugins > Uppod.AJAX) 0.5
	function uppodOnLoad(playerID) {
		//alert(playerID);
	}
	//file OnDownload (set in style > Plugins > Uppod.AJAX) 0.5
	function uppodOnDownload(playerID) {
		//alert(playerID);
	}
	//file OnQuality (set in style > Plugins > Uppod.AJAX) 0.8
	function uppodOnQuality(playerID) {
		//alert(playerID);
	}
	//file OnSeek (set in style > Plugins > Uppod.AJAX) 0.8
	function uppodOnSeek(playerID) {
		//alert(playerID);
	}
	//*******************************************
	// COMMAND - stop all players except one (playerID)
	//*******************************************
	function uppodStopAll(playerID) { 
		for(var i = 0;i<uppod_instances.length;i++) {
			try {
				if(uppod_instances[i] != playerID){
					document.getElementById(uppod_instances[i]).sendToUppod("stop");
				}
			}
			catch( errorObject ) {
			}
		}
	}
	
	// Send
	function uppodSend(playerID,com,callback) {
		document.getElementById(playerID).sendToUppod(com,(callback?callback:''));
	}
	// Return
	function uppodGet(playerID,com,callback) {
		return document.getElementById(playerID).getUppod(com,(callback?callback:''));
	}
	
	//*******************************************
	// RETURN OLD
	//*******************************************
	function uppodGetNpl(n,playerID) {}
	function uppodGetVolume(n,playerID) {}
	function uppodGetTime(n,playerID) {}
	function uppodGetTimeDuration(n,playerID) {}
	function uppodGetStatus(n,playerID) {}
	function uppodGetBytesTotal(n,playerID) {}
	function uppodGetBytesLoaded(n,playerID) {}
	function uppodGetProcent(n,playerID) {}
	function uppodGetFullScreen(n,playerID) {}
	function testCallback(n) {}
	
	//*******************************************
	// Uppod
	//*******************************************
	/////////////////////////////////////////////
	// 	find players on the page
	function uppodPlayers() { 
		var objectID;
		var objectTags = document.getElementsByTagName("object");
		for(var i=0;i<objectTags.length;i++) {
			objectID = objectTags[i].id;
			if(objectID.indexOf("player") >-1&uppod_instances.indexOf(objectID)==-1) {
				uppod_instances[i] = objectID;
				uppod_instances_id[objectID]=i;
			}
		}
	}
	// called after loading player
	function uppodInit(playerID) {
		//alert(playerID);
		uppodPreloader(playerID); // preloaders on
	}
	// called after loading playlist
	function uppodPL(playerID){
		
	}
	// player done (hide preloader)
	function uppodPreloader(playerID) {
		document.getElementById(playerID+"Preloader")?document.getElementById(playerID+"Preloader").style.display="none":'';
		document.getElementById(playerID+"Box")?document.getElementById(playerID+"Box").style.position="static":'';
	}
	// create Array.indexOf for old IE
	if(!Array.indexOf){ 
		Array.prototype.indexOf = function(obj){
		for(var i=0; i<this.length; i++){
			if(this[i]==obj){
				return i;
				}
			}
			return -1;
			}
	}
	var ap_uppodID = setInterval(uppodPlayers, 1000);