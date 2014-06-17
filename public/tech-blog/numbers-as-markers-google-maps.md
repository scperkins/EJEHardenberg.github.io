I was making a heatmap for a client today, and thought to myself. Boy 
wouldn't it be great to have the 'total heat' of an area show up on top
of the map.

Turns out, it's easy to put down a marker, and only slightly harder to 
get a number down instead. The key here is that you have to use an 
overlay and then have the map position everything for you via projection.

So how do you do it? 

	function NumberMarker(latlng,  map, value) {
		this.latlng_ = latlng;
			this.value = value;
			/*Do this or nothing will happen:*/
			this.setMap(map);
		}
	
	NumberMarker.prototype = new google.maps.OverlayView();
	NumberMarker.prototype.draw = function() {
		var me = this;
		var div = this.div_;
		if (!div) {
			// Create a overlay text DIV
			div = this.div_ = document.createElement('DIV');
			// Create the DIV representing our NumberMarker
			div.style.border = "none";
			div.style.position = "absolute";
			div.style.paddingLeft = "0px";
			div.style.cursor = 'pointer';

			var span = document.createElement("span");
			span.className = "markerOverlay";
			span.appendChild(document.createTextNode(this.value));
			div.appendChild(span);
			google.maps.event.addDomListener(div, "click", function(event) {
			google.maps.event.trigger(me, "click");
		});

		// Then add the overlay to the DOM
		var panes = this.getPanes();
			panes.overlayImage.appendChild(div);
		}

	    // Position the overlay 
	    var point = this.getProjection().fromLatLngToDivPixel(this.latlng_);
	    if (point) {
	      div.style.left = point.x + 'px';
	      div.style.top = point.y + 'px';
	    }
	};

	NumberMarker.prototype.remove = function() {
		// Check if the overlay was on the map and needs to be removed.
		if (this.div_) {	
			this.div_.parentNode.removeChild(this.div_);
			this.div_ = null;
		}
	};

	NumberMarker.prototype.getPosition = function() {
		return this.latlng_;
	};

	var myLatlng = new google.maps.LatLng(75,45);
    // define map properties
    var myOptions = {
      zoom: 5,
      center: myLatlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP,
      disableDefaultUI: false,
      scrollwheel: true,
      draggable: true,
      navigationControl: true,
      mapTypeControl: false,
      scaleControl: true,
      disableDoubleClickZoom: false
    };
	// we'll use the heatmapArea 
	var map = new google.maps.Map($('#maparea'')[0], myOptions);
	
	var overlay;
	overlay = new NumberMarker(myLatlng, map, 'whatever text or numbers you want here');


Bam. There you go. In my application I loop through a bunch of 
information and create a number of these markers on the map. I also use
[heatmap.js] to create my heat maps at the same time. Overall, it works 
pretty well. 

If you need any type of information positioned on a map, then just change the 
span tag to be whatever you need it to be and create it appropriately. 

[heatmap.js]:http://www.patrick-wied.at/static/heatmapjs/