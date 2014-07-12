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