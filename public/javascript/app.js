jQuery.fn.fadeOut = function (duration, callback) {
    jQuery(this).stop().fadeTo(duration, 0, function () {
        jQuery(this).css('display', 'none');
        if (typeof callback == 'function') {
            callback();
        }
    });
};
jQuery.fn.fadeIn = function (duration, callback) {
    jQuery(this).css('display', 'inline-block').stop().fadeTo(duration, 1, function () {
        if (typeof callback == 'function') {
            callback();
        }
    });
};
jQuery( document ).ready(function( $ ) {
	if( $('input[name="search"]').length > 0 ){
		$('input[name="search"]').on('keyup', function(evt){

			var search = $(this).val().toUpperCase()

			$('article').contents().filter(function() {
				if( this.innerHTML ){
					if(this.innerHTML.toUpperCase().indexOf(search) >= 0){
						return false;
					}
				}
      			return true
    		}).closest('article').fadeOut()

    		$('article').contents().filter(function() {
				if( this.innerHTML ){
					if(this.innerHTML.toUpperCase().indexOf(search) >= 0){
						return true;
					}
				}
      			return false
    		}).closest('article').fadeIn()

			if($(this).val().length <= 0){
				$('article').fadeIn()		
			}

			evt.stopPropagation()
		})

		$('input[name="search"]').on('blur', function(evt){
			if($(this).val().length <= 0){
				$('article').fadeIn()		
			}
		})
	}
})